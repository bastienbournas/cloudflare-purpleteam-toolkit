#!/usr/bin/env python

import ipaddr

############################################################################################################
#                                                                                                          #
# cf_purpleteam_toolkit_common.py                                                                          #
#                                                                                                          #
# This module regroups all the common code and helper functions to be shared by the tools.                 #
#                                                                                                          #
############################################################################################################

#
# Check that the fiven string respects the IPv4 format
#
def is_ipv4(string):
    try:
        ipaddr.IPv4Network(string)
        return True
    except ValueError:
        return False