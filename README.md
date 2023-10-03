# Cloudflare PurpleTeam Toolkit

This repo contains a collection of tools to perform some security tests, scans and investigations on the established configurations in cloudflare. To keep everything simple, each of them is a small python script with a reduced scope.

The toolkit contains:
1. cf-waf-bypass - try to bypass the WAF on your origin
2. cf-dns-detective - enumerate and investigate dns entries, including the proxy status
3. cf-zt-gateway-detective - search, enumerate and investigate among the Zero Trust Gateway policies

### 1. cf-waf-bypass
This tool tries to bypass cloudflare by accessing directly to the origin server IP. 2 bypasses are currently implemented.

1. direct bypass

Sometimes, cloudflare proxy is enabled for a domain, but there is no actual restriction on the server to prevent traffic from coming directly. When a "normal" user try to reach the service, cloudflare DNS will answer with the IP of its own proxy, and will forward traffic to the origin. But if a bad actor knows the IP address, he can use it directly and hit the server without going threw the cloudflare proxy, and the waf rules. Very often the origin IP can easily be found in archives or search engines such as shodan. The cf-waf-bypass tool attempts to do exactly this bypass, by takin in parameter the url, and the origin ip. It'll print the answer, so that you know if the bypass was successful
```
python3 cf-waf-bypass.py --direct -x GET -url https://my-target.com/foo.php -ip 6.6.6.6
```

1. bypass cloudflare threw cloudflare

TODO
https://certitude.consulting/blog/en/using-cloudflare-to-bypass-cloudflare/

### 2. cf-dns-detective

TODO

### 3. cf-zt-gateway-detective

TODO
