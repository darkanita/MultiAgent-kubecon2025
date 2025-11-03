// ===================================================================================================
// MICROSERVICES AKS MODULE - RESOURCE GROUP SCOPE (PHASE 2)
// ===================================================================================================

@description('Environment name for resource naming')
param environmentName string

@description('Primary location for all resources')
param location string

@description('Resource token for unique naming')
param resourceToken string

@description('Tags to apply to all resources')
param tags object

@description('Whether to use shared ACR')
param useSharedAcr bool = false

@description('Shared ACR name if using existing')
param sharedAcrName string = ''

@description('Whether to use shared OpenAI')
param useSharedOpenAi bool = false

@description('Shared OpenAI endpoint if using existing')
param sharedOpenAiEndpoint string = ''

// =================================================================================================
// 1. LOG ANALYTICS WORKSPACE - FOR MONITORING
// =================================================================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// =================================================================================================
// 2. APPLICATION INSIGHTS - FOR MONITORING
// =================================================================================================

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${resourceToken}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// =================================================================================================
// 3. CONTAINER REGISTRY - ONLY IF NOT SHARED
// =================================================================================================

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = if (!useSharedAcr) {
  name: 'acrma${take(replace(resourceToken, '-', ''), 12)}'
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

// =================================================================================================
// 4. AKS CLUSTER - MICROSERVICES CONFIGURATION
// =================================================================================================

resource aks 'Microsoft.ContainerService/managedClusters@2024-01-01' = {
  name: 'aks-${resourceToken}'
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    dnsPrefix: 'aks-${resourceToken}'
    enableRBAC: true
    agentPoolProfiles: [
      {
        name: 'agentpool'
        count: 1  // Start with 1, can scale up
        vmSize: 'Standard_B2s'
        mode: 'System'
        osType: 'Linux'
        enableAutoScaling: true
        minCount: 1
        maxCount: 3
      }
    ]
    networkProfile: {
      networkPlugin: 'azure'
      networkPolicy: 'azure'
      loadBalancerSku: 'standard'
      serviceCidr: '10.1.0.0/16'
      dnsServiceIP: '10.1.0.10'
    }
    addonProfiles: {
      omsagent: {
        enabled: true
        config: {
          logAnalyticsWorkspaceResourceID: logAnalytics.id
        }
      }
    }
  }
}

// =================================================================================================
// 5. AZURE OPENAI - ONLY IF NOT SHARED
// =================================================================================================

resource openai 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = if (!useSharedOpenAi) {
  name: 'oai-${resourceToken}'
  location: 'eastus'  // OpenAI is only available in specific regions
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: 'oai-${resourceToken}'
    publicNetworkAccess: 'Enabled'
  }
}

resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = if (!useSharedOpenAi) {
  parent: openai
  name: 'gpt-4o-mini'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o-mini'
      version: '2024-07-18'
    }
    raiPolicyName: 'Microsoft.Default'
  }
  sku: {
    name: 'GlobalStandard'
    capacity: 50
  }
}

// =================================================================================================
// OUTPUTS
// =================================================================================================

// AKS outputs
output aksClusterName string = aks.name
output aksClusterFqdn string = aks.properties.fqdn
output aksClusterId string = aks.id
output aksKubeletIdentityObjectId string = aks.properties.identityProfile.kubeletidentity.objectId

// ACR outputs
output containerRegistryId string = !useSharedAcr ? acr.id : ''
output containerRegistryName string = !useSharedAcr ? acr.name : sharedAcrName
output containerRegistryEndpoint string = !useSharedAcr ? acr!.properties.loginServer : '${sharedAcrName}.azurecr.io'

// OpenAI outputs
output openAiId string = !useSharedOpenAi ? openai.id : ''
output openAiEndpoint string = !useSharedOpenAi ? openai!.properties.endpoint : sharedOpenAiEndpoint

// Monitoring outputs
output logAnalyticsWorkspaceId string = logAnalytics.id
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
