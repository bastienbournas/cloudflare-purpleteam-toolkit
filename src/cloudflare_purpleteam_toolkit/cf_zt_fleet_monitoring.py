#!/usr/bin/env python
import requests
import argparse
import json
from datetime import datetime, timezone, timedelta

#
# Use cloudflare's API to retrieve all the WARP devices status. 
# The result is returned into a map, the key being the status and the value the list of users under this status
#
def get_cf_dex_devices_statuses(cf_account, cf_token):
    devices_statuses = []
    page = 1
    per_page = 50
    finished = False
    end_time = datetime.now(timezone.utc)
    begining_time = end_time - timedelta(minutes=10)

    while not finished:
        params = {
            'from': begining_time.isoformat(),
            'to': end_time.isoformat(),
            'page': page,
            'per_page': per_page
        }

        response = requests.get(
            f'https://api.cloudflare.com/client/v4/accounts/{cf_account}/dex/fleet-status/devices',
            headers={
                "Authorization": f"Bearer {cf_token}",
                "Content-Type": "application/json"
            },
            params=params
        )

        result = response.json()['result']

        if (not result) or (len(result) < per_page):
            finished = True  # Exit loop if there are no more results
        else:
            devices_statuses.extend(result)
            page += 1  # Go to next page

    status_email_map = {}
    seen_emails = set()

    for device in devices_statuses:
        email = device.get("personEmail")
        status = device.get("status")

        if email and email not in seen_emails:
            if status not in status_email_map:
                status_email_map[status] = []
            status_email_map[status].append(email)
            seen_emails.add(email)

    return status_email_map


#
# Argument parsing for CLI usage
#
def parse_args():
    parser = argparse.ArgumentParser("cloudflare-zt-fleet-monitoring")
    parser.add_argument("-cfa","--cf_account", required=True, help="Cloudflare account id", type=str)
    parser.add_argument("-cft","--cf_token", required=True, help="Cloudflare Authorization Bearer token", type=str)
    parser.add_argument("-s","--status", required=False, help="Get the fleet corresponding to the given status (connected, paused, etc). If not specified, all statuses are returned.", type=str)

    return parser.parse_args()

#
# Main
#
def main():
    args = parse_args()

    devices_statuses = get_cf_dex_devices_statuses(args.cf_account,args.cf_token)
    if args.status:
        if args.status in devices_statuses:
            print(json.dumps(devices_statuses.get(args.status), indent=2))
        else:
            print("Status " + args.status + " not found.")
            print("Available statuses are:")
            print(list(devices_statuses.keys()))
    else:
        print(json.dumps(devices_statuses, indent=2))


if __name__ == "__main__":
    main()