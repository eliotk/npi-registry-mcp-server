#!/usr/bin/env python3
"""NPI Registry MCP Server.

An MCP server that provides tools for searching the National Provider Identifier (NPI) registry.
"""

import asyncio
import sys
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel, Field


class NPISearchParams(BaseModel):
    """Parameters for NPI registry search."""

    first_name: Optional[str] = Field(None, description="Provider's first name")
    last_name: Optional[str] = Field(None, description="Provider's last name")
    organization_name: Optional[str] = Field(None, description="Organization name")
    npi: Optional[str] = Field(None, description="Specific NPI number (10 digits)")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State abbreviation (e.g., 'CA', 'NY')")
    postal_code: Optional[str] = Field(None, description="ZIP/postal code")
    specialty: Optional[str] = Field(None, description="Provider specialty or taxonomy")
    limit: int = Field(10, description="Maximum number of results to return (1-200)", ge=1, le=200)


class NPIProvider(BaseModel):
    """NPI provider information."""

    npi: str
    entity_type: str
    replacement_npi: Optional[str] = None
    ein: Optional[str] = None
    is_organization: bool

    # Basic information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    name_prefix: Optional[str] = None
    name_suffix: Optional[str] = None
    credential: Optional[str] = None
    sole_proprietor: Optional[str] = None
    gender: Optional[str] = None
    enumeration_date: Optional[str] = None
    last_updated: Optional[str] = None
    status: Optional[str] = None

    # Organization information
    organization_name: Optional[str] = None
    organization_subpart: Optional[str] = None
    parent_organization_lbn: Optional[str] = None
    parent_organization_tin: Optional[str] = None
    authorized_official_first_name: Optional[str] = None
    authorized_official_last_name: Optional[str] = None
    authorized_official_title: Optional[str] = None
    authorized_official_telephone: Optional[str] = None

    # Addresses
    addresses: List[Dict[str, Any]] = Field(default_factory=list)

    # Practice locations
    practice_locations: List[Dict[str, Any]] = Field(default_factory=list)

    # Taxonomies (specialties)
    taxonomies: List[Dict[str, Any]] = Field(default_factory=list)

    # Other identifiers
    identifiers: List[Dict[str, Any]] = Field(default_factory=list)


