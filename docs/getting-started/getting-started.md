<!--

Eclipse Tractus-X - Software Development KIT

Copyright (c) 2025 LKS Next
Copyright (c) 2025 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This work is made available under the terms of the
Creative Commons Attribution 4.0 International (CC-BY-4.0) license,
which is available at
https://creativecommons.org/licenses/by/4.0/legalcode.

SPDX-License-Identifier: CC-BY-4.0

-->
# Tractus-SDK Documentation

## Prerequisites

Before getting started with the Tractus-X SDK, ensure you have:

- **Python 3.12+** installed on your system
- **Internet connection** for downloading packages
- **Basic Python knowledge** (variables, functions, imports)
- **Text editor** or IDE for writing code

## Installation Guide

### Development Environment Setup

We recommend using a virtual environment to avoid conflicts with other Python projects:

```bash title="Create Virtual Environment"
# Create a new virtual environment
python -m venv tractux-sdk-env

# Activate the environment
# On Windows:
tractux-sdk-env\Scripts\activate
# On macOS/Linux:
source tractux-sdk-env/bin/activate
```

The Tractus-X SDK can be installed in two ways: from PyPI (recommended for most users) or from source (for developers).

=== "Install from PyPI (Recommended)"

    This is the easiest way to get started:

    ```bash
    # Install the SDK directly from PyPI (recommended for users)
    pip install tractusx-sdk
    
    # Verify the installation works
    python -c "
    try:
        from tractusx_sdk.dataspace.services import BaseConnectorService
        print('✅ SDK Ready!')
        print('BaseConnectorService imported successfully')
    except Exception as e:
        print('❌ Import failed:')
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    "
    ```

=== "Install from Source"

    If you need the latest development version or want to contribute:

    ```bash
    # Only use this if you need the latest development version
    git clone https://github.com/eclipse-tractusx/tractusx-sdk.git
    cd tractusx-sdk
    pip install -e .
    
    # Verify installation
    python -c "
    try:
        from tractusx_sdk.dataspace.services import BaseConnectorService
        print('✅ SDK Ready!')
        print('BaseConnectorService imported successfully')
    except Exception as e:
        print('❌ Import failed:')
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    "
    ```

!!! success "Installation Complete!"
    If you see "✅ SDK Ready!" then you're all set to continue to the next step!

