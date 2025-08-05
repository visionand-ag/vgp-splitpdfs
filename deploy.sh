#!/bin/bash

RESOURCE_GROUP="prod-01-appl-splitpdfs"
ACR_NAME="vgpsplitpdfsacr"
FUNCTION_APP_NAME="splitpdfs-fapp-cont"
STORAGE_ACCOUNT="splitpdfsa"
APP_SERVICE_PLAN="splitpdfs-asp"
LOCATION="switzerlandnorth"
CLIENT_NAME="splitpdfs-client"

# Login to Azure
az login

# Create resource group
az group create --name $RESOURCE_GROUP --location "$LOCATION"

# Assign contributor role to the current user logged in with az
az role assignment create --assignee $(az ad signed-in-user show --query userPrincipalName --output tsv) --role Contributor --scope /subscriptions/$(az account show --query id --output tsv)/resourceGroups/$RESOURCE_GROUP

# Create Azure AD application for the SharePoint Authentication
az ad app create --display-name "$CLIENT_NAME"
AD_APP_PRINCIPAL_ID=$(az ad app list --display-name $CLIENT_NAME --query "[0].appId" --output tsv)

# Assign AD application the Storage Blob Data Contributor role
az role assignment create --assignee $AD_APP_PRINCIPAL_ID --role "Storage Blob Data Contributor" --scope "/subscriptions/$(az account show --query id --output tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT"

# Create ACR
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Build and push image
az acr login --name $ACR_NAME
az acr build --registry $ACR_NAME --image pdf-splitting-function:latest --file Dockerfile .

# Create storage account
az storage account create --name $STORAGE_ACCOUNT --location "$LOCATION" --resource-group $RESOURCE_GROUP --sku Standard_LRS

# Create Blob container
az storage container create --name pdfs --account-name $STORAGE_ACCOUNT
az storage container create --name processed-pdfs --account-name $STORAGE_ACCOUNT

# Create App Service Plan
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku P1V2 --is-linux

# Get ACR details
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

# Create Function App
az functionapp create \
    -g $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $FUNCTION_APP_NAME \
    --storage-account $STORAGE_ACCOUNT \
    --image $ACR_LOGIN_SERVER/pdf-splitting-function:latest \
    --registry-username $ACR_USERNAME \
    --registry-password $ACR_PASSWORD \
    --functions-version 4

# Assign System Assigned Managed Identity to Function App
az functionapp identity assign --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

# Assign Storage Blob Data Contributor role to the Function App's Managed Identity
FUNCTION_APP_PRINCIPAL_ID=$(az functionapp identity show --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP --query principalId --output tsv)
az role assignment create --assignee $FUNCTION_APP_PRINCIPAL_ID --role "Storage Blob Data Contributor" --scope /subscriptions/$(az account show --query id --output tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT

echo "Deployment complete! Function App: $FUNCTION_APP_NAME"