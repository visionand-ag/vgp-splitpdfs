# Power Platform Process (Flow) App

A Power Platform solution consisting of multiple cloud flows and a canvas app. The app enables users to define their own processes, each with customizable triggers and actions. It integrates with a PDF-splitting function so that when physical documents are scanned, the resulting PDFs are automatically split—and each split PDF initiates a separate process.

## ✅ Deployment Checklist

Before running the deployment scripts, ensure you have:

- [ ] Libraries created and templates uploaded
- [ ] Permissions for libaries set
- [ ] Service Account created
- [ ] Shared Mailbox Created and permissions set
- [ ] Permissions for service Principal (split-pdf) given on SharePoint site
- [ ] Creator Kit installed (Environment feature to allow custom pcf components enabled)
- [ ] Solution successfully deployed
- [ ] Environment variables set
- [ ] Cloud Flows active

## 🛠️ Setup & Installation

### Prerequisites

- Installation CreatorKit (pcf components allowed on environment)
- App Registration
- Connections
  - Azure Blob Service Principal
  - Dataverse - Service User
  - Excel - Service User
  - Office 365 Groups - Service User
  - Office 365 Outlook - Service User
  - Office 365 Users - Service User
  - Office 365 Users - User
  - OneDrive for Business - Service User
  - SharePoint - Service User
- SharePoint Bibliotheken
- Shared Mailbox
- Service Account
- PowerShell Modul MS Graph PowerShell

### 1. Environment Configuration

1. Go to the Power Platform admin center and click on the environment(s)
2. Click on `Settings`
3. Expand `Product` and click on `Features`
4. Enable `Power Apps component framekwork for canvas apps`

### 2. Create SharePoint libraries & permissions

#### Create libraries

1. Create a new SharePoint site collection called `Flow`
2. Make sure the existing "Documents" library exists
3. Create a library called `Backup`
4. Create a library called `Templates`
5. Create a library called `DigitalerPosteingang`
6. Create a library called `DigitalerPosteingangIn`
7. (Optional) Create an additional library for triggers
8. (Optional) Create an additional library for actions (saving documents)

#### Upload documents

Upload the [documents](TemplateFiles.zip) to the `Templates` library

#### Set permissions

- Documents
  - Contribute: Everyone
- Backup
  - Contribute: Service User
  - Read: Marc/Nander
- Templates
  - Read: Everyone
  - Contribute: Service User
- DigitalerPosteingang
  - Contribute: Service User
- DigitalerPosteingangIn
  - Contribute: Printers will save their scanned files here (or a flow which will be triggerd by an incoming mail and then saves the attachments)
  - Contribute: Service User
- Optional: Additional library for triggers
- Optional: Additional library for actions (saving documents)

### 3. Create service user

1. Create a service user
2. Assign a `M365 Business Basic/Premium/E1/E3`, as well as `Power Automate Premium` license

### 4. Create shared mailbox and set permissions

1. Create a shared mailbox
2. Set "Send As" permissions to the service account from the previous step

### 5. Install creator kit

1. Use the [Creator Kit](CreatorKitCore_1_0_20250310_1_managed.zip) and upload it as a solution

### 6. Create App Registration

1. Create an app registration called, name of your choosing, e.g. prd-01-appl-flow
2. Add Dynamics CRM API permissions of type Delegate with user_impersonation
3. Click on Certificates & secrets
4. Generate a new secret and give it a description (e.g. Flow - Dataverse)

### 7. Follow the instructions from the azure function

At this point, the azure function instructions can be followed. Once done, come back here and continue

### 8. Sites.Selected Permissions

The service principal needs to be created before continuing with this step.
To give permissions to sites.selected, we have 2 options. Choose one that works best for you.

#### Option 1: Graph Explorer

```http
GET | https://graph.microsoft.com/v1.0/sites?select=webUrl,Title,Id&$search="<Name of the site>*"
POST | https://graph.microsoft.com/v1.0/sites/<SiteId from above>/permissions
{
    "roles": [
        "write"
    ],
    "grantedToIdentities": [
        {
            "application": {
                "id": "<Client ID App Registration>",
                "displayName": "<A display name the app, only used to identify>"
            }
        }
    ]
}
```

#### Option 2: MS Graph PowerShell

```powershell
Search-MgSite -Search '"<Name of the site>*"' | Select-Object WebUrl, DisplayName, Id

$siteId = "<SiteId>"
$body = @{
    roles = @("write")
    grantedToIdentities = @(
        @{
            application = @{
                id: "<Client ID App Registration>",
                displayName: "<A display name the app, only used to identify>"
            }
        }
    )
} | ConvertTo-Json -Depth 10
```

