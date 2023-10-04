#!/usr/bin/env python
import sys
import requests
import csv
from cf_purpleteam_toolkit_common import is_ipv4
import argparse

def get_cf_dns_entries(cf_token, zone_identifier,proxy_enabled=None):
    dns_entries = None
    if proxy_enabled == None:
        dns_entries = requests.get('https://api.cloudflare.com/client/v4/zones/' + zone_identifier + '/dns_records', params={"per_page":"50000"}, headers={"Authorization":"Bearer " + cf_token, "Content-Type":"application/json"}).json()['result']
    else:
        dns_entries = requests.get('https://api.cloudflare.com/client/v4/zones/' + zone_identifier + '/dns_records', params={"per_page":"50000","proxied":proxy_enabled}, headers={"Authorization":"Bearer " + cf_token, "Content-Type":"application/json"}).json()['result']

    output = []
    output.append(["type","name","content","proxied"])
    for entry in dns_entries:
        raw = []
        raw.append(entry['type'])
        raw.append(entry['name'])
        raw.append(entry['content'])
        raw.append(entry['proxied'])
        output.append(raw)

    return output

def parse_args():
    parser = argparse.ArgumentParser("cf-dns-map")
    parser.add_argument("-cft","--cf_token", required=True, help="Cloudflare Authorization Bearer token", type=str)
    parser.add_argument("-zid","--zone_id", required=True, help="Cloudflare zone identifier", type=str)
    parser.add_argument("-o","--output", required=False, help="Dump all DNS informations to the given file", type=str)
    parser.add_argument('--proxied',required=False, action=argparse.BooleanOptionalAction)
    parser.add_argument('--not_proxied',required=False, action=argparse.BooleanOptionalAction)
    return parser.parse_args()

def main():
    args = parse_args()

    output = []
    if args.proxied:
        output = get_cf_dns_entries(args.cf_token, args.zone_id, True)
    elif args.not_proxied:
        output = get_cf_dns_entries(args.cf_token, args.zone_id, False)
    else:
        output = get_cf_dns_entries(args.cf_token, args.zone_id)

    if (args.output == None):
        writer = csv.writer(sys.stdout)
        writer.writerows(output)
    else:
        if args.output != None:
            with open(args.output, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(output)

if __name__ == "__main__":
    main()