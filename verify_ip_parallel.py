'''
Test this script with:
python verify_ip_parallel.py <ip_address>
try using 8.8.8.8
'''

import httpx
import asyncio
import sys
import json

async def fetch_geo_data(client, service_name, url):
    """
    An asynchronous function to fetch geolocation data from a single URL.
    """
    print(f"  -> Sending request to {service_name}...")
    try:
        # Added a user-agent as some services may block default script agents.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = await client.get(url, timeout=10, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        
        # --- Data extraction logic customized for each service ---
        location_info = {}
        if service_name == "ip-api.com":
            location_info = {
                "Country": data.get('country'), "Region": data.get('regionName'),
                "City": data.get('city'), "ISP": data.get('isp')
            }
        elif service_name == "ipinfo.io":
            location_info = {
                "Country": data.get('country'), "Region": data.get('region'),
                "City": data.get('city'), "ISP": data.get('org')
            }
        elif service_name == "ipwhois.app":
            location_info = {
                "Country": data.get('country'), "Region": data.get('region'),
                "City": data.get('city'), "ISP": data.get('isp')
            }
        elif service_name == "get.geojs.io":
            location_info = {
                "Country": data.get('country'), "Region": data.get('region'),
                "City": data.get('city'), "ISP": data.get('organization_name')
            }
        return service_name, location_info

    except httpx.RequestError as e:
        return service_name, {"Error": f"Request failed: {e.__class__.__name__}"}
    except json.JSONDecodeError:
        return service_name, {"Error": "Failed to decode JSON response."}

async def main(ip_address):
    """
    Main async function to run all API calls in parallel.
    """
    print(f"🔍 Verifying IP Address: {ip_address}")
    print("-------------------------------------")

    services = {
        "ip-api.com": f"http://ip-api.com/json/{ip_address}",
        "ipinfo.io": f"https://ipinfo.io/{ip_address}/json",
        "ipwho.is": f"http://ipwho.is/{ip_address}",
        "get.geojs.io": f"https://get.geojs.io/v1/ip/geo/{ip_address}.json"
    }

    # An AsyncClient allows us to send multiple requests over the same connection.
    async with httpx.AsyncClient() as client:
        # Create a list of tasks to run concurrently
        tasks = [fetch_geo_data(client, name, url) for name, url in services.items()]
        
        # asyncio.gather runs all tasks in parallel and waits for them to complete.
        results = await asyncio.gather(*tasks)

    print("\n--- Geolocation Verification Report ---")
    # Sort results for consistent ordering
    for service, info in sorted(results):
        print(f"\n[{service}]")
        if "Error" in info:
            print(f"  Error: {info['Error']}")
        else:
            for key, value in info.items():
                print(f"  {key}: {value}")
    print("---------------------------------------")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_ip_parallel.py <ip_address>")
        sys.exit(1)

    ip_to_verify = sys.argv[1]
    # asyncio.run() is the standard way to execute an async main function.
    asyncio.run(main(ip_to_verify))
