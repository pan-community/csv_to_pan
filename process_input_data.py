#!/usr/bin/env python3

# Example of how to iterate over structured input data and create the appropriate API calls to translate into PAN-OS
# objects and rules
# 070121 - nembery

import json
from skilletlib import SkilletLoader
from skilletlib import Skillet


# Set up our PAN-OS device connection information
# in a real deployment you should keep these are env vars or otherwise inject them in a more secure manor
context = {"device_group": "poc-dg", "ip_address": "10.10.10.10", "username": "admin", "password": "admin"}

# load our input data from a JSON file
with open("input_data.json", "r") as input_file:
    input_data_str = input_file.read()
    input_data = json.loads(input_data_str)

# load all our API tools
sl = SkilletLoader("./skillets")


# create a simple stub function
def get_palo_service_name_for_port(port_name):
    """
    Stub function to return palo service name for a port as defined from the input data. FIXME!

    :param port_name:
    :return: palo specific port names...
    """
    if port_name == "TCP80":
        return "service-http"
    elif port_name == "TCP443":
        return "service-https"

    # failsafe
    return "service-https"


# iterate over each rule in the input data and do all the creation stuff
for r in input_data.get("rules", []):
    source = r.get("source", {})
    dest = r.get("dest", {})
    port = r.get("port", {})
    comment = r.get("comment", "")
    rule_name = r.get("rule_name", "")

    # get the add_address API tool
    add_address: Skillet = sl.get_skillet_with_name("add_address_object")

    # get the add_address_group API tool
    add_address_group: Skillet = sl.get_skillet_with_name("add_address_group")

    # get the source_group_name
    source_group_name = source.get("group_name", "GROUP_1")

    for member in source.get("members", []):
        # copy our context object
        c = context.copy()
        # add tool specific variables
        c["ipv4_address"] = member
        c["ipv4_address_group"] = source_group_name
        # first, build the source address objects for each member
        add_address.execute(c)
        # second, add that member to the address_group
        add_address_group.execute(c)

    dest_group_name = dest.get("group_name", "DEST_GROUP_1")

    for member in dest.get("members", []):
        c = context.copy()
        # add tool specific variables
        c["ipv4_address"] = member
        c["ipv4_address_group"] = dest_group_name
        # first, build the source address objects for each member
        add_address.execute(c)
        # second, add that member to the address_group
        add_address_group.execute(c)

    port_group_name = port.get("group_name", "PORT_GROUP_1")

    # get the add_service_group API tool
    add_service_group: Skillet = sl.get_skillet_with_name("add_service_group")

    service_group_name = port.get("group_name", "SERVICE_GROUP_1")
    for member in port.get("members", []):
        c = context.copy()
        c["service_group"] = service_group_name

        palo_service_name = get_palo_service_name_for_port(member)
        c["service_group_entry"] = palo_service_name

        add_service_group.execute(c)

    add_security_rule = sl.get_skillet_with_name("add_security_rule")

    c = context.copy()
    c["rule_name"] = rule_name
    c["rule_description"] = comment
    c["source_group"] = source_group_name
    c["destination_group"] = dest_group_name

    add_security_rule.execute(c)
