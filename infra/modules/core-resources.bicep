// ===================================================================================================
// CORE RESOURCES MODULE - RESOURCE GROUP SCOPE
// ===================================================================================================

@description('Environment name for resource naming')
param environmentName string

@description('Primary location for all resources')
param location string

@description('Resource token for unique naming')
param resourceToken string

@description('Tags to apply to all resources')
param tags object

// =================================================================================================
// 1. VIRTUAL NETWORK - BASIC
// =================================================================================================

resource vnet 'Microsoft.Network/virtualNetworks@2023-06-01' = {
  name: 'vnet-${resourceToken}'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: ['10.0.0.0/16']
    }
    subnets: [
      {
        name: 'aks-subnet'
        properties: {
          addressPrefix: '10.0.0.0/20'
        }
      }
    ]
  }
}

// =================================================================================================
// 2. LOG ANALYTICS WORKSPACE - FOR MONITORING
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
// 3. CONTAINER REGISTRY - BASIC
// =================================================================================================

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'acrma${environmentName}${take(replace(resourceToken, '-', ''), 8)}'
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

// Grant ACR Pull permission to AKS identity
resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, aks.id, 'acrpull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: aks.properties.identityProfile.kubeletidentity.objectId
    principalType: 'ServicePrincipal'
  }
}

// =================================================================================================
// 4. AKS CLUSTER - MINIMAL CONFIGURATION
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
        count: 1
        vmSize: 'Standard_B2s'
        mode: 'System'
        osType: 'Linux'
      }
    ]
    networkProfile: {
      networkPlugin: 'kubenet'
      loadBalancerSku: 'standard'
    }
  }
}

// =================================================================================================
// 6. AZURE OPENAI - BASIC
// =================================================================================================

resource openai 'Microsoft.CognitiveServices/accounts@2024-04-01-preview' = {
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

resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-04-01-preview' = {
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

output aksClusterName string = aks.name
output aksClusterFqdn string = aks.properties.fqdn
output containerRegistryName string = acr.name
output containerRegistryEndpoint string = acr.properties.loginServer
output openaiEndpoint string = openai.properties.endpoint
output logAnalyticsWorkspaceId string = logAnalytics.id
