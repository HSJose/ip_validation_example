# Test this script with:
# pip install httpx rich
# python verify_ip_parallel.py 8.8.8.8

import httpx
import asyncio
import sys
import json
from rich import print
from rich.panel import Panel
from collections import Counter

async def fetch_geo_data(client, service_name, url):
    """
    An asynchronous function to fetch geolocation data from a single URL.
    """
    print(f"  [cyan]Sending request to {service_name}...[/cyan]")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = await client.get(url, timeout=12, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        location_info = {}

        if service_name == "ip-api.com":
            location_info = {
                "Country": data.get('country'), "Country Code": data.get('countryCode'),
                "Region": data.get('regionName'), "City": data.get('city'),
                "ISP": data.get('isp')
            }
        elif service_name == "ipinfo.io":
            country_code = data.get('country')
            location_info = {
                "Country": country_code, "Country Code": country_code,
                "Region": data.get('region'), "City": data.get('city'),
                "ISP": data.get('org')
            }
        elif service_name == "ipwho.is":
            location_info = {
                "Country": data.get('country'), "Country Code": data.get('country_code'),
                "Region": data.get('region'), "City": data.get('city'),
                "ISP": data.get('isp')
            }
        elif service_name == "get.geojs.io":
            location_info = {
                "Country": data.get('country'), "Country Code": data.get('country_code'),
                "Region": data.get('region'), "City": data.get('city'),
                "ISP": data.get('organization_name')
            }
        return service_name, location_info

    except httpx.HTTPStatusError as e:
         return service_name, {"Error": f"HTTP Error: {e.response.status_code}"}
    except httpx.RequestError as e:
        return service_name, {"Error": f"Request failed: {e.__class__.__name__}"}
    except json.JSONDecodeError:
        return service_name, {"Error": "Failed to decode JSON response."}

async def main(ip_address):
    """
    Main async function to run all API calls and perform a consensus check.
    """
    print(f"🔍 [bold green]Verifying IP Address: {ip_address}[/bold green]")
    print("-------------------------------------")

    services = {
        "ip-api.com": f"http://ip-api.com/json/{ip_address}",
        "ipinfo.io": f"https://ipinfo.io/{ip_address}/json",
        "ipwho.is": f"https://ipwho.is/{ip_address}",
        "get.geojs.io": f"https://get.geojs.io/v1/ip/geo/{ip_address}.json"
    }

    timeout = httpx.Timeout(10.0, connect=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = [fetch_geo_data(client, name, url) for name, url in services.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    print("\n[bold]--- Geolocation Verification Report ---[/bold]")
    processed_results = []
    for res in results:
        if isinstance(res, tuple):
            processed_results.append(res)
        elif isinstance(res, Exception):
             print(f"\n[red]Unexpected error during gathering: {res}[/red]")

    for service, info in sorted(processed_results):
        print(f"\n[bold yellow][{service}][/bold yellow]")
        if "Error" in info:
            print(f"  [red]Error: {info['Error']}[/red]")
        else:
            for key, value in info.items():
                print(f"  {key:<15}: {value}")
    print("---------------------------------------")

    # --- NEW: CONSENSUS CHECK LOGIC ---
    print("\n[bold]--- Consensus Check ---[/bold]")
    
    country_codes = [
        info["Country Code"]
        for _, info in processed_results
        if "Error" not in info and info.get("Country Code")
    ]
    
    if len(country_codes) < 2:
        print("[yellow]Not enough data for a consensus check.[/yellow]")
    else:
        counts = Counter(country_codes)
        consensus_code, consensus_count = counts.most_common(1)[0]
        total_checks = len(country_codes)
        mismatch_count = total_checks - consensus_count
        mismatch_percentage = (mismatch_count / total_checks) * 100
        
        print(f"Total successful checks: {total_checks}")
        print(f"Most common Country Code: '[bold]{consensus_code}[/bold]' (found in {consensus_count} of {total_checks} checks)")
        
        if mismatch_percentage > 25:
            message = (
                f"[bold]Mismatch Alert![/bold]\n\n"
                f"[yellow]{mismatch_percentage:.1f}%[/yellow] of services did not match the consensus code ('{consensus_code}')."
            )
            print(Panel(message, title="[bold red]Verification Failed[/bold red]", border_style="red", expand=False))
        else:
            message = (
                f"[bold]All Clear![/bold]\n\n"
                f"The mismatch rate is [green]{mismatch_percentage:.1f}%[/green], which is within the acceptable 25% threshold."
            )
            print(Panel(message, title="[bold green]Verification Passed[/bold green]", border_style="green", expand=False))
            
    print("---------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("[red]Usage: python verify_ip_final.py <ip_address>[/red]")
        sys.exit(1)

    ip_to_verify = sys.argv[1]
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main(ip_to_verify))
