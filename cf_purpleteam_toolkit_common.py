#!/usr/bin/env python

import ipaddr

def is_ipv4(string):
    try:
        ipaddr.IPv4Network(string)
        return True
    except ValueError:
        return False