class NPIRegistryClient:
    """Client for interacting with the NPI Registry API."""

    BASE_URL = "https://npiregistry.cms.hhs.gov/api/"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def search(self, params: NPISearchParams) -> List[NPIProvider]:
        """Search the NPI registry."""
        # Build query parameters
        query_params = {"version": "2.1", "limit": str(params.limit)}

        if params.npi:
            query_params["number"] = params.npi
        if params.first_name:
            query_params["first_name"] = params.first_name
        if params.last_name:
            query_params["last_name"] = params.last_name
        if params.organization_name:
            query_params["organization_name"] = params.organization_name
        if params.city:
            query_params["city"] = params.city
        if params.state:
            query_params["state"] = params.state
        if params.postal_code:
            query_params["postal_code"] = params.postal_code
        if params.specialty:
            query_params["taxonomy_description"] = params.specialty

        try:
            response = await self.client.get(
                f"{self.BASE_URL}",
                params=query_params
            )
            response.raise_for_status()
            data = response.json()

            results = []
            if "results" in data:
                for result in data["results"]:
                    provider = self._parse_provider(result)
                    results.append(provider)

            return results

        except httpx.HTTPError as e:
            raise Exception(f"Error searching NPI registry: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def _parse_provider(self, data: Dict[str, Any]) -> NPIProvider:
        """Parse NPI provider data from API response."""
        basic = data.get("basic", {})

        # Determine if this is an organization based on enumeration_type
        # NPI-1 = Individual, NPI-2 = Organization
        enumeration_type = data.get("enumeration_type", "")
        is_org = enumeration_type == "NPI-2"

        provider_data = {
            "npi": data.get("number", ""),
            "entity_type": "Organization" if is_org else "Individual",
            "replacement_npi": data.get("replacement_npi"),
            "ein": basic.get("ein"),
            "is_organization": is_org,
            "enumeration_date": basic.get("enumeration_date"),
            "last_updated": basic.get("last_updated"),
            "status": basic.get("status"),
            "sole_proprietor": basic.get("sole_proprietor"),
            "gender": basic.get("gender"),
        }

        if is_org:
            # Organization fields
            provider_data.update({
                "organization_name": basic.get("organization_name"),
                "organization_subpart": basic.get("organization_subpart"),
                "parent_organization_lbn": basic.get("parent_organization_lbn"),
                "parent_organization_tin": basic.get("parent_organization_tin"),
                "authorized_official_first_name": basic.get("authorized_official_first_name"),
                "authorized_official_last_name": basic.get("authorized_official_last_name"),
                "authorized_official_title": basic.get("authorized_official_title"),
                "authorized_official_telephone": basic.get("authorized_official_telephone"),
            })
        else:
            # Individual fields
            provider_data.update({
                "first_name": basic.get("first_name"),
                "last_name": basic.get("last_name"),
                "middle_name": basic.get("middle_name"),
                "name_prefix": basic.get("name_prefix"),
                "name_suffix": basic.get("name_suffix"),
                "credential": basic.get("credential"),
            })

        # Add addresses
        provider_data["addresses"] = data.get("addresses", [])

        # Add practice locations
        provider_data["practice_locations"] = data.get("practice_locations", [])

        # Add taxonomies
        provider_data["taxonomies"] = data.get("taxonomies", [])

        # Add other identifiers
        provider_data["identifiers"] = data.get("identifiers", [])

        return NPIProvider(**provider_data)


# Initialize FastMCP
mcp = FastMCP("NPI Registry MCP Server")

# Initialize NPI client
npi_client = NPIRegistryClient()


@mcp.tool()
async def search_npi_registry(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    organization_name: Optional[str] = None,
    npi: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    postal_code: Optional[str] = None,
    specialty: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search the National Provider Identifier (NPI) registry.

    The NPI registry contains information about healthcare providers and organizations
    in the United States. You can search by various criteria including name, NPI number,
    location, and specialty.

    WILDCARD SUPPORT: Most text fields support wildcard searches using '*' after at least
    2 characters for fuzzy matching (e.g., 'smith*', 'hosp*', 'cardi*').

    Args:
        first_name: Provider's first name (supports wildcards: 'john*' matches 'John', 'Johnny', etc.)
        last_name: Provider's last name (supports wildcards: 'smith*' matches 'Smith', 'Smithson', etc.)
        organization_name: Organization name (supports wildcards: 'hosp*' matches 'Hospital', 'Hospice', etc.)
        npi: Specific 10-digit NPI number to look up (exact match only)
        city: City name (supports wildcards: 'san*' matches 'San Francisco', 'San Diego', etc.)
        state: State abbreviation (e.g., 'CA', 'NY', 'TX') - exact match only
        postal_code: ZIP/postal code (supports wildcards: '902*' matches '90210', '90211', etc.)
        specialty: Provider specialty or taxonomy (supports wildcards: 'cardi*' matches 'Cardiology', 'Cardiac Surgery', etc.)
        limit: Maximum number of results to return (1-200, default: 10)

    Examples:
        - Find all Smiths: last_name='smith*'
        - Find hospitals: organization_name='hosp*'
        - Find cardiologists: specialty='cardio*'
        - Find providers in San cities: city='san*'
        - Find providers in 90210 area: postal_code='902*'

    Returns:
        Dictionary containing search results with provider information
    """
    try:
        # Validate input parameters
        if limit < 1 or limit > 200:
            return {
                "error": "Limit must be between 1 and 200",
                "results": []
            }

        # Validate NPI format if provided
        if npi and (not npi.isdigit() or len(npi) != 10):
            return {
                "error": "NPI must be exactly 10 digits",
                "results": []
            }

        # Validate state format if provided
        if state and len(state) != 2:
            return {
                "error": "State must be a 2-letter abbreviation (e.g., 'CA', 'NY')",
                "results": []
            }

        # Create search parameters
        params = NPISearchParams(
            first_name=first_name,
            last_name=last_name,
            organization_name=organization_name,
            npi=npi,
            city=city,
            state=state,
            postal_code=postal_code,
            specialty=specialty,
            limit=limit,
        )

        # Perform search
        providers = await npi_client.search(params)

        # Format results
        results = []
        for provider in providers:
            result = {
                "npi": provider.npi,
                "entity_type": provider.entity_type,
                "is_organization": provider.is_organization,
                "status": provider.status,
                "enumeration_date": provider.enumeration_date,
                "last_updated": provider.last_updated,
            }

            if provider.is_organization:
                result.update({
                    "organization_name": provider.organization_name,
                    "organization_subpart": provider.organization_subpart,
                    "authorized_official": {
                        "first_name": provider.authorized_official_first_name,
                        "last_name": provider.authorized_official_last_name,
                        "title": provider.authorized_official_title,
                        "telephone": provider.authorized_official_telephone,
                    } if provider.authorized_official_first_name else None,
                })
            else:
                result.update({
                    "name": {
                        "first": provider.first_name,
                        "last": provider.last_name,
                        "middle": provider.middle_name,
                        "prefix": provider.name_prefix,
                        "suffix": provider.name_suffix,
                        "credential": provider.credential,
                    },
                    "gender": provider.gender,
                    "sole_proprietor": provider.sole_proprietor,
                })

            # Add addresses
            if provider.addresses:
                result["addresses"] = provider.addresses

            # Add practice locations
            if provider.practice_locations:
                result["practice_locations"] = provider.practice_locations

            # Add taxonomies (specialties)
            if provider.taxonomies:
                result["taxonomies"] = provider.taxonomies

            # Add other identifiers
            if provider.identifiers:
                result["identifiers"] = provider.identifiers

            results.append(result)

        return {
            "success": True,
            "count": len(results),
            "results": results,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


async def cleanup():
    """Cleanup resources on shutdown."""
    await npi_client.close()


def main():
    """Main entry point for the MCP server."""
    try:
        # Run the MCP server - FastMCP handles the event loop internally
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        # Handle graceful shutdown
        print("\n🔒 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        raise


if __name__ == "__main__":
    main()