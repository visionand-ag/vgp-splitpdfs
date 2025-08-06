#!/bin/bash

RESOURCE_GROUP=""
FUNCTION_APP_NAME=""

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