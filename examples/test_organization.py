#!/usr/bin/env python3
"""Test script to verify organization detection with enumeration_type."""

import asyncio
from npi_registry_mcp.server import NPIRegistryClient, NPISearchParams


async def main():
    """Test organization search."""
    client = NPIRegistryClient()

    try:
        # Search for hospitals to get some organizations
        print("🔍 Searching for hospitals in Pennsylvania...")
        params = NPISearchParams(organization_name="Hospital", state="PA", limit=5)
        results = await client.search(params)

        print(f"✅ Found {len(results)} results:")

        for i, provider in enumerate(results, 1):
            print(f"\n{i}. NPI: {provider.npi}")
            print(f"   Type: {provider.entity_type}")
            print(f"   Is Organization: {provider.is_organization}")

            if provider.is_organization:
                print(f"   Organization: {provider.organization_name}")
                if provider.authorized_official_first_name:
                    print(f"   Authorized Official: {provider.authorized_official_first_name} {provider.authorized_official_last_name}")
            else:
                print(f"   Name: {provider.first_name} {provider.last_name}")

            print(f"   Status: {provider.status}")
            print(f"   Addresses: {len(provider.addresses)} found")

    except Exception as e:
        print(f"❌ Error during search: {e}")

    finally:
        await client.close()
        print("\n🔒 Client closed successfully")


if __name__ == "__main__":
    asyncio.run(main())