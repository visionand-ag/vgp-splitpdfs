#!/bin/bash

RESOURCE_GROUP="prod-01-appl-splitpdfs"
FUNCTION_APP_NAME="splitpdfs-fapp-cont"

# Login to Azure
az login

#  Configure App Settings from JSON config file
az functionapp config appsettings set --name $FUNCTION_APP_NAME -g $RESOURCE_GROUP --settings @settings.json

# Restart the function app to apply changes
az functionapp restart \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP

# Check deployment status
az functionapp show \
    --name $FUNCTION_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query state