#################################################################################
# Eclipse Tractus-X - Software Development KIT
#
# Copyright (c) 2025 CGI Deutschland B.V. & Co. KG
# Copyright (c) 2025 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the
# License for the specific language govern in permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0
#################################################################################

import time
import logging
from typing import Optional
from requests import Response

from ...tools.http_tools import HttpTools
from ...managers import OAuth2Manager

class DiscoveryFinderService:

    @staticmethod
    def find_discovery_urls(url:str,  oauth:OAuth2Manager, keys:list=["bpn"], types_key:str="types", endpoints_key:str="endpoints", endpoint_address_key:str="endpointAddress", return_type_key:str='type') -> str | None:
        """
          Allows you to find a discovery service urls by key
        """

        ## Check if IAM is connected
        if(not oauth.connected):
            raise ConnectionError("[EDC Discovery Service] The authentication service is not connected! Please execute the oauth.connect() method")
        
        ## Setup headers and body
        headers:dict = oauth.add_auth_header(headers={'Content-Type' : 'application/json'})
        body:dict = {
            types_key: keys
        }

        response:Response = HttpTools.do_post(url=url, headers=headers, json=body)
        ## In case the response code is not successfull or the response is null
        if(response is None or response.status_code != 200):
            raise Exception("[EDC Discovery Service] It was not possible to get the discovery service because the response was not successful!")
        
        data = response.json()

        if(not(endpoints_key in data) or len(data[endpoints_key]) == 0):
            raise Exception("[EDC Discovery Service] No endpoints were found in the discovery service for this keys!")

        # Map to every key the endpoint address
        return dict(map(lambda x: (x[return_type_key], x[endpoint_address_key]), data[endpoints_key]))

      
