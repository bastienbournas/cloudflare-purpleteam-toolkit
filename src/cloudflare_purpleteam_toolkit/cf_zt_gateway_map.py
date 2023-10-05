#!/usr/bin/env python
import sys
import requests
import csv
import argparse
import ipaddr
from cf_purpleteam_toolkit_common import is_ipv4

#
# Use cloudflare's API to retrieve all Gateway policies, filter the results to keep only the essential,
# and return the policies in a CSV ready format.
#
def get_cf_gateway_firewall_policies(cf_account, cf_token):
    gateway_firewall_policies = requests.get('https://api.cloudflare.com/client/v4/accounts/' + cf_account + '/gateway/rules', headers={"Authorization":"Bearer " + cf_token, "Content-Type":"application/json"}).json()['result']
    
    output = []
    output.append(['Type', 'Name', 'Precedence','IP range', 'Identity'])
    for policy in gateway_firewall_policies:
        row = []
        row.append(policy['filters'][0])
        row.append(policy['name'])
        row.append(policy['precedence'])
        traffic = policy['traffic']
        if policy['filters'] == ['l4']:
            traffic = traffic.replace('net.dst.ip in {', '')
            traffic = traffic.replace('}', '')
        row.append(traffic)
        if policy['filters'] == ['dns']:
            override_ips = policy['rule_settings']['override_ips']
            if override_ips:
                row.append(override_ips[0])
            else:
                row.append("No IP Override")      
        
        if policy['identity']:
            row.append(policy['identity'])
        else:
            row.append('Everybody')
        
        output.append(row)

    return output

#
# Search for the given IP (CIDR) into the given gateway policies (retrieved with get_cf_gateway_firewall_policies)
# The given IP can be a single one (6.6.6.6/32), or a range (6.6.6.6/24).
# This the search will output policies that match (eg that cover the range)
#
def policy_search_by_ip(reference_range, policies):
    print("Checking Gateway policies that match " + reference_range)
    ref_ip_range = ipaddr.IPNetwork(reference_range)

    print("Network policies matchs:")
    found = False
    for row in policies:
        if row[0] == 'l4' and is_ipv4(row[3]):
            current_ip_range = ipaddr.IPNetwork(row[3])
            if ref_ip_range.overlaps(current_ip_range):
                found = True
                print(row[1])
    if not found:
        print("None")

    print("DNS policies matchs:")
    found = False
    for row in policies:
        if row[0] == 'dns':
            ip_str = str(row[4]) + "/32"
            if is_ipv4(ip_str):
                current_ip_range = ipaddr.IPNetwork(ip_str)
                if ref_ip_range.overlaps(current_ip_range):
                    found = True
                    print(row[1])
    if not found:
        print("None")

#
# Argument parsing for CLI usage
#
def parse_args():
    parser = argparse.ArgumentParser("cloudflare-zt-gateway-map")
    parser.add_argument("-cfa","--cf_account", required=True, help="Cloudflare account id", type=str)
    parser.add_argument("-cft","--cf_token", required=True, help="Cloudflare Authorization Bearer token", type=str)
    parser.add_argument("-o","--output", required=False, help="Write the Cloudflare Gateway policies to the given file", type=str)
    parser.add_argument("-ip","--ip_range", help="Search for policies that match with the given IP address (CIDR notation)", type=str)
    return parser.parse_args()

#
# Main
#
def main():
    args = parse_args()

    policies = get_cf_gateway_firewall_policies(args.cf_account, args.cf_token)

    if (args.output == None) and (args.ip_range == None):
        writer = csv.writer(sys.stdout)
        writer.writerows(policies)
    else:
        if args.output != None:
            with open(args.output, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(policies)

        if args.ip_range != None:
            policy_search_by_ip(args.ip_range, policies)

if __name__ == "__main__":
    main()