### 9. Upload solution file

1. Upload the file [ProcessApp_1_0_0_18.zip](ProcessApp_1_0_0_18.zip) (DEV), respectively [ProcessApp_1_0_0_18_managed.zip](ProcessApp_1_0_0_18_managed.zip) (PRD) to the solutions
2. Set all connections and variables (if first time deployment. This step isn't necessary if the solution has already been deployed before and no new connections/variables have been added)

#### Connectors

Log in with all the prompted connectors. Make sure to login with a service principal if the connection name is called "Service Principal", or with the service account if it's called "Service Account". If it's called "User Account", you may login with your personal account.

#### Apply role to Service Principal

1. Open the Power Platform Admin Center
2. Click on the environment where you installed the solution to
3. Click on `Settings`
4. Expand `Users + permissions` and click on Application users
5. Click on `New app user`
6. Click on `Add an app` and add the service principal from the previous step
7. Set the business unit
8. Click on the edit icon next to `Security roles`
9. Add the "Flow Admin" role and save

#### Add Users

1. Share the app with all users
2. Make sure the role "Flow User" is assigned

#### Environment variables

Make sure the following environment variables have the right values:

- flowAppUrl: The URL to the app. You can only get the URL of the app once the solution has been deployed for the first time
- flowSharePointSites: a JSON with the following structure:

```json
{
  "sites": [
    {
      "BaseUrl": "https://visionand.sharepoint.com/sites/fabian",
      "ServerRelativeUrl": "/sites/Fabian/Shared Documents",
      "LibraryId": "3ab84f45-a6c0-4699-a335-a5f605948b77",
      "Name": "Fabian",
      "Type": "site"
    },
    {
      "BaseUrl": "https://visionand.sharepoint.com/sites/Flow2",
      "ServerRelativeUrl": "/sites/Flow2/Freigegebene Dokumente",
      "LibraryId": "ff5affaf-d590-4e9a-bce7-c29cef332e1b",
      "Name": "Flow2",
      "Type": "site"
    }
  ]
}
```

- flowSharePointSitesAction: a JSON with the following structure:

```json
{
  "sites": [
    {
      "BaseUrl": "https://visionand.sharepoint.com/sites/prj-1020",
      "ServerRelativeUrl": "/sites/prj-1020/Freigegebene Dokumente",
      "LibraryId": "9f132a76-7d36-473c-aac7-f45647c3f8ee",
      "Name": "VGP - Prozess App",
      "Type": "site"
    },
    {
      "BaseUrl": "https://visionand.sharepoint.com/sites/TEST-visionand",
      "ServerRelativeUrl": "/sites/TEST-visionand/Freigegebene Dokumente",
      "LibraryId": "70f8327e-e21c-429a-8cb0-4973d7342c7e",
      "Name": "TEST - visionand",
      "Type": "site"
    },
    {
      "BaseUrl": "https://visionand.sharepoint.com/sites/fabian",
      "ServerRelativeUrl": "/sites/Fabian/Shared Documents",
      "LibraryId": "3ab84f45-a6c0-4699-a335-a5f605948b77",
      "Name": "Fabian",
      "Type": "site"
    },
    {
      "BaseUrl": "https://visionand.sharepoint.com/sites/Flow2",
      "ServerRelativeUrl": "/sites/Flow2/Freigegebene Dokumente",
      "LibraryId": "ff5affaf-d590-4e9a-bce7-c29cef332e1b",
      "Name": "Flow2",
      "Type": "site"
    }
  ]
}
```

- flowDisplaySettings

```json
{ "flowName": "Flow", "flowObjectId": "fce29f87-0401-4204-b7f6-c9b3446bf4a6" }
```

- flowOpenDataSampleFileUrl: The URL to the sample file for bulk uploads (to be found in the Templates folder)

#### Other

1. Make sure that all flows are turned on
2. Make sure all users are in the defined groups
3. Test the app for any errors

### 10. Add App Settings records

If the following record already exist, skip this step. Otherwise, follow:

1. Go to https://make.powerapps.com (ensure the environment)
2. Click on Tables
3. Search for "AppSettings"
4. Open it and add the following record:

```
Name: Last Document Check
Key: lastDocCheck
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏢 About Vision&

Developed by [visionand AG](https://visionand.ch) - your business, simply brilliant

---

**Last Updated**: August 2025  
**Version**: 1.0.0
