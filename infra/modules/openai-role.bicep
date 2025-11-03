// ===================================================================================================
// OPENAI ROLE ASSIGNMENT MODULE
// ===================================================================================================

@description('The object ID of the AKS kubelet identity')
param aksKubeletIdentityObjectId string

@description('The name of the OpenAI account')
param openAiName string

// Reference the OpenAI account
resource openAi 'Microsoft.CognitiveServices/accounts@2023-05-01' existing = {
  name: openAiName
}

// Grant Cognitive Services OpenAI User role
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(openAi.id, aksKubeletIdentityObjectId, 'CognitiveServicesOpenAIUser')
  scope: openAi
  properties: {
    principalId: aksKubeletIdentityObjectId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd') // Cognitive Services OpenAI User
    principalType: 'ServicePrincipal'
  }
}
