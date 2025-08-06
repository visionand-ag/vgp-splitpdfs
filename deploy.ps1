$RESOURCE_GROUP = "prod-01-appl-splitpdfs"
$ACR_NAME = "vgpsplitpdfsacr"
$FUNCTION_APP_NAME = "splitpdfs-fapp-cont"
$STORAGE_ACCOUNT = "splitpdfsa"
$APP_SERVICE_PLAN = "splitpdfs-asp"
$LOCATION = "switzerlandnorth"

# Login to Azure
az login

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# Build and push image
az acr login --name $ACR_NAME
az acr build --registry $ACR_NAME --image pdf-splitting-function:latest --file Dockerfile .

# Create storage account
az storage account create --name $STORAGE_ACCOUNT --location $LOCATION --resource-group $RESOURCE_GROUP --sku Standard_LRS

# Create Blob containers
az storage container create --name pdfs --account-name $STORAGE_ACCOUNT
az storage container create --name processed-pdfs --account-name $STORAGE_ACCOUNT

# Create App Service Plan
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku P1V2 --is-linux

# Get ACR details
$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --query loginServer --output tsv
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username --output tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv

# Create Function App
az functionapp create `
    -g $RESOURCE_GROUP `
    --plan $APP_SERVICE_PLAN `
    --name $FUNCTION_APP_NAME `
    --storage-account $STORAGE_ACCOUNT `
    --image "$ACR_LOGIN_SERVER/pdf-splitting-function:latest" `
    --registry-username $ACR_USERNAME `
    --registry-password $ACR_PASSWORD `
    --functions-version 4

# Enable system-managed identity
az functionapp identity assign --name $FUNCTION_APP_NAME --resource-group $RESOURCE_GROUP

Write-Host "Deployment complete! Function App: $FUNCTION_APP_NAME"