#!/usr/bin/env python
import sys
import requests
from forcediphttpsadapter.adapters import ForcedIPHTTPSAdapter
import argparse
import csv
from cf_purpleteam_toolkit_common import is_ipv4
from cf_dns_map import get_cf_dns_entries

#   
# Bypass cloudflare with the server orgin IP.
# Url is used to forge the appropriate host header, but the request is sent directly to the IP address.
# ForcedIPHTTPSAdapter is used to make the ssl scheme work (https).
#
def bypass_cloudflare_directly(url, ip):
    session = requests.Session()
    session.mount(url, ForcedIPHTTPSAdapter(dest_ip=ip))
    r = session.get(url, verify=False)
    print(r.text)

#   
# For the given proxied DNS entry name and IP, check for bypasses in the unproxied_entries list
#
def check_for_proxy_bypass(proxied_name, proxied_ip, unproxied_entries):
    bypass_list = []
    for unproxied_entry in unproxied_entries:
        if unproxied_entry[0] == "A":
            if is_ipv4(unproxied_entry[2]):
                ip = unproxied_entry[2]
                if proxied_ip == ip:
                    bypass_list.append(unproxied_entry)
        elif unproxied_entry[0] == "CNAME":
            cname_alias = unproxied_entry[2]
            if proxied_name == cname_alias:
                bypass_list.append(unproxied_entry)

    return bypass_list

#   
# Search for bypass threw DNS itself (unproxified CNAME, different unproxified entry with same IP, etc)
# Returns a list of DNS entries that allow to bypass a proxied DNS entry, following this format:
#   ["proxied_type","proxied_name","proxied_content","bypass_type","bypass_name","bypass_content"]
# Where proxied_* represents the attributes of the proxied entry that can be bypassed,
# and bypass_* represents the attributes of the entry that allows the bypass
#
def get_cf_bypassing_dns_entries(cf_token, zone_identifier):
    proxied_entries = get_cf_dns_entries(cf_token, zone_identifier, True)
    unproxied_entries = get_cf_dns_entries(cf_token, zone_identifier, False)
    
    output = []
    output.append(["proxied_type","proxied_name","proxied_content","bypass_type","bypass_name","bypass_content"])
    for proxied_entry in proxied_entries:
        if (is_ipv4(proxied_entry[2])):
            name = proxied_entry[1]
            ip = proxied_entry[2]
            bypass_list = check_for_proxy_bypass(name, ip, unproxied_entries)
            for bypass in bypass_list:
                output.append([proxied_entry[0], proxied_entry[1], proxied_entry[2], bypass[0],bypass[1],bypass[2]])

    return output

#
# Argument parsing for CLI usage
#
def parse_args():
    parser = argparse.ArgumentParser("cloudflare_waf_bypass")
    parser.add_argument('-d','--direct_bypass', required=False, action='store_true', help="Bypass cloudflare with the server orgin IP. Use with -url and -ip")
    parser.add_argument("-url","--url",  required=('--direct' in sys.argv) or ('-d' in sys.argv), help="Url to make the test request", type=str)
    parser.add_argument("-ip","--ip", required=('--direct' in sys.argv) or ('-d' in sys.argv), help="Origin IP address to bypass cloudflare proxy", type=str)
    parser.add_argument("-x","--request_type", required=False, help="GET or POST (GET is the default)", type=str, default="GET")
    parser.add_argument('-dns','--dns_bypass', required=False, action='store_true', help="Search for bypass threw DNS itself (unproxified CNAME, different unproxified entry with same IP, etc). Needs cloudflare API token: use with -cft and -zid options")
    parser.add_argument("-cft","--cf_token", required=('--dns_bypass' in sys.argv) or ('-dns' in sys.argv), help="Cloudflare Authorization Bearer token", type=str)
    parser.add_argument("-zid","--zone_id", required=('--dns_bypass' in sys.argv) or ('-dns' in sys.argv), help="Cloudflare zone identifier", type=str)
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
    if args.direct_bypass: 
        bypass_cloudflare_directly(args.url,args.ip)
    elif args.dns_bypass:
        output = get_cf_bypassing_dns_entries(args.cf_token,args.zone_id)
        if (args.output == None):
            writer = csv.writer(sys.stdout)
            writer.writerows(output)
        else:
            if args.output != None:
                with open(args.output, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(output)
    else:
        parser.print_help()
        parser.exit()

if __name__ == "__main__":
    main()