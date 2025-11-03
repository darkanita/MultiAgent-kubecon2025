// ===================================================================================================
// ACR ROLE ASSIGNMENT MODULE
// ===================================================================================================

@description('The object ID of the AKS kubelet identity')
param aksKubeletIdentityObjectId string

@description('The name of the ACR')
param acrName string

// Reference the ACR
resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

// Grant AcrPull role
resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, aksKubeletIdentityObjectId, 'AcrPull')
  scope: acr
  properties: {
    principalId: aksKubeletIdentityObjectId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalType: 'ServicePrincipal'
  }
}
