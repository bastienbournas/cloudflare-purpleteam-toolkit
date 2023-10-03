#!/usr/bin/env python
import sys
import requests
from forcediphttpsadapter.adapters import ForcedIPHTTPSAdapter
import argparse

#   
# Bypass cloudflare with the server orgin IP.
# Url is used to forge the appropriate host header, but the request is sent directly to the IP address.
# ForcedIPHTTPSAdapter is used to make the ssl scheme work (https).
#
def bypassCloudflareDirectly(url, ip):
    session = requests.Session()
    session.mount(url, ForcedIPHTTPSAdapter(dest_ip=ip))
    r = session.get(url, verify=False)
    print(r.text)

#
# Argument parsing for CLI usage
#
def parse_args():
    parser = argparse.ArgumentParser("cloudflare-waf-bypass")
    parser.add_argument('-d','--direct', required=False, action='store_true', help="Bypass cloudflare with the server orgin IP. Use with -url and -ip")
    parser.add_argument("-url","--url",  required=('--direct' in sys.argv) or ('-d' in sys.argv), help="Url to make the test request", type=str)
    parser.add_argument("-ip","--ip", required=('--direct' in sys.argv) or ('-d' in sys.argv), help="Origin IP address to bypass cloudflare proxy", type=str)
    parser.add_argument("-x","--request_type", required=False, help="GET or POST (GET is the default)", type=str, default="GET")
    parser.add_argument("-o","--output", required=False, help="Dump all WAF informations to the given file", type=str)

    if len(sys.argv)==1:
        parser.print_help()
        parser.exit()

    return parser, parser.parse_args()

#
# Main
#
def main():
    parser, args = parse_args()
    if args.direct : 
        bypassCloudflareDirectly(args.url,args.ip)
    else:
        parser.print_help()
        parser.exit()
        
if __name__ == "__main__":
    main()