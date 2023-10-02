#!/usr/bin/env python
import sys
import requests
from forcediphttpsadapter.adapters import ForcedIPHTTPSAdapter
import csv
import ipaddr
import argparse
    
def bypassCloudflare(url, ip):
    session = requests.Session()
    session.mount(url, ForcedIPHTTPSAdapter(dest_ip=ip))
    r = session.get(url, verify=False)
    print(r.text)

def parse_args():
    parser = argparse.ArgumentParser("cloudflare-waf-debug")
    parser.add_argument("-url","--url", required=True, help="Url to make the test request", type=str)
    parser.add_argument("-ip","--ip", required=True, help="Origin IP address to bypass cloudflare proxy", type=str)
    parser.add_argument("-x","--request_type", required=False, help="GET or POST (GET is the default)", type=str, default="GET")
    parser.add_argument("-o","--output", required=False, help="Dump all WAF informations to the given file", type=str)

    return parser.parse_args()

def main():
    args = parse_args()
    bypassCloudflare(args.url,args.ip)

if __name__ == "__main__":
    main()