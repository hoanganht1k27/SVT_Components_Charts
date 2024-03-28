#!/opt/.pyenv/versions/automation36/bin/python

from liveStatusWrapper import *
from dynamic_inventory import DynamicInventory
import argparse
import json
import time
import os
import BASE_FUNC
import logging

class IcingaInventory():
    def __init__(self):
        self.data = {}  # All data
        self.inventory = {}  # Ansible Inventory

    def getLivestatusData(self, icinga_host=None, icinga_port=None):
        host_default = "localhost"
        port_default = 6558
        ICINGA_HOST=None
        ICINGA_PORT=None

        # GET Variable from Ansible CLI
        try:
            ICINGA_HOST = os.environ['ICINGA_HOST']
            ICINGA_PORT = os.environ['ICINGA_PORT']
        except:
            pass

        # GET Variable from Ansible Rundeck
        try:
            ICINGA_HOST = os.environ['icinga_host']
            ICINGA_PORT = os.environ['icinga_port']
        except:
            pass

        # icinga_host and icinga_port is variable from Option Provider
        if  icinga_host != None and icinga_port != None:
            host = icinga_host
            port = icinga_port
        elif ICINGA_HOST != None and ICINGA_PORT != None:
            host = ICINGA_HOST
            port = ICINGA_PORT
        else:
            host = host_default
            port = port_default

        hosts_data = getInfos(host, int(port), 'hosts',
                            ['display_name ~ '],
                            'display_name', 'address', 'state', 'state_type', 'groups', 'custom_variable_names', 'custom_variable_values')
        self.data = hosts_data
        return self.data

    def build_inventory(self, icinga_host=None, icinga_port=None):
        """ Build Icinga inventory """
        self.data = self.getLivestatusData(icinga_host, icinga_port)
        for each in self.data:
            each["device_groups"] = each.pop("groups")
        self.inventory = DynamicInventory().build_inventory(data = self.data,
                                                           hostname_key =  "display_name",
                                                           ip_key = "address",
                                                           all_vars = {})
        return self.inventory

if __name__ == '__main__':
    args = DynamicInventory().Init_Arguments()
    log_file = os.path.join(args.log_dir,
                            args.log_prefix + '_' + time.strftime(args.log_timestamp) + '_' + args.log_surfix + '.log')

    BASE_FUNC.LOGGER_INIT(args.log_level, log_file, print_log_init=False, shell_output=False)

    if args.list:
        inventory = IcingaInventory().build_inventory()
        print(json.dumps(inventory))

    if args.host:
        try:
            inventory = IcingaInventory().build_inventory()
            print(json.dumps(inventory['_meta']['hostvars'][args.host]))

        except KeyError:
            print("No host: {}".format(args.host))
            print("Select in list hosts: {}".format(inventory['all']['hosts']))
