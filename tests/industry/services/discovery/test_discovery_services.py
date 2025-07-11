import pytest
from unittest import mock
from tractusx_sdk.industry.services.discovery.discovery_services import BpnDiscoveryService

@pytest.fixture
def mock_oauth():
    mock_oauth = mock.Mock()
    mock_oauth.add_auth_header.side_effect = lambda headers: {**headers, "Authorization": "Bearer token"}
    return mock_oauth

@pytest.fixture
def service(mock_oauth):
    return BpnDiscoveryService(
        oauth=mock_oauth,
        discovery_finder_url="https://discovery.example.com",
        cache_timeout_seconds=10
    )

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.DiscoveryFinderService")
def test_get_connector_discovery_url_success(mock_finder, service, mock_oauth):
    mock_finder.find_discovery_urls.return_value = {"manufacturerPartId": "https://bpn.example.com"}
    url = service.get_connector_discovery_url(mock_oauth, "https://discovery.example.com")
    assert url == "https://bpn.example.com"

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.DiscoveryFinderService")
def test_get_connector_discovery_url_not_found(mock_finder, service, mock_oauth):
    mock_finder.find_discovery_urls.return_value = {}
    with pytest.raises(Exception, match="Connector Discovery endpoint not found"):
        service.get_connector_discovery_url(mock_oauth, "https://discovery.example.com")

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_search_bpns_success(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"bpns": [{"value": "BPNL0001"}, {"value": "BPNL0002"}]}
    mock_http.do_post.return_value = mock_response

    result = service.search_bpns(keys=["key1", "key2"])
    assert result == {"bpns": [{"value": "BPNL0001"}, {"value": "BPNL0002"}]}

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_search_bpns_unauthorized(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_response = mock.Mock()
    mock_response.status_code = 401
    mock_http.do_post.return_value = mock_response

    with pytest.raises(Exception, match="Unauthorized access"):
        service.search_bpns(keys=["key1"])

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_search_bpns_no_response(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_http.do_post.return_value = None

    with pytest.raises(Exception, match="No response received"):
        service.search_bpns(keys=["key1"])

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.op")
@mock.patch.object(BpnDiscoveryService, "search_bpns")
def test_find_bpns_returns_unique(mock_search, mock_op, service):
    mock_search.return_value = {"bpns": [{"value": "BPNL0001"}, {"value": "BPNL0001"}, {"value": "BPNL0002"}]}
    mock_op.extract_dict_values.return_value = ["BPNL0001", "BPNL0001", "BPNL0002"]
    result = service.find_bpns(keys=["key1"])
    assert set(result) == {"BPNL0001", "BPNL0002"}

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_set_identifier_success(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_response = mock.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"result": "ok"}
    mock_http.do_post.return_value = mock_response

    result = service.set_identifier("key1")
    assert result == {"result": "ok"}

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_set_identifier_failure(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_http.do_post.return_value = mock_response

    with pytest.raises(Exception, match="Failed to create BPN identifier"):
        service.set_identifier("key1")

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_set_multiple_identifiers_success(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_response = mock.Mock()
    mock_response.status_code = 201
    mock_response.json.return_value = [{"result": "ok"}]
    mock_http.do_post.return_value = mock_response

    result = service.set_multiple_identifiers(["key1", "key2"])
    assert result == [{"result": "ok"}]

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_delete_bpn_identifier_by_id_success(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_response = mock.Mock()
    mock_response.status_code = 204
    mock_http.do_delete.return_value = mock_response

    # Should not raise
    service.delete_bpn_identifier_by_id("resource123")

@mock.patch("tractusx_sdk.industry.services.discovery.discovery_services.HttpTools")
@mock.patch.object(BpnDiscoveryService, "_get_or_update_discovery_url")
def test_delete_bpn_identifier_by_id_failure(mock_get_url, mock_http, service):
    mock_get_url.return_value = "https://bpn.example.com"
    mock_response = mock.Mock()
    mock_response.status_code = 400
    mock_http.do_delete.return_value = mock_response

    with pytest.raises(Exception, match="Failed to delete BPN identifier"):
        service.delete_bpn_identifier_by_id("resource123")