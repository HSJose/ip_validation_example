'''
I recommend using the verify_ip_parallel.py version for better performance.
Test this script with:
python verify_ip.py <ip_address>
try using 8.8.8.8
'''

import requests
import sys
import json

def verify_ip_geolocation(ip_address):
    """
    Queries multiple IP geolocation APIs to verify the location of an IP address.
    """
    print(f"🔍 Verifying IP Address: {ip_address}")
    print("-------------------------------------")

    # A dictionary of services to query.
    # You can easily add more services here.
    # For services that require an API key, append it to the URL.
    services = {
        "ip-api.com": f"http://ip-api.com/json/{ip_address}",
        "ipinfo.io": f"https://ipinfo.io/{ip_address}/json",
        "ipwhois.app": f"http://ipwho.is/{ip_address}",
        "get.geojs.io": f"https://get.geojs.io/v1/ip/geo/{ip_address}.json"
    }

    results = {}

    for service_name, url in services.items():
        print(f"🌐 Querying {service_name}...")
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes
            data = response.json()

            # Extracting common fields - may need adjustment for different APIs
            location_info = {
                "Country": data.get('country') or data.get('country_name'),
                "Region": data.get('regionName') or data.get('region_name') or data.get('region'),
                "City": data.get('city'),
                "ISP": data.get('isp') or data.get('org')
            }
            results[service_name] = location_info

        except requests.exceptions.RequestException as e:
            results[service_name] = {"Error": str(e)}
        except json.JSONDecodeError:
            results[service_name] = {"Error": "Failed to decode JSON response."}

    print("\n--- Geolocation Verification Report ---")
    for service, info in results.items():
        print(f"\n[{service}]")
        if "Error" in info:
            print(f"  Error: {info['Error']}")
        else:
            for key, value in info.items():
                print(f"  {key}: {value}")
    print("---------------------------------------")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_ip.py <ip_address>")
        sys.exit(1)

    ip_to_verify = sys.argv[1]
    verify_ip_geolocation(ip_to_verify)
