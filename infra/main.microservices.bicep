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
// EXISTING RESOURCES (IF SHARED)
// =================================================================================================

// Reference existing ACR if shared
resource existingAcr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = if (useSharedAcr) {
  name: sharedAcrName
  scope: resourceGroup()
}

// Reference existing OpenAI if shared
resource existingOpenAi 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = if (useSharedOpenAi) {
  name: !empty(sharedOpenAiId) ? last(split(sharedOpenAiId, '/')) : 'dummy'
  scope: resourceGroup(!empty(sharedOpenAiId) ? split(sharedOpenAiId, '/')[4] : resourceGroup().name)
}

// =================================================================================================
// MICROSERVICES INFRASTRUCTURE MODULE
// =================================================================================================

module microservicesInfra './modules/microservices-aks.bicep' = {
  name: 'microservices-infrastructure'
  params: {
    environmentName: environmentName
    location: location
    resourceToken: resourceToken
    tags: tags
    useSharedAcr: useSharedAcr
    sharedAcrName: useSharedAcr ? sharedAcrName : ''
    useSharedOpenAi: useSharedOpenAi
    sharedOpenAiEndpoint: useSharedOpenAi ? existingOpenAi.properties.endpoint : ''
  }
}

// =================================================================================================
// RBAC - GRANT AKS ACCESS TO RESOURCES
// =================================================================================================

// Grant AKS access to ACR (either shared or new)
var acrResourceId = useSharedAcr ? existingAcr.id : microservicesInfra.outputs.containerRegistryId
resource aksAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(microservicesInfra.outputs.aksClusterId, acrResourceId, 'AcrPull')
  scope: useSharedAcr ? existingAcr : resourceGroup()
  properties: {
    principalId: microservicesInfra.outputs.aksKubeletIdentityObjectId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalType: 'ServicePrincipal'
  }
}

// Grant AKS access to OpenAI (either shared or new)
var openAiResourceId = useSharedOpenAi ? existingOpenAi.id : microservicesInfra.outputs.openAiId
resource aksOpenAiUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(microservicesInfra.outputs.aksClusterId, openAiResourceId, 'CognitiveServicesOpenAIUser')
  scope: useSharedOpenAi ? existingOpenAi : resourceGroup()
  properties: {
    principalId: microservicesInfra.outputs.aksKubeletIdentityObjectId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd') // Cognitive Services OpenAI User
    principalType: 'ServicePrincipal'
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
output AZURE_CONTAINER_REGISTRY_NAME string = useSharedAcr ? existingAcr.name : microservicesInfra.outputs.containerRegistryName

@description('The login server of the container registry')
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = useSharedAcr ? existingAcr.properties.loginServer : microservicesInfra.outputs.containerRegistryEndpoint

// AI Services
@description('The endpoint for the Azure OpenAI service')
output AZURE_OPENAI_ENDPOINT string = useSharedOpenAi ? existingOpenAi.properties.endpoint : microservicesInfra.outputs.openAiEndpoint

@description('The name of the Azure OpenAI deployment')
output AZURE_OPENAI_DEPLOYMENT_NAME string = 'gpt-4o-mini'

@description('The resource ID of Azure OpenAI')
output AZURE_OPENAI_ID string = useSharedOpenAi ? existingOpenAi.id : microservicesInfra.outputs.openAiId

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
