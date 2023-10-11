# Cloudflare PurpleTeam Toolkit

This repo contains a collection of tools to perform some security tests, scans and investigations on the established configurations in cloudflare. To keep everything simple, each of them is a small python script with a reduced scope.

The toolkit contains:
1. cf_waf_bypass.py - try to bypass the WAF on your origin
2. cf_dns_map.py - enumerate dns entries, including the proxy status
3. cf-zt-gateway-map.py - search, enumerate and investigate among the Zero Trust Gateway policies

The cf_purpleteam_toolkit_common.py module regroups all the common code and helper functions to be shared by the different tools.   

### 1. cf_waf_bypass
This tool aims to bypass cloudflare by accessing directly to the origin server IP, escaping the WAF analysis. 3 kind of bypasses are currently implemented.

1. direct bypass

Sometimes, cloudflare proxy is enabled for a domain, but there is no actual restriction on the server to prevent traffic from coming directly. When a "normal" user try to reach the service, cloudflare DNS will answer with the IP of its own proxy, and will forward traffic to the origin. But if a bad actor knows the IP address, he can use it directly and hit the server without going threw the cloudflare proxy, and the waf rules. Very often the origin IP can easily be found in archives or search engines such as shodan. The cf_waf_bypass tool with the --direct_bypass option attempts to do exactly this bypass, by takin in parameter the url, and the origin ip. It'll print the answer, so that you know if the bypass was successful
```
python3 cf_waf_bypass.py --direct_bypass -x GET -url https://my-target.com/foo.php -ip 6.6.6.6
```

2. bypass threw cloudflare DNS misconfiguration

Misconfigurations in cloudflare dns itself can lead to proxied entries bypass. Some example of such misconfigurations are an unproxified CNAME entry pointing to a proxified entry, or a different unproxified entry with same IP as a proxified one. Using the cf_waf_bypass tool with the --dns_bypass option allows to scan all the dns entries threw the cloudflare API, and outputs a list of all the possibles bypasses caused by these misconfigurations. 
The output is in CSV format, each raw containing : ["proxied_type","proxied_name","proxied_content","bypass_type","bypass_name","bypass_content"]. proxied_* represents the attributes of the proxied entry that can be bypassed, and bypass_* represents the attributes of the entry that allows the bypass. When a bypass is found, you can then use --direct_bypass option to actually execute it.
```
python3 cf_waf_bypass.py --dns_bypass -cft CF_API_TOKEN --zid CF_ZONE_ID -o output.csv
```

3. bypass cloudflare threw cloudflare

TODO
https://certitude.consulting/blog/en/using-cloudflare-to-bypass-cloudflare/

### 2. cf_dns_map

Threw cloudflare API, cf_dns_map allows to enumerate dns entries, including the proxy status.
The output is in CSV format, so that it's easy to process. 

List all dns entries with proxy status:
```
python3 cf_dns_map.py -zid CF_ZONE_ID -cft CF_API_TOKEN -o output.csv
```

List proxied dns entries:
```
python3 cf_dns_map.py --proxied -zid CF_ZONE_ID -cft CF_API_TOKEN -o output.csv
```

List unproxied dns entries:
```
python3 cf_dns_map.py --unproxied -zid CF_ZONE_ID -cft CF_API_TOKEN -o output.csv
```

### 3. cf_zt_gateway_map

Navigating threw Cloudflare Gateway policies (DNS, Network, HTTP) in the ui can be hard when there are a lot of them. It is especially hard to find network/dns policies about about a specific IP address. The cf_zt_gateway_map.py tool solves that by relying on cloudflare's API to dump all gateway policies into a CSV format easy to read and process. If the -ip option is given, it will search for policies that match the IP/CIDR. The given IP can be a single one (6.6.6.6/32), or a range (6.6.6.6/24).

Dump all Gateway DNS/Network policies:
```
python3 cf_zt_gateway_map.py -cfa CF_ACCOUNT_ID -cft CF_API_TOKEN -o output.csv
```

Dump all Gateway DNS/Network policies and print policies that match the given IP:
```
python3 cf_zt_gateway_map.py -cfa CF_ACCOUNT_ID -cft CF_API_TOKEN -ip 6.6.6.6/32 -o output.csv
```
