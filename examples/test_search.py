#!/usr/bin/env python3
"""Simple test script to demonstrate NPI registry search functionality."""

import asyncio
from npi_registry_mcp.server import NPIRegistryClient, NPISearchParams


async def main():
    """Test the NPI registry client."""
    client = NPIRegistryClient()

    try:
        # Test search for a common provider name
        print("🔍 Searching for providers named 'Smith' in California...")
        params = NPISearchParams(last_name="Smith", state="CA", limit=3)
        results = await client.search(params)

        print(f"✅ Found {len(results)} results:")
        for i, provider in enumerate(results, 1):
            print(f"\n{i}. NPI: {provider.npi}")
            print(f"   Type: {provider.entity_type}")
            if provider.is_organization:
                print(f"   Organization: {provider.organization_name}")
            else:
                print(f"   Name: {provider.first_name} {provider.last_name}")
                if provider.credential:
                    print(f"   Credential: {provider.credential}")
            print(f"   Status: {provider.status}")

        # Test search by NPI number (example)
        print("\n" + "="*50)
        print("🔍 Testing NPI number search (this will likely return no results)...")
        params = NPISearchParams(npi="1234567890")
        results = await client.search(params)
        print(f"✅ NPI search returned {len(results)} results")

    except Exception as e:
        print(f"❌ Error during search: {e}")

    finally:
        await client.close()
        print("\n🔒 Client closed successfully")


if __name__ == "__main__":
    asyncio.run(main())