!!! warning "Compatibility Notice"
    Currently this SDK is not 100% compatible and has not been tested against the `v0.11.x` connector. The issue is being worked on [here](https://github.com/eclipse-tractusx/tractusx-sdk/issues/159).

## First Step: Creation of an Asset

Now let's create your first data asset in the dataspace. This example shows you the basic workflow of connecting to a dataspace, requesting the current assets, and creating an asset.

!!! info "Prerequisites"
    You will need a connector **deployed** to be able to follow this tutorial.

### Basic Configuration

Let's configure your connection to a dataspace connector and request all available assets:

Create a file called `connect.py` with your configuration and connection logic:
    
```python
from tractusx_sdk.dataspace.services.connector import BaseConnectorProviderService
from tractusx_sdk.dataspace.services.connector.service_factory import ServiceFactory
import logging

# Step 1: Configure your connector settings
# Replace these with your actual connector details
consumer_connector_controlplane_hostname = "https://connector.example.com"
consumer_connector_controlplane_management_api = "/management"
consumer_api_key_header = "X-Api-Key"
consumer_api_key = "your-api-key"
consumer_dataspace_version = "jupiter"  # or "saturn" for latest

# Step 2: Set up headers for API authentication
consumer_connector_headers = {
    consumer_api_key_header: consumer_api_key,
    "Content-Type": "application/json"
}

# Step 3: Initialize logger
logger = logging.getLogger(__name__)



# Step 4: Create connector service using ServiceFactory
provider_connector_service: BaseConnectorProviderService = ServiceFactory.get_connector_provider_service(
    dataspace_version=consumer_dataspace_version,
    base_url=consumer_connector_controlplane_hostname,
    dma_path=consumer_connector_controlplane_management_api,
    headers=consumer_connector_headers,
    logger=logger,
    verbose=True
)

# Step 5: Test the connection
try:
    print("🔗 Connecting to dataspace...")

    assets = provider_connector_service.assets.get_all()
    
    # Check if assets is a Response object and extract the data
    if hasattr(assets, 'json'):
        # If it's a Response object, get the JSON data
        assets_data = assets.json()
        print("📦 Assets data:")
        print(assets_data)
    elif hasattr(assets, 'status_code'):
        # If it's a Response object but JSON parsing fails
        print(f"✅ Response status: {assets.status_code}")
        print(f"📄 Raw response text: {assets.text}")
    else:
        # If it's already parsed data
        print("📦 Assets:")
        print(assets)

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("💡 Check your configuration values and network connection")
```

Run this script to test your connection:

```bash
python connect.py
```

!!! info "Configuration Values"
    **Replace the configuration values** in the script with your actual connector details:
    
    - `consumer_connector_controlplane_hostname`: Your connector URL
    - `consumer_api_key`: Your API key for authentication  
    - `consumer_connector_controlplane_management_api`: Management API path (usually `/management`)
    - `consumer_dataspace_version`: Version of your dataspace connector
    
    Contact your dataspace administrator for these values.

!!! tip "Connection Tips"
    🔧 **Start simple**: Test connection before building complex features  
    📦 **Check assets**: See what data is available in your dataspace  
    📞 **Get help**: Contact your dataspace administrator if connection fails

### Create an Asset

Now let's create a new data asset in the dataspace:

Modify the file called `connect.py`:

```python
from tractusx_sdk.dataspace.services.connector import BaseConnectorProviderService
from tractusx_sdk.dataspace.services.connector.service_factory import ServiceFactory
import logging

# Step 1: Configure your connector settings
# Replace these with your actual connector details
consumer_connector_controlplane_hostname = "https://connector.example.com"
consumer_connector_controlplane_management_api = "/management"
consumer_api_key_header = "X-Api-Key"
consumer_api_key = "your-api-key"
consumer_dataspace_version = "jupiter"  # or "saturn" for latest

# Step 2: Set up headers for API authentication
consumer_connector_headers = {
    consumer_api_key_header: consumer_api_key,
    "Content-Type": "application/json"
}

# Step 3: Initialize logger
logger = logging.getLogger(__name__)



# Step 4: Create connector service using ServiceFactory
provider_connector_service: BaseConnectorProviderService = ServiceFactory.get_connector_provider_service(
    dataspace_version=consumer_dataspace_version,
    base_url=consumer_connector_controlplane_hostname,
    dma_path=consumer_connector_controlplane_management_api,
    headers=consumer_connector_headers,
    logger=logger,
    verbose=True
)

# Step 5: Test the connection
try:
    print("🔗 Connecting to dataspace...")

    # assets = provider_connector_service.assets.get_all()
    
    # # Check if assets is a Response object and extract the data
    # if hasattr(assets, 'json'):
    #     # If it's a Response object, get the JSON data
    #     assets_data = assets.json()
    #     print("📦 Assets data:")
    #     print(assets_data)
    # elif hasattr(assets, 'status_code'):
    #     # If it's a Response object but JSON parsing fails
    #     print(f"✅ Response status: {assets.status_code}")
    #     print(f"📄 Raw response text: {assets.text}")
    # else:
    #     # If it's already parsed data
    #     print("📦 Assets:")
    #     print(assets)

    response = provider_connector_service.create_asset(
        asset_id="test-asset-001",
        base_url="https://example.com/data",
        dct_type="example-type",
        version="3.0"
    )

    print("✅ Connection successful!")
    print("📦 Created Asset:")
    print(response)

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("💡 Check your configuration values and network connection")
```

Run the script:

```bash
python connect.py
```

!!! info "What You'll See"
    This script shows you all the data assets available in your dataspace, including manufacturing data, supply chain information, and other business data shared by participants.

### Request the Created Asset and Verify

Let's request access to the asset we just created and get the data:

Create a file called `request_asset.py`:

```python
from tractusx_sdk.dataspace.services.connector import BaseConnectorProviderService
from tractusx_sdk.dataspace.services.connector.service_factory import ServiceFactory
import logging

# Step 1: Configure your connector settings
# Replace these with your actual connector details
consumer_connector_controlplane_hostname = "https://connector.example.com"
consumer_connector_controlplane_management_api = "/management"
consumer_api_key_header = "X-Api-Key"
consumer_api_key = "your-api-key"
consumer_dataspace_version = "jupiter"  # or "saturn" for latest

# Step 2: Set up headers for API authentication
consumer_connector_headers = {
    consumer_api_key_header: consumer_api_key,
    "Content-Type": "application/json"
}

# Step 3: Initialize logger
logger = logging.getLogger(__name__)



# Step 4: Create connector service using ServiceFactory
provider_connector_service: BaseConnectorProviderService = ServiceFactory.get_connector_provider_service(
    dataspace_version=consumer_dataspace_version,
    base_url=consumer_connector_controlplane_hostname,
    dma_path=consumer_connector_controlplane_management_api,
    headers=consumer_connector_headers,
    logger=logger,
    verbose=True
)

# Step 5: Test the connection
try:
    print("🔗 Connecting to dataspace...")

    # assets = provider_connector_service.assets.get_all()
    
    # # Check if assets is a Response object and extract the data
    # if hasattr(assets, 'json'):
    #     # If it's a Response object, get the JSON data
    #     assets_data = assets.json()
    #     print("📦 Assets data:")
    #     print(assets_data)
    # elif hasattr(assets, 'status_code'):
    #     # If it's a Response object but JSON parsing fails
    #     print(f"✅ Response status: {assets.status_code}")
    #     print(f"📄 Raw response text: {assets.text}")
    # else:
    #     # If it's already parsed data
    #     print("📦 Assets:")
    #     print(assets)

    # response = provider_connector_service.create_asset(
    #     asset_id="test-asset-001",
    #     base_url="https://example.com/data",
    #     dct_type="example-type",
    #     version="3.0"
    # )

    # print("✅ Connection successful!")
    # print("📦 Created Asset:")
    # print(response)

    response_specific = provider_connector_service.assets.get_by_id("test-asset-001")
    print("✅ Connection successful!")
    print("📦 Retrieved Asset by ID:")
    print(response_specific.json())

except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("💡 Check your configuration values and network connection")
```

Run the script:

```bash
python connect.py
```

!!! success "Data Access Complete!"
    Congratulations! You've successfully created an asset and accessed it.

### Troubleshooting

If you encounter issues, here are common solutions:

??? question "Import Errors"
    
    **Problem**: `ModuleNotFoundError: No module named 'tractusx_sdk'`
    
    **Solutions**:
    - Ensure you activated your virtual environment
    - Reinstall the SDK: `pip uninstall tractusx-sdk && pip install tractusx-sdk`
    - Check Python version: `python --version` (should be 3.12+)

??? question "Connection Errors"
    
    **Problem**: Cannot connect to connector
    
    **Solutions**:
    - Verify you have valid connector credentials
    - Check network connectivity
    - Contact your dataspace administrator for correct configuration

### Next Steps

Now that you have the SDK installed and verified:

1. **📚 Explore Libraries**: Learn about the [Dataspace Library](../user-guide/dataspace-library/index.md) for connector services
2. **🔍 Read Services Documentation**: Check out [connector services](../user-guide/dataspace-library/connector/services.md) for detailed API reference
3. **📖 SDK Structure**: Understand the [SDK architecture](../user-guide/sdk-structure-and-components.md)
4. **🤝 Join Community**: Connect with other developers in our [discussions](https://github.com/eclipse-tractusx/tractusx-sdk/discussions)

## NOTICE

This work is licensed under the [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode).

- SPDX-License-Identifier: CC-BY-4.0
- SPDX-FileCopyrightText: 2025 Contributors to the Eclipse Foundation
- Source URL: https://github.com/eclipse-tractusx/tractusx-sdk