class ConnectorDiscoveryService:
    
    connector_discovery_url:str
    oauth:OAuth2Manager
    connector_discovery_key:str
    discovery_finder_url:str
    cache_timeout_seconds:int
    discovery_cache:dict
    endpoint_address_key:str
    types_key:str
    endpoints_key:str
    return_type_key:str
    verbose:bool
    logger:Optional[logging.Logger]

    def __init__(self, oauth:OAuth2Manager, discovery_finder_url:str, connector_discovery_key:str="bpn", 
                 cache_timeout_seconds:int = 60 * 60 * 12, endpoint_address_key:str="endpointAddress", 
                 types_key:str="types", endpoints_key:str="endpoints", return_type_key:str='type',
                 verbose:bool=False, logger:Optional[logging.Logger]=None):
        """
        Initialize the Connector Discovery Service with caching functionality.
        
        Args:
            oauth (OAuth2Manager): OAuth2 manager for authentication.
            discovery_finder_url (str): URL for the discovery finder service.
            connector_discovery_key (str): Key for connector discovery (default: "bpn").
            cache_timeout_seconds (int): Cache timeout in seconds (default: 12 hours).
            endpoint_address_key (str): Key for endpoint address in discovery response.
            types_key (str): Key for types in discovery response.
            endpoints_key (str): Key for endpoints in discovery response.
            return_type_key (str): Key for return type in discovery response.
            verbose (bool): Enable verbose logging (default: False).
            logger (Optional[logging.Logger]): Logger instance for logging (default: None).
        """
        self.oauth = oauth
        self.discovery_finder_url = discovery_finder_url
        self.connector_discovery_key = connector_discovery_key
        self.cache_timeout_seconds = cache_timeout_seconds
        self.discovery_cache = {}
        self.endpoint_address_key = endpoint_address_key
        self.types_key = types_key
        self.endpoints_key = endpoints_key
        self.return_type_key = return_type_key
        self.verbose = verbose
        self.logger = logger
        
        # Initialize the connector discovery URL
        self.connector_discovery_url = self._get_or_update_discovery_url()

    def get_connector_discovery_url(self, oauth:OAuth2Manager, discovery_finder_url:str, connector_discovery_key:str="bpn") -> str:
        """
        Fetches the discovery URL for connector discovery.

        Args:
            oauth (OAuth2Manager): OAuth2 manager for authentication.
            discovery_finder_url (str): URL for the discovery finder service.
            connector_discovery_key (str): Key for connector discovery (default: "bpn").

        Returns:
            str: The connector discovery URL.

        Raises:
            Exception: If no discovery endpoint is found for the given key.
        """
        endpoints = DiscoveryFinderService.find_discovery_urls(
            url=discovery_finder_url, 
            oauth=oauth, 
            keys=[connector_discovery_key], 
            endpoint_address_key=self.endpoint_address_key, 
            types_key=self.types_key, 
            endpoints_key=self.endpoints_key, 
            return_type_key=self.return_type_key
        )
        if(connector_discovery_key not in endpoints):
          raise Exception("[Connector Discovery Service] Connector Discovery endpoint not found!")
        
        return endpoints[connector_discovery_key]

    def _get_or_update_discovery_url(self, connector_discovery_key:str=None) -> str:
        """
        Retrieves a cached discovery URL or updates the cache if expired.
        
        Safety mechanism: If the refresh attempt fails, the cached URL is preserved
        to maintain service availability during temporary connectivity issues.

        Args:
            connector_discovery_key (str): The identifier key for the discovery type.
                                          If None, uses the instance's default key.

        Returns:
            str: A valid discovery URL.
            
        Raises:
            Exception: If no cached URL exists and the initial discovery fails.
        """
        if connector_discovery_key is None:
            connector_discovery_key = self.connector_discovery_key
            
        current_time = time.time()
        entry:dict = self.discovery_cache.get(connector_discovery_key)
        
        # Check if the entry exists and if it is still valid
        if (
            not entry or
            (current_time - entry.get("timestamp", 0)) > self.cache_timeout_seconds
        ):
            try:
                url = self.get_connector_discovery_url(
                    oauth=self.oauth,
                    discovery_finder_url=self.discovery_finder_url,
                    connector_discovery_key=connector_discovery_key
                )
                if url:
                    # Update cache only if successful
                    self.discovery_cache[connector_discovery_key] = {
                        "url": url,
                        "timestamp": current_time
                    }
                    if self.verbose and self.logger:
                        import datetime
                        cache_count = len(self.discovery_cache)
                        valid_until = datetime.datetime.fromtimestamp(current_time + self.cache_timeout_seconds)
                        self.logger.info(f"[Connector Discovery Service] Updated cache with new discovery URL for key '{connector_discovery_key}': {url}")
                        self.logger.info(f"[Connector Discovery Service] Cache status: {cache_count} URL(s) cached, valid until {valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as e:
                # If we have a cached entry, preserve it and continue using it
                if entry:
                    # Log the error but continue with cached URL
                    if self.verbose and self.logger:
                        self.logger.warning(f"[Connector Discovery Service] Failed to refresh discovery URL, using cached version. Error: {str(e)}")
                    return entry["url"]
                else:
                    # No cached entry available, re-raise the exception
                    raise e
        else:
            # Using valid cached URL
            if self.verbose and self.logger and entry:
                import datetime
                cache_count = len(self.discovery_cache)
                valid_until = datetime.datetime.fromtimestamp(entry["timestamp"] + self.cache_timeout_seconds)
                self.logger.debug(f"[Connector Discovery Service] Using cached discovery URL for key '{connector_discovery_key}': {entry['url']}")
                self.logger.debug(f"[Connector Discovery Service] Cache status: {cache_count} URL(s) cached, this entry valid until {valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
            
        return self.discovery_cache[connector_discovery_key]["url"]

    def find_connector_by_bpn(self, bpn:str, bpn_key:str="bpn", connector_endpoint_key:str="connectorEndpoint") -> list | None:
        """
        Finds connector endpoints for a given BPN using the cached discovery URL.

        Args:
            bpn (str): The Business Partner Number to search for.
            bpn_key (str): The key for BPN in the response (default: "bpn").
            connector_endpoint_key (str): The key for connector endpoints in the response (default: "connectorEndpoint").

        Returns:
            list | None: List of connector endpoints for the BPN, or None if not found.

        Raises:
            Exception: If the connector discovery service request fails.
        """
        # Use cached discovery URL, refresh if necessary
        discovery_url = self._get_or_update_discovery_url()

        body:list = [
            bpn
        ]
        
        headers:dict = self.oauth.add_auth_header(headers={'Content-Type' : 'application/json'})

        response = HttpTools.do_post(url=discovery_url, headers=headers, json=body)
        if(response is None or response.status_code != 200):
            raise Exception("[Connector Discovery Service] It was not possible to get the connector urls because the connector discovery service response was not successful!")
        
        json_response:dict = response.json()

        # Iterate over the json_response to find the connectorEndpoint for the specified BPN
        for item in json_response:
            if item.get(bpn_key) == bpn:
                return item.get(connector_endpoint_key, [])
        # If the BPN is not found, return None or an empty list
        return None