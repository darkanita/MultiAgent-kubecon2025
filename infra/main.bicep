// ===================================================================================================
// MAIN TEMPLATE - AZD COMPATIBLE
// ===================================================================================================

targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string = resourceGroup().location

// =================================================================================================
// VARIABLES
// =================================================================================================

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = {
  'azd-env-name': environmentName
  project: 'multiagent-kubecon'
  purpose: 'azd-simple'
}

// =================================================================================================
// CORE INFRASTRUCTURE MODULE
// =================================================================================================

module coreInfra './modules/core-resources.bicep' = {
  name: 'core-infrastructure'
  params: {
    environmentName: environmentName
    location: location
    resourceToken: resourceToken
    tags: tags
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
output AZURE_AKS_CLUSTER_NAME string = coreInfra.outputs.aksClusterName

@description('The FQDN of the AKS cluster')
output AZURE_AKS_CLUSTER_FQDN string = coreInfra.outputs.aksClusterFqdn

// Container Registry  
@description('The name of the container registry')
output AZURE_CONTAINER_REGISTRY_NAME string = coreInfra.outputs.containerRegistryName

@description('The login server of the container registry')
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = coreInfra.outputs.containerRegistryEndpoint

// AI Services
@description('The endpoint for the Azure OpenAI service')
output AZURE_OPENAI_ENDPOINT string = coreInfra.outputs.openaiEndpoint

@description('The name of the Azure OpenAI deployment')
output AZURE_OPENAI_DEPLOYMENT_NAME string = 'gpt-4o-mini'

// Data Services
@description('The Cosmos DB endpoint')
output AZURE_COSMOS_ENDPOINT string = coreInfra.outputs.cosmosEndpoint

@description('The Cosmos DB database name')
output AZURE_COSMOS_DATABASE_NAME string = 'AgentDB'

// Monitoring
@description('The Log Analytics workspace ID')
output AZURE_LOG_ANALYTICS_WORKSPACE_ID string = coreInfra.outputs.logAnalyticsWorkspaceId

// Additional useful outputs
@description('The resource token for naming')
output RESOURCE_TOKEN string = resourceToken
