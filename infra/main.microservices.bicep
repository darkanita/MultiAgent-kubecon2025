// ===================================================================================================
// MICROSERVICES INFRASTRUCTURE - AZD COMPATIBLE (PHASE 2)
// ===================================================================================================

targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string = resourceGroup().location

@description('Optional: Use existing ACR from Phase 1 (leave empty to create new)')
param sharedAcrName string = ''

@description('Optional: Use existing OpenAI from Phase 1 (leave empty to create new)')
param sharedOpenAiId string = ''

@description('Optional: Shared OpenAI endpoint if using existing')
param sharedOpenAiEndpoint string = ''

// =================================================================================================
// VARIABLES
// =================================================================================================

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = {
  'azd-env-name': environmentName
  project: 'multiagent-kubecon'
  purpose: 'microservices'
  phase: '2'
}

// Use shared or create new
var useSharedAcr = !empty(sharedAcrName)
var useSharedOpenAi = !empty(sharedOpenAiId)

// =================================================================================================
// MICROSERVICES INFRASTRUCTURE MODULE
// =================================================================================================

module microservicesInfra './modules/microservices-aks.bicep' = {
  name: 'microservices-infrastructure'
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
    useSharedAcr: useSharedAcr
    sharedAcrName: useSharedAcr ? sharedAcrName : ''
    useSharedOpenAi: useSharedOpenAi
    sharedOpenAiEndpoint: ''  // Will be set via azd env
  }
}

// =================================================================================================
// RBAC - GRANT AKS ACCESS TO RESOURCES
// =================================================================================================

// Grant AKS access to new ACR (if created)
module acrRoleAssignment './modules/acr-role.bicep' = if (!useSharedAcr) {
  name: 'acr-role-assignment'
  params: {
    aksKubeletIdentityObjectId: microservicesInfra.outputs.aksKubeletIdentityObjectId
    acrName: microservicesInfra.outputs.containerRegistryName
  }
}

// Grant AKS access to shared ACR (if using existing)
module sharedAcrRoleAssignment './modules/acr-role.bicep' = if (useSharedAcr) {
  name: 'shared-acr-role-assignment'
  params: {
    aksKubeletIdentityObjectId: microservicesInfra.outputs.aksKubeletIdentityObjectId
    acrName: sharedAcrName
  }
}

// Grant AKS access to new OpenAI (if created)
module openAiRoleAssignment './modules/openai-role.bicep' = if (!useSharedOpenAi) {
  name: 'openai-role-assignment'
  params: {
    aksKubeletIdentityObjectId: microservicesInfra.outputs.aksKubeletIdentityObjectId
    openAiName: split(microservicesInfra.outputs.openAiId, '/')[8]
  }
}

// Grant AKS access to shared OpenAI (if using existing)
module sharedOpenAiRoleAssignment './modules/openai-role.bicep' = if (useSharedOpenAi) {
  name: 'shared-openai-role-assignment'
  scope: resourceGroup(split(sharedOpenAiId, '/')[2], split(sharedOpenAiId, '/')[4])
  params: {
    aksKubeletIdentityObjectId: microservicesInfra.outputs.aksKubeletIdentityObjectId
    openAiName: last(split(sharedOpenAiId, '/'))
  }
}

// =================================================================================================
// OUTPUTS - AZD COMPATIBLE
// =================================================================================================

// Required by AZD
@description('The location the resources were deployed to')
output AZURE_LOCATION string = location

@description('The name of the resource group')
output AZURE_RESOURCE_GROUP string = resourceGroup().name

// AKS Cluster
@description('The name of the AKS cluster')
output AZURE_AKS_CLUSTER_NAME string = microservicesInfra.outputs.aksClusterName

@description('The FQDN of the AKS cluster')
output AZURE_AKS_CLUSTER_FQDN string = microservicesInfra.outputs.aksClusterFqdn

@description('The resource ID of the AKS cluster')
output AZURE_AKS_CLUSTER_ID string = microservicesInfra.outputs.aksClusterId

// Container Registry
@description('The name of the container registry')
output AZURE_CONTAINER_REGISTRY_NAME string = useSharedAcr ? sharedAcrName : microservicesInfra.outputs.containerRegistryName

@description('The login server of the container registry')
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = useSharedAcr ? '${sharedAcrName}.azurecr.io' : microservicesInfra.outputs.containerRegistryEndpoint

// AI Services
@description('The endpoint for the Azure OpenAI service')
output AZURE_OPENAI_ENDPOINT string = useSharedOpenAi ? sharedOpenAiEndpoint : microservicesInfra.outputs.openAiEndpoint

@description('The name of the Azure OpenAI deployment')
output AZURE_OPENAI_DEPLOYMENT_NAME string = 'gpt-4o-mini'

@description('The resource ID of Azure OpenAI')
output AZURE_OPENAI_ID string = useSharedOpenAi ? sharedOpenAiId : microservicesInfra.outputs.openAiId

// Monitoring
@description('The Log Analytics workspace ID')
output AZURE_LOG_ANALYTICS_WORKSPACE_ID string = microservicesInfra.outputs.logAnalyticsWorkspaceId

@description('The Application Insights connection string')
output APPLICATIONINSIGHTS_CONNECTION_STRING string = microservicesInfra.outputs.appInsightsConnectionString

// Additional useful outputs
@description('The resource token for naming')
output RESOURCE_TOKEN string = resourceToken

@description('Whether using shared ACR')
output USING_SHARED_ACR bool = useSharedAcr

@description('Whether using shared OpenAI')
output USING_SHARED_OPENAI bool = useSharedOpenAi

// Service URLs for MCP configuration
@description('Currency agent internal URL')
output CURRENCY_AGENT_URL string = 'http://currency-agent:8001'

@description('Activity agent internal URL')
output ACTIVITY_AGENT_URL string = 'http://activity-agent:8002'
