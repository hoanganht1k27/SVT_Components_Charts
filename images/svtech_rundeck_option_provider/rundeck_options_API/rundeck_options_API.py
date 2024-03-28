#!/opt/.pyenv/versions/automation36/bin/python

from flask import Flask, jsonify, request, render_template, redirect, url_for
from influxdb import InfluxDBClient
import json
import os
import sys
import re
import yaml
import logging
import argparse
import configparser
import mysql.connector
import requests
from gevent.pywsgi import WSGIServer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../module_utils')))
from module_utils.IcingaInventory import IcingaInventory
from module_utils.liveStatusWrapper import *
import BASE_FUNC
# BASE_FUNC.LOGGER_INIT("INFO", "./rundeck_option_API.log", print_log_init = False,shell_output= True)
# BASE_FUNC.LOGGER_INIT("INFO", "/dev/null", print_log_init = False,shell_output= True)

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

config = configparser.ConfigParser()
config.read('./config.conf')
config_file = config["Config"]["configuration_file"]
datasource_file = config["Config"]["datasource_file"]

ymlfile = open(config_file, 'r')
cfg = yaml.safe_load(ymlfile)

rundeck_conf_file = config["Config"]["rundeck_conf_file"]

# cfg = yaml.safe_load(ymlfile, Loader=yaml.FullLoader)
# port_flask = cfg["port_flask"]

app = Flask(__name__, static_url_path='/static_upgrade')


def args_parser(request_arg=None):
    dict_arg = {}
    for each in request_arg.items():
        dict_arg[each[0]] = each[1]
    return dict_arg

def has_keys(dict={}, key=None):
    list_key = []
    if isinstance(key, str):
        list_key = [key]
    else:
        list_key = key
    flag = 0
    for k in list_key:
        if k not in dict:
            flag = flag + 1
    if flag == 0:
        return True
    else:
        return False

def sort_result(dict_arg, result):
    if "sort" in dict_arg:
        if dict_arg["sort"] == "asc":
            final_result = sorted(result)
        elif dict_arg["sort"] == "desc":
            final_result = sorted(result, reverse=True)
    else:
        final_result = sorted(result)
    return (final_result)

def getDatasource(type="", regex=None, data=None):
    read_datasource_file = open(datasource_file, 'r')
    datasource = yaml.safe_load(read_datasource_file)
    result = []
    for ds in datasource:
        if ds["type"] == type:
            if regex != None and regex != "":
                filter = re.findall(regex, ds["name"])
                if filter != []:
                    if data != None and data != "":
                        result.append(str(ds[data]))
                    else:
                        result.append(ds)
            else:
                result.append(str(ds[data]))
    return result


