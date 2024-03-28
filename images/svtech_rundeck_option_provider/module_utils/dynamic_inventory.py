#!/opt/.pyenv/versions/automation36/bin/python

import os
import argparse
import json
import BASE_FUNC


class DynamicInventory():
    def __init__(self, ):
        self.data = {}  # All data
        self.inventory = {}  # Ansible Inventory

    def add_inventory_group(self, key):
        """ Method to create group dict """
        host_dict = {'hosts': [], 'vars': {}}
        self.inventory[key] = host_dict
        return

    def add_host(self, group, host):
        """ Helper method to reduce host duplication """
        if group not in self.inventory:
            self.add_inventory_group(group)

        if host not in self.inventory[group]['hosts']:
            self.inventory[group]['hosts'].append(host)
        return

    def build_inventory(self, data={}, hostname_key="", ip_key="", all_vars={}):
        """ Build Ansible inventory """

        self.inventory = {
            'all': {
                'hosts': [],
                'vars': all_vars
            },
            '_meta': {
                'hostvars': {}
            }
        }
        dict_host_vars = {}
        for each in data:
            if each[ip_key] != "127.0.0.1":
                self.inventory['all']['hosts'].append(each[hostname_key])
                dict_host_vars[each[hostname_key]] = each
                dict_host_vars[each[hostname_key]]["ansible_host"] = each[ip_key]

        self.inventory['_meta']['hostvars'] = dict_host_vars

        return self.inventory

    def Init_Arguments(self):
        """ Init Arguments """
        cmdline = argparse.ArgumentParser(description="Dynamic Inventory")
        BASE_FUNC.INIT_LOGGING_ARGS(cmdline)
        cmdline.add_argument('--list', action='store_true',  help='Output all hosts info')
        cmdline.add_argument('--host', action='store', help='Output specific host info')
        cmdline.add_argument('--ip', action='store', help='Input Host IP info')
        cmdline.add_argument('--port', action='store', help='Input Port info')
        args = cmdline.parse_args()
        return args
