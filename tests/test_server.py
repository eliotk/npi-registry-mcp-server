"""Tests for the NPI Registry MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from npi_registry_mcp.server import NPIRegistryClient, NPISearchParams, NPIProvider


class TestNPISearchParams:
    """Test NPISearchParams model."""

    def test_default_limit(self):
        """Test default limit is set correctly."""
        params = NPISearchParams()
        assert params.limit == 10

    def test_limit_validation(self):
        """Test limit validation."""
        # Valid limits
        params = NPISearchParams(limit=1)
        assert params.limit == 1

        params = NPISearchParams(limit=200)
        assert params.limit == 200

        # Invalid limits should raise validation error
        with pytest.raises(ValueError):
            NPISearchParams(limit=0)

        with pytest.raises(ValueError):
            NPISearchParams(limit=201)


class TestNPIRegistryClient:
    """Test NPIRegistryClient."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return NPIRegistryClient()

    @pytest.fixture
    def mock_response_data(self):
        """Mock API response data."""
        return {
            "results": [
                {
                    "number": "1234567890",
                    "enumeration_type": "NPI-1",  # Individual provider
                    "basic": {
                        "first_name": "John",
                        "last_name": "Smith",
                        "credential": "MD",
                        "status": "A",
                        "enumeration_date": "2010-05-05",
                        "last_updated": "2023-01-15",
                        "gender": "M"
                    },
                    "addresses": [],
                    "practice_locations": [],
                    "taxonomies": [],
                    "identifiers": []
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_search_success(self, client, mock_response_data):
        """Test successful search."""
        with patch.object(client.client, 'get') as mock_get:
            # Mock successful response
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            # Perform search
            params = NPISearchParams(first_name="John", last_name="Smith")
            results = await client.search(params)

            # Verify results
            assert len(results) == 1
            provider = results[0]
            assert provider.npi == "1234567890"
            assert provider.first_name == "John"
            assert provider.last_name == "Smith"
            assert provider.credential == "MD"
            assert not provider.is_organization
            assert provider.entity_type == "Individual"

    @pytest.mark.asyncio
    async def test_search_organization(self, client):
        """Test organization search."""
        mock_data = {
            "results": [
                {
                    "number": "9876543210",
                    "enumeration_type": "NPI-2",  # Organization
                    "basic": {
                        "organization_name": "Test Hospital",
                        "status": "A",
                        "enumeration_date": "2015-01-01",
                        "authorized_official_first_name": "Jane",
                        "authorized_official_last_name": "Doe"
                    },
                    "addresses": [],
                    "practice_locations": [],
                    "taxonomies": [],
                    "identifiers": []
                }
            ]
        }

        with patch.object(client.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_data
            mock_get.return_value = mock_response

            params = NPISearchParams(organization_name="Test Hospital")
            results = await client.search(params)

            assert len(results) == 1
            provider = results[0]
            assert provider.npi == "9876543210"
            assert provider.organization_name == "Test Hospital"
            assert provider.is_organization
            assert provider.entity_type == "Organization"
            assert provider.authorized_official_first_name == "Jane"

    @pytest.mark.asyncio
    async def test_search_http_error(self, client):
        """Test HTTP error handling."""
        with patch.object(client.client, 'get') as mock_get:
            # Mock HTTP error
            mock_get.side_effect = Exception("Network error")

            params = NPISearchParams(npi="1234567890")

            with pytest.raises(Exception, match="Unexpected error"):
                await client.search(params)

    @pytest.mark.asyncio
    async def test_close(self, client):
        """Test client cleanup."""
        with patch.object(client.client, 'aclose') as mock_close:
            await client.close()
            mock_close.assert_called_once()


class TestNPIProvider:
    """Test NPIProvider model."""

    def test_individual_provider(self):
        """Test individual provider creation."""
        provider = NPIProvider(
            npi="1234567890",
            entity_type="Individual",
            is_organization=False,
            first_name="John",
            last_name="Smith",
            credential="MD"
        )

        assert provider.npi == "1234567890"
        assert provider.entity_type == "Individual"
        assert not provider.is_organization
        assert provider.first_name == "John"
        assert provider.last_name == "Smith"
        assert provider.credential == "MD"

    def test_organization_provider(self):
        """Test organization provider creation."""
        provider = NPIProvider(
            npi="9876543210",
            entity_type="Organization",
            is_organization=True,
            organization_name="Test Hospital"
        )

        assert provider.npi == "9876543210"
        assert provider.entity_type == "Organization"
        assert provider.is_organization
        assert provider.organization_name == "Test Hospital"

    def test_default_lists(self):
        """Test default empty lists."""
        provider = NPIProvider(
            npi="1234567890",
            entity_type="Individual",
            is_organization=False
        )

        assert provider.addresses == []
        assert provider.practice_locations == []
        assert provider.taxonomies == []
        assert provider.identifiers == []