@app.route(cfg["api_url_config"]["datasource"]["datasource_query"], methods=["GET"])
def DatasourceQuery():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if "type" in dict_arg:
            if "attribute" in dict_arg and "regex" in dict_arg:
                datasource = getDatasource(type=dict_arg["type"], regex=dict_arg["regex"], data=dict_arg["attribute"])
            else:
                if "regex" in dict_arg:
                    datasource = getDatasource(type=dict_arg["type"], regex=dict_arg["regex"])
                elif "attribute" in dict_arg:
                    datasource = getDatasource(type=dict_arg["type"], data=dict_arg["attribute"])
                else:
                    datasource = getDatasource()

            final_result = sort_result(dict_arg, datasource)
            return jsonify(final_result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")

# START- CONFIG FILE AUDIT
@app.route(cfg["api_url_config"]["file"]["get_list_file_audit"], methods=["GET"])
def getListFileAudit():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if "path" not in dict_arg:
            return jsonify("Require path !")
        if os.path.isfile(dict_arg["path"]):
            return jsonify("Path ERROR. Path must be Directory !")
        if not dict_arg['domain']:
            return jsonify([])
        if not dict_arg['action'] or dict_arg['action']=='UPLOAD':
            return jsonify([])
        domains=dict_arg['domain'].split(",")
        result = []
        for domain in domains:
            subfolder=os.path.join(dict_arg['path'], domain)
            list_file = os.listdir(subfolder)
            if len(list_file)==0:
                continue
            if "regex" in dict_arg:
                r=re.compile(dict_arg["regex"])
                list_file=list(filter(r.match, list_file))
            list_file=[domain+"/"+i for i in list_file]
            result+=list_file
        return jsonify(result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")
# END
# @app.route("/datasource_query/getlistname", methods=["GET"])
# def DatasourceQueryName():
#     dict_arg = args_parser(request_arg=request.args)

#     datasource = getDatasource()
#     list_name = []
#     if "regex" in dict_arg:
#         for ds in datasource:
#             ds_name = re.findall(dict_arg["regex"], ds["name"])
#             if ds_name != []:
#                 list_name.append(ds_name[0])
#     else:
#         for ds in datasource:
#             list_name.append(ds["name"])
#     print(list_name)
#     return jsonify(list_name)


@app.route(cfg["api_url_config"]["influxdb"]["influxdb_query"], methods=["GET"])
def InfluxdbQuery():
    try:
        dict_arg = args_parser(request_arg=request.args)

        if "host" in dict_arg and "port" in dict_arg and "username" in dict_arg and "password" in dict_arg:
            host = dict_arg["host"]
            port = dict_arg["port"]
            username = dict_arg["username"]
            password = dict_arg["password"]

        if "datasource" in dict_arg:
            datasource_name = dict_arg["datasource"]
            if datasource_name != "":
                datasource_data = getDatasource(type="influxdb", regex=datasource_name)[0]

                host = datasource_data["host"]
                port = datasource_data["port"]
                username = datasource_data["username"]
                password = datasource_data["password"]

        database = None
        query = dict_arg["query"]

        if "db" in dict_arg:
            database = dict_arg["db"]
        column_name = ""
        if "column" in dict_arg:
            column_name = dict_arg["column"]

        connection = InfluxDBClient(host=host, port=port, database=database, username=username, password=password)
        result = connection.query(query)
        list_result = []
        for each in result:
            for item in each:
                for key, val in item.items():
                    if column_name != "":
                        if key == column_name:
                            if "regex" in dict_arg:
                                v = re.findall(dict_arg["regex"], val)
                                if v != []:
                                    list_result.append(val)
                            else:
                                list_result.append(val)
                    else:
                        if "regex" in dict_arg:
                            v = re.findall(dict_arg["regex"], val)
                            if v != []:
                                list_result.append(val)
                        else:
                            list_result.append(val)

        final_result = sort_result(dict_arg, list(set(list_result)))
        return jsonify(final_result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")


@app.route(cfg["api_url_config"]["livestatus"]["livestatus_query"], methods=["GET"])
def LiveStatusQuery():
    dict_arg = args_parser(request_arg=request.args)
    result = []
    try:
        if "inventory_name" in dict_arg:
            # [HaDN] - 04/01/2022 - Edit condition to return [] for static inventory
            if "Dynamic" not in dict_arg["inventory_name"]:
                return jsonify("[]")
        if "datasource" in dict_arg:
            datasource_name = dict_arg["datasource"]
            if datasource_name != "":
                datasource_data = getDatasource(type="livestatus", regex=datasource_name)[0]
                logging.info(datasource_data)

                host = datasource_data["host"]
                port = datasource_data["port"]

                if has_keys(dict_arg, ["data_type", "filter", "column"]):
                    filter = []
                    if type(dict_arg["filter"]) is str:
                        filter = [dict_arg["filter"]]
                    elif type(dict_arg["filter"]) is list:
                        pass
                    else:
                        return jsonify("ERROR")

                    column = dict_arg["column"]
                    livestatus_data = getInfos(host, int(port), dict_arg['data_type'], filter, column)

                    for each in livestatus_data:
                        if "regex" in dict_arg:
                            value = re.findall(dict_arg["regex"], each[column])
                            logging.info(value)
                            if value != []:
                                result.append(value[0])
                        else:
                            result.append(each[column])
        result = list(set(result))
        final_result = sort_result(dict_arg, result)
        return jsonify(final_result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")

def LivestatusGetMappingCustomValue(data, key_name, value_name, get_keyname):
    variable_names = data[key_name]
    variable_values = data[value_name]
    for i in range(len(variable_names)):
        if variable_names[i] == get_keyname:
            return variable_values[i]

@app.route(cfg["api_url_config"]["livestatus"]["livestatus_query_custom_values"], methods=["GET"])
def LiveStatusQueryCustom():
    dict_arg = args_parser(request_arg=request.args)
    result = []
    try:
        if "inventory_name" in dict_arg:
            if "Dynamic" not in dict_arg["inventory_name"]:
                return jsonify("[]")
        if "datasource" in dict_arg:
            datasource_name = dict_arg["datasource"]
            if datasource_name != "":
                datasource_data = getDatasource(type="livestatus", regex=datasource_name)[0]
                logging.info(datasource_data)

                host = datasource_data["host"]
                port = datasource_data["port"]

                if has_keys(dict_arg, ["data_type", "filter", "column"]):
                    filter = []
                    if type(dict_arg["filter"]) is str:
                        filter = [dict_arg["filter"]]
                    elif type(dict_arg["filter"]) is list:
                        pass
                    else:
                        return jsonify("ERROR")

                    column = dict_arg["column"]
                    livestatus_data = getInfos(host, int(port), dict_arg['data_type'], filter, 'custom_variable_names', 'custom_variable_values')

                    for data in livestatus_data:
                        value = LivestatusGetMappingCustomValue(data, "custom_variable_names", "custom_variable_values", column)
                        if value :
                            if "regex" in dict_arg:
                                regex = re.findall(dict_arg["regex"], value)
                                if regex != []:
                                    result.append(regex[0])
                            else:
                                result.append(value)
        result = list(set(result))
        final_result = sort_result(dict_arg, result)
        return jsonify(final_result)

    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")

# [HaDN] - 04/01/2022 - Add icinga2_api_query function
@app.route(cfg["api_url_config"]["icinga2"]["icinga2_api_query"], methods=["GET"])
def Icinga2ApiQuery():
    dict_arg = args_parser(request_arg=request.args)
    try:
        final_result = []
        if "inventory_file" in dict_arg and "inventory_name" in dict_arg:
            inventory_file = dict_arg["inventory_file"]
            inventory_name = dict_arg["inventory_name"]
            if inventory_name != "Dynamic_Inventory":
                with open(inventory_file, "r") as file:
                    readline = file.readlines()
                    for line in readline:
                        if "ansible_host" in line and "#" not in line:
                            dict_tmp = {}
                            regex = re.findall(r"(.*)\s*ansible_host=(\w+.\w+.\w+.\w+)", line)
                            name = regex[0][0]
                            ip = regex[0][1]
                            host = name + " - " + ip
                            dict_tmp["name"] = host
                            dict_tmp["value"] = name.replace(" ", "")
                            if "regex" in dict_arg:
                                regex_host = re.findall("(.*" + dict_arg["regex"] + ".*)", host)
                                if regex_host:
                                    final_result.append(dict_tmp)
                            else:
                                final_result.append(dict_tmp)
                logging.info(final_result)
                return jsonify(final_result)

        if "datasource" in dict_arg:
            datasource_name = dict_arg["datasource"]
            if datasource_name != "":
                datasource_data = getDatasource(type="icinga2", regex=datasource_name)[0]

                host = datasource_data["host"]
                port = datasource_data["port"]
                username = datasource_data["username"]
                password = datasource_data["password"]

                # [HaDN] - 22/06/2022 - Add endpoint_type params - START
                if "endpoint_type" not in dict_arg:
                    endpoint_type = "objects"
                else:
                    endpoint_type = dict_arg["endpoint_type"]

                if "data_type" not in dict_arg:
                    return jsonify("Require data_type !")
                if "attr" not in dict_arg:
                    return jsonify("Require attr !")

                data_type = dict_arg["data_type"]
                attribute = dict_arg["attr"].split(",")

                if "filter" in dict_arg:
                    filter = dict_arg["filter"]

                request_url = "https://{}:{}/v1/{}/{}".format(host, port, endpoint_type, data_type)

                headers = {
                    'Accept': 'application/json',
                    'X-HTTP-Method-Override': 'GET'
                }

                if "filter" in dict_arg:
                    data = {
                        "filter": filter,
                        "attrs": attribute
                    }
                else:
                    data = {
                        "attrs": attribute
                    }

                r = requests.get(request_url,
                                headers=headers,
                                auth=(username, password),
                                data=json.dumps(data),
                                verify=False)
                json_result = r.json()
                if 'results' not in json_result:
                    return jsonify("ERROR")

                results = json_result["results"]
                list_attribute = []

                if len(attribute) == 1:
                    for i in results:
                        if "attrs" in i:
                            list_attribute.append(i["attrs"][attribute[0]])
                        else:
                            list_attribute.append(i[attribute[0]])

                    if "regex" in dict_arg:
                        for each in list_attribute:
                            value = re.findall(dict_arg["regex"], each)
                            if value != []:
                                final_result.append(value[0])
                    else:
                        final_result = list_attribute

                    final_result = sorted(final_result)
                else:
                    for i in results:
                        if "attrs" in i:
                            list_attribute.append(i["attrs"])
                        else:
                            list_attribute.append(i)
                    # [HaDN] - 22/06/2022 - Add endpoint_type params - END

                    if "rundeck_option" in dict_arg:
                        if "name_col" in dict_arg:
                            name_col = dict_arg["name_col"].split(",")
                            value_col = dict_arg["value_col"].split(",")

                            for item in list_attribute:
                                if len(name_col) > 1:
                                    name_string = " - ".join([item[i] for i in name_col])
                                else:
                                    name_string = item[name_col[0]]
                                if len(value_col) > 1:
                                    value_string = " - ".join([item[i] for i in value_col])
                                else:
                                    value_string = item[value_col[0]]
                                item["name"] = name_string
                                item["value"] = value_string

                        final_result = list_attribute
                        if "regex" in dict_arg and "regex_col" in dict_arg:
                            regex_result = []
                            for each in list_attribute:
                                value = re.findall(dict_arg["regex"], each[dict_arg["regex_col"]])
                                if value != []:
                                    regex_result.append(each)
                            final_result = regex_result
                    else:
                        final_result = list_attribute

                logging.info(final_result)
        return jsonify(final_result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")


@app.route(cfg["api_url_config"]["mariadb"]["mariadb_query"], methods=["GET"])
def MariadbQuery():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if has_keys(dict_arg, ["host", "port", "username", "password"]):
            host = dict_arg["host"]
            port = dict_arg["port"]
            username = dict_arg["username"]
            password = dict_arg["password"]

        if "datasource" in dict_arg:
            datasource_name = dict_arg["datasource"]
            if datasource_name != "":
                datasource_data = getDatasource(type="mariadb", regex=datasource_name)[0]

                host = datasource_data["host"]
                port = datasource_data["port"]
                username = datasource_data["username"]
                password = datasource_data["password"]

        database = None
        query = dict_arg["query"]

        if "db" in dict_arg:
            database = dict_arg["db"]

        column_name = ""
        if "column" in dict_arg:
            column_name = dict_arg["column"]
        result = []
        conn = mysql.connector.connect( user=username,
                                        password=password,
                                        host=host,
                                        port=port,
                                        database=database)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        query_result = cursor.fetchall()

        logging.info(query_result)

        for each in query_result:
            if column_name != "":
                if "regex" in dict_arg:
                    regex = re.findall(dict_arg["regex"], each[column_name])
                    if regex != []:
                        result.append(regex[0])
                else:
                    result.append(each[column_name])
            else:
                cursor.close()
                conn.close()
                return jsonify("Require Column Name !")

        cursor.close()
        conn.close()
        final_result = sort_result(dict_arg, result)
        logging.info(final_result)
        return jsonify(final_result)

    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")


@app.route(cfg["api_url_config"]["inventory"]["list_inventory"], methods=["GET"])
def getListInventory():
    dict_arg = args_parser(request_arg=request.args)
    try:
        # inventory_path = dict_arg["inventory_path"].decode("utf-8")
        inventory_path = cfg["dir_config"]["inventory"]["static_inventory_path"]
        list_file = os.listdir(inventory_path)
        list_inventory = list_file
        list_inventory_final = []
        list_inventory_final = sorted(list_inventory)
        list_inventory_final.insert(0, "Dynamic_Inventory")
        if "exclude_inventory" in dict_arg:
            if "," in dict_arg["exclude_inventory"]:
                list_exclude = dict_arg["exclude_inventory"].split(",")
            else:
                list_exclude = [dict_arg["exclude_inventory"]]

            for exclude in list_exclude:
                for inventory in list_inventory:
                    regex = re.findall("(.*" + str(exclude) + ".*)", inventory)
                    if regex != []:
                        try:
                            list_inventory_final.remove(regex[0])
                        except:
                            pass

        final_result = sort_result(dict_arg, list_inventory_final)
        logging.info(final_result)
        return jsonify(final_result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")


@app.route(cfg["api_url_config"]["inventory"]["inventory_file"], methods=["GET"])
def get_inventory_file():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if "inventory_name" in dict_arg:
            inventory_name = dict_arg["inventory_name"]
            # static_inventory_file = dict_arg["static_inventory"]
            # dynamic_inventory_file = dict_arg["dynamic_inventory"]
            static_inventory_path = cfg["dir_config"]["inventory"]["static_inventory_path"]
            static_inventory_file = os.path.join(static_inventory_path, inventory_name)
            dynamic_inventory_file = cfg["dir_config"]["inventory"]["dynamic_inventory_file"]

            if "Dynamic" in inventory_name:
                print(dynamic_inventory_file)
                return jsonify([dynamic_inventory_file])
            else:
                print(static_inventory_file)
                return jsonify([static_inventory_file])
        else:
            return jsonify("Require inventory_name !")
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")

## [Collect Juniper Tableview Data] Get list Tableview
@app.route(cfg["api_url_config"]["tableview"]["tableview_name"], methods=["GET"])
def getTableview():
    try:
        junos_tablevew_dir = cfg["dir_config"]["tableview"]["list_tableview"]
        list_file = os.listdir(junos_tablevew_dir)
        Table_view = [i.replace(".yml", "") for i in list_file if ".yml" in i]
        Table_view.sort()
        return jsonify(Table_view)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")
## [Collect Juniper Tableview Data] Get list Datatype
@app.route(cfg["api_url_config"]["tableview"]["data_type"], methods=["GET"])
def getTableviewDatatype():
    dict_arg = args_parser(request_arg=request.args)
    try:
        junos_tablevew_dir = cfg["dir_config"]["tableview"]["list_tableview"]
        if "table_view" in dict_arg:
            table_view = dict_arg["table_view"]
            file = open(junos_tablevew_dir + "/" + str(table_view) + ".yml", "r")
            read_file = file.readlines()
            list_data = []
            filter = os.popen('cat ' + junos_tablevew_dir + "/" + str(table_view) +
                            '.yml  | grep -e "^.*:" | grep -v " \\|^_.*" | sed "s/view://g" | sed "s/Table//g" | sed "s/://g" | grep -v "Sub" ').read()

            data = filter.split("\n")
            if "" in data:
                data.remove("")
            final_result = sort_result(dict_arg, data)
            logging.info(final_result)
            return jsonify(final_result)
        else:
            return jsonify("Require table_view !")
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")
## [Collect Juniper Tableview Data] Get List filtered host
@app.route(cfg["api_url_config"]["inventory"]["host_filter"], methods=["GET"])
def getFilterHost():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if "inventory_name" not in dict_arg:
            return jsonify("Require inventory_name !")
        if "inventory_file" not in dict_arg:
            return jsonify("Require inventory_file !")
        if "filter" not in dict_arg:
            return jsonify("Require filter !")

        inventoy_name = dict_arg["inventory_name"]
        inventory_file = dict_arg["inventory_file"]
        filter = dict_arg["filter"]

        list_filtered_host = []

        if "Dynamic" in inventoy_name:
            if "device_type" not in dict_arg:
                return jsonify("Require device_type !")
            if "state" not in dict_arg:
                return jsonify("Require state !")
            if "model" not in dict_arg:
                return jsonify("Require model !")

            if "icinga_host" not in dict_arg:
                icinga_host = "localhost"
            else:
                icinga_host = dict_arg["icinga_host"]
            if "icinga_port" not in dict_arg:
                icinga_port = 6558
            else:
                icinga_port = dict_arg["icinga_port"]

            Dynamic_inventory = IcingaInventory().build_inventory(icinga_host, icinga_port)
            list_host_vars = Dynamic_inventory["_meta"]["hostvars"]

            list_device_type_all = []
            list_model_all = []
            list_state_all = ["UP", "DOWN", "UNREACHABLE"]
            for host in list_host_vars:
                host_vars = list_host_vars[host]
                device_type = LivestatusGetMappingCustomValue(host_vars, "custom_variable_names", "custom_variable_values", "device_type")
                model = LivestatusGetMappingCustomValue(host_vars, "custom_variable_names", "custom_variable_values", "model")
                if device_type not in list_device_type_all:
                    list_device_type_all.append(device_type)
                if model not in list_model_all:
                    list_model_all.append(model)


            if dict_arg["device_type"].lower() == "all":
                list_device_type_filter = list_device_type_all
            else:
                list_device_type_filter = dict_arg["device_type"].split(",")

            if  dict_arg["model"].lower() == "all":
                list_model_filter = list_model_all
            else:
                list_model_filter = dict_arg["model"].split(",")

            if  dict_arg["state"].lower() == "all":
                list_state_filter = list_state_all
            else:
                list_state_filter = dict_arg["state"].split(",")

            for host in list_host_vars:
                host_vars = list_host_vars[host]
                state = ""
                state_index = host_vars["state"]
                if state_index == 0:
                    state = "UP"
                elif state_index == 1:
                    state = "DOWN"
                elif state_index == 2:
                    state = "UNREACHABLE"
                dict_tmp = {}
                dict_tmp["value"] = host_vars["display_name"]
                dict_tmp["name"] = "{} - {} - {}".format(host_vars["display_name"], host_vars["address"], state)
                device_type = LivestatusGetMappingCustomValue(host_vars, "custom_variable_names", "custom_variable_values", "device_type")
                model = LivestatusGetMappingCustomValue(host_vars, "custom_variable_names", "custom_variable_values", "model")

                if device_type in list_device_type_filter and model in list_model_filter and state in list_state_filter:
                    # [HaDN] - 04/01/2022 - Edit host -> dict_tmp["name"]
                    regex_host = re.findall("(.*" + filter + ".*)", dict_tmp["name"])
                    if regex_host:
                        list_filtered_host.append(dict_tmp)

        else:
            with open(inventory_file, "r") as file:
                readline = file.readlines()
                for line in readline:
                    if "ansible_host" in line and "#" not in line:
                        dict_tmp = {}
                        regex = re.findall(r"(.*)\s*ansible_host=(\w+.\w+.\w+.\w+)", line)
                        name = regex[0][0]
                        ip = regex[0][1]
                        host = name + " - " + ip
                        dict_tmp["name"] = host
                        dict_tmp["value"] = name.replace(" ", "")
                        regex_host = re.findall("(.*" + filter + ".*)", host)
                        if regex_host:
                            list_filtered_host.append(dict_tmp)
        # data = list_filtered_host
        data = sorted(list_filtered_host, key = lambda i: i['value']) 
        logging.info(data)
        return jsonify(data)
    except Exception as e:
        logging.error(e)
        return jsonify("[]")

@app.route(cfg["api_url_config"]["file"]["get_list_file"], methods=["GET"])
def getListFile():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if "path" not in dict_arg:
            return jsonify("Require path !")
        # if "type" not in dict_arg:
        #     return jsonify("Require type !")
        if os.path.isfile(dict_arg["path"]):
            return jsonify("Path ERROR. Path must be Directory !")
        result = []
        list_file = os.listdir(dict_arg["path"])
        if "type" in dict_arg:
            if dict_arg["type"] == "file":
                for each in list_file:
                    file_full = os.path.join(dict_arg["path"], each)
                    if os.path.isfile(file_full):
                        if "regex" in dict_arg:
                            regex = re.findall(dict_arg["regex"], each)
                            if regex != []:
                                result.append(regex[0])
                        else:
                            result.append(each)
            elif dict_arg["type"] == "dir":
                for each in list_file:
                    file_full = os.path.join(dict_arg["path"], each)
                    if os.path.isdir(file_full):
                        if "regex" in dict_arg:
                            regex = re.findall(dict_arg["regex"], each)
                            if regex != []:
                                result.append(regex[0])
                        else:
                            result.append(each)
        else:
            for each in list_file:
                if "regex" in dict_arg:
                    regex = re.findall(dict_arg["regex"], each)
                    if regex != []:
                        result.append(regex[0])
                else:
                    result.append(each)

        final_result = sort_result(dict_arg, result)

        logging.info(final_result)
        return jsonify(final_result)

    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")

from functools import reduce
def get_nested_item(data, keys):
    return reduce(lambda seq, key: seq[key], keys, data)

@app.route(cfg["api_url_config"]["dir_config"]["get_dir_config"], methods=["GET"])
def getDirConfig():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if "path" not in dict_arg:
            return jsonify("Require path !")

        get_items = dict_arg["path"].split(".")

        full_result = get_nested_item(cfg, get_items)
        result = []
        logging.info(full_result)

        if isinstance(full_result, dict):
            if "type" not in dict_arg:
                result = full_result
            else:
                for key, value in full_result.items():
                    if dict_arg["type"] == "key":
                        result.append(key)
                    elif dict_arg["type"] == "value":
                        result.append(value)

        elif isinstance(full_result, str):
            result = [full_result]

        elif isinstance(full_result, list):
            result = full_result

        logging.info(result)
        return jsonify(result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")

@app.route(cfg["api_url_config"]["file"]["get_file_content"], methods=["GET"])
def getContentInFile():
    dict_arg = args_parser(request_arg=request.args)
    try:
        if "path" not in dict_arg:
            return jsonify("Require path !")
        if "regex_line" not in dict_arg:
            return jsonify("Require regex_line !")
        if "regex_text" not in dict_arg:
            return jsonify("Require regex_text !")
        path = dict_arg["path"]
        result = []
        with open(path, "r") as file:
            # [HaDN] - 22/04/2022 - Add regex_block option for get_file_content
            if "regex_block" in dict_arg:
                readfile = file.read()
                regex_block = re.findall(dict_arg["regex_block"], readfile)
                if regex_block != []:
                    for block in regex_block:
                        for line in block.split("\n"):
                            regex_line = re.findall(dict_arg["regex_line"], line)
                            if regex_line != []:
                                regex_text = re.findall(dict_arg["regex_text"], regex_line[0])
                                if regex_text != []:
                                    result.append(regex_text[0].strip())
            else:
                readline = file.readlines()
                for line in readline:
                    if ";" not in line and "#" not in line:
                        # regex_line = re.findall(r"(\[backend_.*\])", line)
                        regex_line = re.findall(dict_arg["regex_line"], line)
                        if regex_line != []:
                            regex_text = re.findall(dict_arg["regex_text"], regex_line[0])
                            if regex_text != []:
                                result.append(regex_text[0].strip())
        logging.info(result)
        return jsonify(result)
    except Exception as e:
        logging.error(e)
        return jsonify("ERROR")


@app.route("/upgrade_status/<device_name>/start", methods=["GET","POST"])
def user_confirm_start(device_name):
    current_path = os.getcwd()
    data_path = os.path.join(current_path, "data/")
    list_file = os.listdir(data_path)

    if request.method == 'POST':
        if device_name + ".json" not in list_file :
            data = {}
            data["device"] = device_name
            data["user_confirm"] = "PENDING"
            with open(data_path + device_name + ".json", "w") as file:
                json.dump(data, file, indent=4)
            return jsonify(data)
        else:
            with open(data_path + device_name + ".json", "r") as file:
                data = json.load(file)
            return jsonify(data)
    elif request.method == 'GET':
        return '', 404

@app.route("/upgrade_status/<device_name>/user_confirm", methods=["GET","POST"])
def user_confirm(device_name):

    current_path = os.getcwd()
    data_path = os.path.join(current_path, "data/")
    list_file = os.listdir(data_path)

    if request.method == 'GET':
        if device_name + ".json" in list_file :
            # data = {}
            # data["device"] = device_name
            # data["user_confirm"] = "PENDING"
            # with open(data_path + device_name + ".json", "w") as file:
            #     json.dump(data, file, indent=4)
            # return jsonify(data)
        # else:
            with open(data_path + device_name + ".json", "r") as file:
                data = json.load(file)
            return jsonify(data)
        else:
            return '', 404

    if request.method == 'POST':
        print(request.data)
        receive_data = json.loads(request.data)["user_confirm"]
        data = {}
        data["device"] = device_name
        if device_name + ".json" in list_file :
            if receive_data == "TRUE":
                data["user_confirm"] = "TRUE"
            elif receive_data == "FALSE":
                data["user_confirm"] = "FALSE"
            else:
                data["user_confirm"] = "PENDING"
                return '', 404
            with open(data_path + device_name + ".json", "w") as file:
                json.dump(data, file, indent=4)
                return '', 204
        else:
            return '', 404


@app.route("/upgrade_status/<device_name>/stop", methods=["GET","POST"])
def user_confirm_done(device_name):

    current_path = os.getcwd()
    data_path = os.path.join(current_path, "data/")
    list_file = os.listdir(data_path)

    if request.method == 'POST':
        # receive_data = json.loads(request.data)["user_confirm"]
        # data = {}
        # data["device"] = device_name
        # data["user_confirm"] = "DONE"
        os.system("rm -f {}{}.json".format(data_path, device_name))
        return "Done"
        # with open(data_path + device_name + ".json", "w") as file:
        #     json.dump(data, file, indent=4)
        #     return '', 204
    elif request.method == 'GET':
        return '', 404



@app.route("/upgrade_status/<device_name>/status", methods=["GET","POST"])
def status(device_name):
    return render_template('status.html')


@app.route("/list_user", methods=["GET","POST"])
def list_user():
    # request_arg = request.args
    list_user = []
    conf_file = open(rundeck_conf_file, 'r')
    readlines = conf_file.readlines()
    for line in readlines:
        if ":" in line and "#" not in line:
            split_line = line.split(",")
            user_and_pass = split_line[0]
            user = user_and_pass.split(":")[0]
            list_user.append(user)
    conf_file.close()
    print(list_user)
    return jsonify(list_user)


@app.route("/get_icinga_applied_config", methods=["GET","POST"])
def get_icinga_applied_config():
    dict_arg = {}
    request_arg = request.args
    for each in request_arg.items():
        dict_arg[each[0]] = each[1]

    action = dict_arg['action']
    config_file_path = dict_arg['config_file_path']
    config_file = dict_arg['config_file']
    if action != "Add":
        list_apply_line = []
        with open("{}/{}".format(config_file_path, config_file), 'r') as read_conf_file:
            readlines = read_conf_file.readlines()

        for line in readlines:
            if ("assign" in line or "ignore" in line) and "block" not in line:
                list_apply_line.append(line.strip())

        print(list_apply_line)
        return jsonify(list_apply_line)
    else:
        return jsonify("[]")


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    cmdline = argparse.ArgumentParser(description="Rundeck options API")
    cmdline.add_argument("-p", help="port", nargs='?', type=str, default="1111")
    args = cmdline.parse_args()
    # app.run(host="0.0.0.0",port=args.p, debug=True)
    http_server = WSGIServer(('', int(args.p)), app, log=logger)
    http_server.serve_forever()