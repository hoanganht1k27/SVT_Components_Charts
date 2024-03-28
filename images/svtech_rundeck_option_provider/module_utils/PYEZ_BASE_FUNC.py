from .BASE_FUNC import *#need the bloody . to work on WinPython
import os
import sys
import ast
import logging
from lxml import etree

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


hardware_xpath_dict = dict(ChassisInventory  =  "//chassis/chassis-module",
                       Midplane  =  "//chassis/chassis-module[starts-with(name,'Midplane')]",
                       RoutingEngine  =  "//chassis/chassis-module[starts-with(name,'Routing Engine')]",
                       CB  =  "//chassis/chassis-module[starts-with(name,'CB')]",
                       PEM  =  "//chassis/chassis-module[starts-with(name,'PEM')]",
                       PDM =  "//chassis/chassis-module[starts-with(name,'PDM')]",
                       FPM  =  "//chassis/chassis-module[starts-with(name,'FPM')]",
                       FanTray  =  "//chassis/chassis-module[starts-with(name,'Fan Tray')]",
                       FPC  =  "//chassis/chassis-module[starts-with(name,'FPC')]",
                       MIC  =  ".//name[starts-with(.,'MIC')]/parent  =    =  *",
                       PIC  =  ".//name[starts-with(.,'PIC')]/parent  =    =  *",
                       PortModule  =  ".//name[starts-with(.,'Xcvr')]/parent  =    =  *"
                   )

#data_format_dict = dict( PYEZ_TABLEVIEW_TO_LIST = () "LIST", "List", "list"],
#                         PYEZ_TABLEVIEW_TO_DICT = [ "Dict", "DICT", "dict","dictionary"],
#                         PYEZ_TABLEVIEW_TO_LIST_OF_DICT= [ "list_of_dict", "List_of_dict", "LIST_OF_DICT"],
#                         PYEZ_TABLEVIEW_TO_JSON = [ "JSON", "json", "Json"],
#                         PYEZ_TABLEVIEW_TO_XML = [ "XML", "Xml", "xml"],
#                         PYEZ_TABLEVIEW_TO_DATAFRAME = [ "CSV", "csv", "Csv"],
#                         GET_PYEZ_TABLEVIEW_RAW = [ "TABLEVIEW", "tableview", "Tableview", "Tableview","raw"]
#                        )

#data_format_dict =     {
#                         ( "LIST", "List", "list") : {
#                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_LIST",
#                                                    "write_func" : "WRITE_PY_STRUCT_TO_FILE"},
#
#                         ( "Dict", "DICT", "dict","dictionary") : {
#                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_DICT",
#                                                    "write_func" : "WRITE_PY_STRUCT_TO_FILE"},
#
#                         ( "list_of_dict", "List_of_dict", "LIST_OF_DICT") : {
#                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_LIST_OF_DICT",
#                                                    "write_func" : "WRITE_PY_STRUCT_TO_FILE"},
#
#                         ( "JSON", "json", "Json") : {
#                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_JSON",
#                                                    "write_func" : "WRITE_JSON_TO_FILE",
#                                                    },
#                         ( "XML", "Xml", "xml") : {
#                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_XML",
#                                                    "write_func" : "WRITE_XML_TO_FILE"},
#
#                         ( "CSV", "csv", "Csv", "xsl", "Xls", "XLS", "Dataframe", "DATAFRAME", "dataframe") : {
#                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_DATAFRAME",
#                                                    "write_func" : "WRITE_DATAFRAME_TO_FILE"},
#                         #                           "convert_func" : "GET_PYEZ_TABLEVIEW_RAW",
#                         #                           "write_func" : "PYEZ_TABLEVIEW_TO_CSV"},
#
#                         ( "TABLEVIEW", "tableview", "Tableview", "Tableview","raw"): {
#                                                    "convert_func" : "GET_PYEZ_TABLEVIEW_RAW",
#                                                    #"write_func" : "WRITE_PYEZ_TABLEVIEW_RAW"}, #TODO
#                                                    "write_func" : "WRITE_PY_STRUCT_TO_FILE"},
#                        }

data_format_dict =     {
                         "list" : {   "format_names":( "list", "python list"),
                                             "convert_func" : "PYEZ_TABLEVIEW_TO_LIST",
                                             "write_func" : "WRITE_PY_STRUCT_TO_FILE"},

                         "dict" : {    "format_names": ( "dict","dictionary"),
                                              "convert_func" : "PYEZ_TABLEVIEW_TO_DICT",
                                              "write_func" : "WRITE_PY_STRUCT_TO_FILE"},

                          "list_of_dict": { "format_names": ( "list_of_dict", "list of dict"),
                                                   "convert_func" : "PYEZ_TABLEVIEW_TO_LIST_OF_DICT",
                                                   "write_func" : "WRITE_PY_STRUCT_TO_FILE"},

                          "json" : { "format_names": ( "json"),
                                            "convert_func" : "PYEZ_TABLEVIEW_TO_JSON",
                                            "write_func" : "WRITE_JSON_TO_FILE",},

                          "xml" : { "format_names": ( "xml"),
                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_XML",
                                                    "write_func" : "WRITE_XML_TO_FILE"},

                          "csv" : { "format_names" : (  "csv",  "xls" , "excel", "dataframe"),
                                                    "convert_func" : "PYEZ_TABLEVIEW_TO_DATAFRAME",
                                                    "write_func" : "WRITE_DATAFRAME_TO_FILE"},
                         #                           "convert_func" : "GET_PYEZ_TABLEVIEW_RAW",
                         #                           "write_func" : "PYEZ_TABLEVIEW_TO_CSV"},

                         "tableview": { "format_names" : (  "tableview", "raw"),
                                                    "convert_func" : "GET_PYEZ_TABLEVIEW_RAW",
                                                    #"write_func" : "WRITE_PYEZ_TABLEVIEW_RAW"}, #TODO
                                                    "write_func" : "WRITE_PY_STRUCT_TO_FILE"},
                        }


try:
    logging.debug("Testing if importing pandas is possible")
    import pandas
except Exception as e:
    logging.warning("Failed to import pandas due to {}, using csv-based functions".format(e))
    data_format_dict["csv"]["convert_func"] = "GET_PYEZ_TABLEVIEW_RAW"
    data_format_dict["csv"]["write_func"] = "PYEZ_TABLEVIEW_TO_CSV"

def PYEZ_CONNECTION_ARGS_INIT(parser):
    # ===================================================CONNECTION PARAMETER=======================================================

    connection_options = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
         "PyEZ connection Options",
         "Customize the options to connect to Junos device"
    )
    connection_options.add_argument( '-ha',
                         '--host_address',
                         dest = "host_address",
                         type=str,
                         default = None,
                         help='One single address of device to connect, not required if host_list or host_file is provided')

    connection_options.add_argument( '-p',
                         '--port',
                         dest = "port",
                         type=str,
                         default="830",
                         help='Netconf port number to be user ')

    connection_options.add_argument('-u',
                        '--username',
                        dest = "username",
                        type=str,
                        help='username to authenticate')

    connection_options.add_argument('-pw',
                        '--password',
                        dest = "password",
                        type=str,
                        help='password to authenticate')

    connection_options.add_argument('-cm',
                        '--console_connection_mode',
                        dest = "console_connection_mode",
                        choices = [ 'telnet' , 'serial'] ,
                        type=str,
                        help='Mode of connection in case netconf over ssh is not available, choose between telnet/serial')

    connection_options.add_argument('-rt',
                        '--rpc_timeout',
                        dest = "rpc_timeout",
                        type=int,
                        default=30,
                        help='Timeout while wait for rpc response, default to 30sec to follow PyEZ predefined value')

def TABLEVIEW_ARGS_INIT(parser):
    tableview_options = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
        "PyEZ tablview data definition Options",
        "Customize the options to access the PyEZ tableview data definition",
    )
    if "win" in sys.platform.lower():
        tableview_options.add_argument('-tb',
                                       '--tableview_file',
                                       dest = "tableview_file",
                                       type = str ,
                                       #required = True,
                                       widget = 'FileChooser',
                                       help='Tableview file use to lookup data definition ')
    else:
        tableview_options.add_argument('-tb',
                                       '--tableview_file',
                                       dest = "tableview_file",
                                       type = str ,
                                       #required = True,
                                       help='Tableview file use to lookup data definition ')

    tableview_options.add_argument('-d',
                                   '--data_type',
                                   dest = "data_type",
                                   type = str ,
                                   #required = True,
                                   help='Data type to be fetched ')


    tableview_options.add_argument('-rk',
                                   '--rpc_kwargs',
                                   dest = "rpc_kwargs",
                                   type = ast.literal_eval ,
                                   default = None,
                                   help='dictionary contain arguments for the rpc ')

    # ===================================================OUTPUT PARAMETER=======================================================
    tableview_output_options = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
         "PyEZ tableview output Options",
         "Customize the options to convert the PyEZ tableview to desired format"
    )
    global data_format_dict
    output_choices = []
    for keyword,value in data_format_dict.items():
        output_choices.append(keyword)

    tableview_output_options.add_argument( '-of',
                        '--output_format',
                        dest = "output_format",
                        type = str ,
                        default = 'list_of_dict',
                        choices = output_choices,
                        help='format of the output data ')

    tableview_output_options.add_argument( '-oty',
                        '--output_type',
                        dest = "output_type",
                        type = str ,
                        default = 'object',
                        choices = ['object','pipeline','file'],
                        help='where to return the formatted data')


def PYEZ_TABLEVIEW_TO_LIST( dev=None,
                            tableview_obj=None,
                            include_hostname=False):
    # type  =   (tableview_obj) -> PyEZTableView
    """Recursively expand any table items"""

    try:
        import jnpr.junos.factory.optable as TableModule
        if not isinstance(tableview_obj, TableModule.Table):
            logging.warning("This function need a PyEZ table data, invalid type [ {} ] provided, exiting".format(type(tableview_obj)))
            logging.debug("Received adata is {}".format(tableview_obj))
            return CRITICAL

        listdata = []
        # data.items() is a list of tuples
        data_items = tableview_obj.items()
        if len(data_items) == 0:
            logging.warning("Sub tableview is empty, filling value None to avoid error during subsequent data conversion")
            return 'Nothing'

    except Exception as e:
        logging.error("Failed to initiate list to convert tableview data of [ {} ], due to: [ {} ]".format(tableview_obj.hostname,e))
        return CRITICAL

    logging.info ("Converting tableview data of [ {} ] to pure list".format(tableview_obj.hostname))
    for table_key, table_fields in data_items:
        temp = []
        try:
            for key, value in table_fields:
                # calling it normalized value because we created the keys
                if value and isinstance(value, TableModule.Table):
                    if dev != None:
                        value = PYEZ_TABLEVIEW_TO_LIST(dev=dev, tableview_obj=value, include_hostname=False) #only allow include_hostname at first call, do not allow during recursion
                    else:
                        value = PYEZ_TABLEVIEW_TO_LIST( value, include_hostname=False) #only allow include_hostname at first call, do not allow during recursion

                # default behavior will be converting tuple to list for json and dataframe handling, add if later
                temp.append([str(key), value])

            # Hostname for json and dataframe later
            if include_hostname == True:
                # temp.append(["hostname", format(tableview_obj.hostname)])
                temp.append(["address", format(tableview_obj.hostname)])
                temp.append(["hostname", format(dev.facts['hostname'])])

                logging.debug("Appended hostname [ {} ] into converted data ".format(tableview_obj.hostname))

            #appending to list as a list of 2 item
            logging.debug("Converted value [ {} ]".format(temp) )
            listdata.append([table_key, temp])

        except Exception as e:
            logging.error("Failed to convert tableview data  [ {} ] to list, due to: [ {} ]".format(tableview_obj,e))
            return CRITICAL
    return listdata


def PYEZ_TABLEVIEW_TO_LIST_OF_DICT( dev=None,
                                    tableview_obj=None,
                                    include_hostname=False):
    # type  =   (tableview_obj) -> PyEZTableView
    """Recursively convert Juniper PyEZ Table/View items to list of dicts."""
    try:
        import jnpr.junos.factory.optable as TableModule
        if not isinstance(tableview_obj, TableModule.Table):
            logging.warning("This function need a PyEZ table data, invalid type [ {} ] provided, exiting".format(type(tableview_obj)))
            logging.debug("Received adata is {}".format(tableview_obj))
            return CRITICAL

        listdata = []
        # data.items() is a list of tuples
        data_items = tableview_obj.items()
        if len(data_items) == 0:
            logging.warning("Sub tableview is empty, filling value None to avoid error during subsequent data conversion")
            return 'Nothing'

    except Exception as e:
        logging.error("Failed to initiate list to convert tableview data of [ {} ], due to: [ {} ]".format(tableview_obj.hostname,e))
        return CRITICAL


    for table_key, table_fields in data_items:
        temp = {}
        try:
            for key, value in table_fields:
                if value and isinstance(value, TableModule.Table):
                    if dev != None:
                        value = PYEZ_TABLEVIEW_TO_LIST_OF_DICT(dev=dev, tableview_obj=value, include_hostname=include_hostname) #only allow include_hostname at first call, do not allow during recursion
                    else:
                        value = PYEZ_TABLEVIEW_TO_LIST_OF_DICT(tableview_obj=value, include_hostname=include_hostname) #only allow include_hostname at first call, do not allow during recursion

                # default behavior will be converting tuple to list for json and dataframe handling
                temp[str(key)] = value
                temp['tableview_key'] = str(table_key) #store it inside field dict instead of outside
                # Hostname for json and dataframe later
            if include_hostname == True:
                logging.info ("Converting tableview data of [ {} ] to a list of dict".format(tableview_obj.hostname))
                if dev != None:
                    temp["hostname"] = format(dev.facts['hostname'])
                temp["address"] = format(tableview_obj.hostname)

                logging.debug("Appended hostname [ {} ] into converted data ".format(tableview_obj.hostname))

            logging.debug("Converted value [ {} ]".format(temp) )
            listdata.append(temp)
        except Exception as e:
            logging.error("Failed to convert tableview data [ {} ] to list of dict, due to: [ {} ]".format(tableview_obj,e))
            return CRITICAL
    return listdata

def PYEZ_TABLEVIEW_TO_DICT( dev=None,
                            tableview_obj=None,
                            include_hostname=False):
    # type  =   (tableview_obj) -> PyEZTableView
    """Recursively convert Juniper PyEZ Table/View items to list of dicts."""
    try:
        import jnpr.junos.factory.optable as TableModule
        if not isinstance(tableview_obj, TableModule.Table):
            logging.warning("This function need a PyEZ table data, invalid type [ {} ] provided, exiting".format(type(tableview_obj)))
            logging.debug("Received adata is {}".format(tableview_obj))
            return CRITICAL

        dictdata = {}
        # data.items() is a list of tuples
        data_items = tableview_obj.items()
        if len(data_items) == 0:
            logging.warning("Sub tableview is empty, filling value None to avoid error during subsequent data conversion")
            return 'Nothing'

    except Exception as e:
        logging.error("Failed to initiate list to convert tableview data of [ {} ], due to: [ {} ]".format(tableview_obj.hostname,e))
        return CRITICAL


    logging.info ("Converting tableview data of [ {} ] to a pure dict".format(tableview_obj.hostname))
    for table_key, table_fields in data_items:
        temp = {}
        try:
            for key, value in table_fields:
                if isinstance(value, TableModule.Table):
                    if dev != None:
                        value = PYEZ_TABLEVIEW_TO_DICT(dev=dev, tableview_obj=value, include_hostname=include_hostname) #only allow include_hostname at first call, do not allow during recursion
                    else:
                        value = PYEZ_TABLEVIEW_TO_DICT(tableview_obj=value, include_hostname=include_hostname) #only allow include_hostname at first call, do not allow during recursion

                # default behavior will be converting tuple to list for json and dataframe handling
                temp[str(key)] = value
            # Hostname for json and dataframe later
            if include_hostname == True:
                # temp["hostname"] = format(tableview_obj.hostname)
                temp["address"] = format(tableview_obj.hostname)
                temp["hostname"] = format(dev.facts['hostname'])

                logging.debug("Appended hostname [ {} ] into converted data ".format(tableview_obj.hostname))

            logging.debug("Converted value [ {} ]".format(temp) )
            dictdata[str(table_key)] = temp
        except Exception as e:
            logging.error("Failed to convert tableview data  [ {} ] to pure dict, due to: [ {} ]".format(tableview_obj,e))
            return CRITICAL
    return dictdata

def PYEZ_TABLEVIEW_TO_DATAFRAME(dev=None,
                                tableview_obj=None,
                                include_hostname=False):
    # type  =   (tableview_obj) -> PyEZTableView
    # type  =   (output_filename) -> str
    """Recursively convert Juniper PyEZ Table/View items to list of dicts, then to dataframe"""
    from pandas import DataFrame
    if dev != None:
        data_list = PYEZ_TABLEVIEW_TO_LIST_OF_DICT(dev=dev, tableview_obj=tableview_obj,include_hostname=include_hostname)
    else:
        data_list = PYEZ_TABLEVIEW_TO_LIST_OF_DICT(tableview_obj=tableview_obj,include_hostname=include_hostname)

    if data_list == CRITICAL or data_list == WARNING or data_list is None:
        logging.warning("Table data of [ {} ] was not converted to list of dict, dataframe will not be created, exit code for conversion was [ {} ]".format(tableview_obj.hostname,data_list))
        return WARNING

    try:
        logging.info("Converting from PyEZ table [ {} ] > list_of_dict > dataframe".format(tableview_obj))
        dataframe = DataFrame(data_list)
    except Exception as e:
        logging.error("Failed to convert table data [ {} ] to dataframe due to [ {} ]".format(tableview_obj,e))
        return CRITICAL

    return dataframe


def PYEZ_TABLEVIEW_TO_JSON( dev=None,
                            tableview_obj=None,
                            include_hostname=False):
    # type  =   (tableview_obj) -> PyEZTableView
    # type  =   (output_filename) -> str
    """Recursively convert Juniper PyEZ Table/View items to list of dicts, then to json, because the default to_json from Juniper is stupid"""
    if dev != None:
        data_dict = PYEZ_TABLEVIEW_TO_DICT(dev=dev, tableview_obj=tableview_obj,include_hostname=include_hostname)
    else:
        data_dict = PYEZ_TABLEVIEW_TO_DICT(tableview_obj=tableview_obj, include_hostname=include_hostname)

    import jnpr.junos.factory.optable as TableModule
    if data_dict == CRITICAL or data_dict == WARNING:
        logging.warning("Table data of [ {} ] was not converted to dict, json will not be written, exit code for conversion was [ {} ]".format(tableview_obj.hostname,data_dict))
        return WARNING

    try:
        logging.info("Converting from PyEZ table  [ {} ] > list_of_dict > json".format(tableview_obj))
        import json
        return json.dumps( data_dict,
                           indent=4,
                           sort_keys=True,
                           ensure_ascii=False)
        #with open(output_filename, 'wb') as output_file:
        #    json.dump(data_dict,output_file,indent=4, sort_keys=True)
        #logging.info("All data successfully written to " + str(output_filename) )
    except Exception as e:
        logging.error("Failed to write tableview data of [ {} ] to json due to [ {} ]".format(tableview_obj.hostname,e))
        return CRITICAL


def PYEZ_TABLEVIEW_TO_XML(dev=None,
                          tableview_obj=None,
                          include_hostname=False):
    # type  =   (tableview_obj) -> PyEZTableView
    """Simply prettify xml output of table data"""

    if len(tableview_obj.items()) == 0:
        logging.warning("Table data item list of [ {} ] is empty, the result xml may contain error or the tableview definition is wrong!!".format(tableview_obj.hostname))

    try:
        logging.info("Converting from PyEZ tableview of host [ {} ] > prettified xml".format(tableview_obj.hostname))
        xml_result = etree.tostring(tableview_obj.xml, pretty_print=True)
        logging.debug("Result prettified xml for host {} is {}".format(tableview_obj.hostname,xml_result))
    except Exception as e:
        logging.error("Failed to convert tableview  [ {} ] to xml due to [ {} ]".format(tableview_obj,e))
        return CRITICAL

    return xml_result


def IMPORT_JUNOS_TABLE_VIEW(TableviewFile):

    if TableviewFile is None:
        logging.warning("Received custom table filename is None, nothing will be imported")
        return WARNING
    elif os.path.isfile(TableviewFile):
        from jnpr.junos.factory.factory_loader import FactoryLoader
        import yaml

        try:
            logging.info("Importing JunosPyEZ custom tableview file [ {} ]".format(TableviewFile))
            with open(TableviewFile, 'r') as TableView:
                tableview_namespace = FactoryLoader().load(yaml.safe_load(TableView))
            return tableview_namespace
        except Exception as e:
            logging.error ( "Error during custom tableview import due to  [ {} ]".format(e))
            logging.exception("Full traceback is here")
            return CRITICAL
    else:
        logging.warning("Table view file {} not found, table will not be imported !!".format(TableviewFile))
        return CRITICAL

def GET_PYEZ_TABLEVIEW_RAW(dev=None,
                           data_type=None,
                           tableview_file=None,
                           kwargs=None):
    #""" get information of junos device into a list of tableview item"""
    #type  =   dev -> junos.jnpr Device
    #type  =   data_type -> string
    #type  =   tableview_file -> string
    #type  =   kwargs -> dict


    TableviewList = IMPORT_JUNOS_TABLE_VIEW(tableview_file)
    if TableviewList == CRITICAL or TableviewList == WARNING:
        logging.error ( "Error during custom tableview import, data will not be fetched")
        return CRITICAL

    else:
        try:
            #if tablename is None and data_type is not None:
            #    tablename = data_type + "Table"
            #    logging.debug("Table name was not provided, using constructed table name " + str(tablename))
            #else:
            #    logging.warning("data type or table name was not provided, no information will be fetched!!")
            #    return WARNING

            tablename =   "{}Table".format(data_type)
            #if TableviewList.has_key(tablename): #only available in python 2
            if tablename in TableviewList:
                logging.info("Found table named [ {} ] in the provided tableview file, getting data".format(tablename))

                #Tu.doan 20/06/2019: Do not open/close socket for each rpc call to avoid connection-limit configuration on device (in case  data collection action require multiple rpc call, for example PortModuleDetail), the main file must handle the opening/closure of socket
                #dev.open(auto_probe=5) # this is required otherwise the bloody thing will wait forever

                logging.debug("Opened netconfig session to {}".format(dev))
                if kwargs is None:
                    #tu.doan 7/05/2019: GET_RPC will return exception if "commands" is used in table definition, rewrite this later
                    #logging.info("No argument provided for the RPC  [ {} ] - getting all data".format(TableviewList[tablename].GET_RPC))
                    logging.info("No argument provided - getting all data")
                    result = TableviewList[tablename](dev).get()
                    # result.address = result.hostname
                    # result.name = dev.facts['hostname']

                else:
                    #tu.doan 7/05/2019: GET_RPC will return exception if "commands" is used in table definition, rewrite this later
                    #logging.info("Some arguments was provided for the RPC  [ {} ], list of args is [ {} ] ".format(TableviewList[tablename].GET_RPC,kwargs))
                    logging.info("Some arguments was provided {}, passing to rpc".format(kwargs))
                    result = TableviewList[tablename](dev).get(**kwargs)
                #dev.close()
            else:
                logging.warning( "Invalid data type or tablename specified, provided file is [ {} ], data_type is [ {} ] and table name is [ {} ]".format(tableview_file,data_type,tablename) )
                return CRITICAL
        except Exception as e:
            logging.error ( "Data fetch from PyEZ tableview failed due to [ {} ]".format(e))
            return CRITICAL

    return result


def FORMAT_PYEZ_TABLEVIEW(dev=None,
                          tableview_obj=None,
                          include_hostname=False,
                          output_format = 'dictionary'):
    #""" get hardware information of junos device into a list of tableview item"""
    #type  =   tableview_obj -> jnpr.junos.factory.optable.TableModule.Table
    #type  =   output_format -> string
    import jnpr.junos.factory.optable as TableModule
    if not isinstance(tableview_obj, TableModule.Table):
        logging.warning("This function need a PyEZ table data, invalid type [ {} ] provided, exiting".format(type(tableview_obj)))
        logging.debug("Received adata is {}".format(tableview_obj))
        return CRITICAL

    global data_format_dict

    data_type_exist = False
    for data_format_names,data_format_metadata in data_format_dict.items(): #use iteritems in python 2
        #traversing the dictionary of possible output format, put the raw table through the corresponding convert function
        if output_format.lower() in data_format_metadata["format_names"]:
            data_type_exist = True
            convert_func_name = data_format_metadata['convert_func']

            if convert_func_name == "GET_PYEZ_TABLEVIEW_RAW":
                result = tableview_obj #If the desired output format is raw, return without any conversion (exception case)
            else:
                logging.debug("convert function name is [ {} ] ".format(convert_func_name))
                #If the desired output format not raw, return by calling the conversion function from global name space. DO NOT use "convert_func_name()" since that require function object, we only a string of the name
                if dev != None:
                    result = globals()[convert_func_name](dev=dev,tableview_obj=tableview_obj,include_hostname=include_hostname)
                else:
                    result = globals()[convert_func_name](tableview_obj=tableview_obj,include_hostname=include_hostname)

                #Another way to call this function
                #from  sys import modules
                #current_module = modules[__name__] #get current module name, because getattr require module name
                #convert_func = getattr(current_module,current_module)
                #result = convert_func(tableview_obj)

    # this comparison throw an exception through panda - confusing as fuck, use a check token instead
    #if result == None:
    if not data_type_exist:
         logging.warning("Invalid output format specified [ {} ] ".format(output_format))
         return CRITICAL
    else:
         return result

def GET_PYEZ_TABLEVIEW_FORMATTED(dev=None,
                                 data_type=None,
                                 tableview_file=None,
                                 rpc_kwargs=None,
                                 include_hostname=False,
                                 output_format = 'dictionary'):
    #""" get hardware information of junos device into a list of tableview item"""
    #type  =   dev -> junos.jnpr Device
    #type  =   data_type -> string
    #type  =   tableview_file -> string
    #type  =   output_format -> string
    #type  =   output_type -> string

    tableview_obj_raw = GET_PYEZ_TABLEVIEW_RAW(dev,data_type, tableview_file,rpc_kwargs)

    if tableview_obj_raw in [CRITICAL, WARNING]:
        logging.error("Tableview data will not be converted due to fetch failure for host[ {} ] . return code [ {} ]".format(dev, tableview_obj_raw) )
        return tableview_obj_raw
    else:
        logging.info ("Tableview data fetch complete for [ {} ], formatting data to [ {} ]".format(tableview_obj_raw.hostname,output_format))
        if dev != None:
            result = FORMAT_PYEZ_TABLEVIEW( dev=dev,
                                            tableview_obj=tableview_obj_raw,
                                            include_hostname=include_hostname,
                                            output_format=output_format)

        else:
            result = FORMAT_PYEZ_TABLEVIEW( tableview_obj=tableview_obj_raw,
                                            include_hostname=include_hostname,
                                            output_format=output_format)
        return result

def WRITE_PYEZ_TABLEVIEW_FORMATTED(dev=None,
                                   tableview_obj=None,
                                   include_hostname=False,
                                   output_format = 'dictionary',
                                   filename=None,
                                   write_mode = "w"):

    import jnpr.junos.factory.optable as TableModule
    if not isinstance(tableview_obj, TableModule.Table):
        logging.warning("This function need a PyEZ table data, invalid type [ {} ] provided, exiting".format(type(tableview_obj)))
        logging.debug("Received adata is {}".format(tableview_obj))
        return CRITICAL

    global data_format_dict

    data_type_exist = False
    for data_format_names,data_format_metadata in data_format_dict.items(): #use iteritems in python 2
        #traversing the dictionary of possible output format, put the raw table through the corresponding convert function
        if output_format.lower() in data_format_metadata["format_names"]:

            try:
                data_type_exist = True
                write_func_name = data_format_metadata['write_func']

                logging.info("formatting data for [ {} ] to [ {} ] before writing  ".format(tableview_obj.hostname,output_format))
                if dev != None:
                    result = FORMAT_PYEZ_TABLEVIEW(dev=dev,
                                                tableview_obj = tableview_obj,
                                                include_hostname = include_hostname,
                                                output_format = output_format,)
                else:
                    result = FORMAT_PYEZ_TABLEVIEW(tableview_obj = tableview_obj,
                                                include_hostname = include_hostname,
                                                output_format = output_format,)

                #TODO: fucking pandas cannot do this, now what?
                #if result == WARNING or result == CRITICAL:
                #    logging.warning("Seem like format operation on tableview object [ {} ] failed, nothing will be written to file")
                #    return WARNING

                logging.debug("write function name is [ {} ] ".format(write_func_name))
                logging.debug("Type of converted block data to be written is [ {} ]".format(type(result)))
                #Write  by calling the write function from global name space. DO NOT use "write_func_name()" since that require function object, we only a string of the name
                write_result = globals()[write_func_name](result,
                                                          filename=filename,
                                                          write_mode=write_mode)
            except Exception as e:
                logging.error("Could not write provided tableview object [ {} ] to file due to [ {} ]".format(tableview_obj,e))
                return CRITICAL

class PYEZ_TABLEVIEW_WRAPPER():
    #wrapper to save multi-host data

    #Save this for later use, this belong to the class, not the instance, do not change
    pyez_table_loader = 'jnpr.junos.factory.factory_loader'

    def __init__(self):
        self.TableviewFile = 1
        self.TableviewObject = 1
        self.data_type = 1
        self.rpc_kwargs = 1
        self.output_format = 1
        self.output_type = 1
        self.output_file = 1


def WRITE_PY_STRUCT_TO_FILE(py_data,
                            filename,
                            write_mode = "w",
                            encoding = "utf-8"):
    try:
        import io
        from pprint import pformat
        logging.info ("Writing python suct to file [ {} ]".format(filename))
        prettified = pformat(py_data)

        if encoding == "utf-8":
            with io.open(filename, write_mode, encoding='utf-8') as py_file:     ##open output file
                prettified_coded = unicode(prettified,'utf-8')
                if file_writable(filename) == True:
                    py_file.write(prettified_coded)

        elif encoding == "ascii" or encoding == "ASCII":
            with open(filename, write_mode) as py_file:     ##open output file
                if file_writable(filename) == True:
                    py_file.write(prettified)

        else:
            logging.error ( "Incorrect encoding specified [ {} ], nothing will be written ".format(encoding))
            return CRITICAL
    except Exception as e:
        logging.error ( "Error writing result to text file due to [ {} ]".format(encoding))
        return CRITICAL
    return OK

def WRITE_XML_TO_FILE(xml_data,
                      filename,
                      write_mode = "w"):
    try:
        logging.info ("Writing info to file " + filename)
        with open(filename, write_mode) as xml_file:     ##open output file
            xml_file.write('<root>\n') ##put xml root directive

            #for xml_element in xml_data:
            #    xml_content = etree.tostring(xml_element, pretty_print=True) ##parsing xml content to write
            #    logging.debug("writing " + xml_content + " to file")
            #    xml_file.write(xml_content)
            xml_file.write(xml_data)

            xml_file.write('</root>') ##put xml root directive
    except Exception as e:
        logging.error ( "Error writing result to XML file due to ".format(e))
        return CRITICAL
    return OK

def WRITE_JSON_TO_FILE(json_data,
                       filename,
                       write_mode = "w",
                       encoding = "utf-8"):

    import codecs,json
    # Make it work for Python 2+3 and with Unicode
    try:
        to_unicode = unicode
    except NameError:
         to_unicode = str
    logging.info ("Writing info to file " + filename)

    try:
        if type(json_data) == str:
            with open(filename, write_mode) as json_file:
                json_file.write(json_data)
        elif type(json_data) == dict:
            if encoding == "utf-8":
                with codecs.open(filename, write_mode, encoding='utf-8') as json_file:     ##codesc.open with encoding set only accepts unicode objects, be absolutely sure json_data is unicode
                    converted_str=  json.dumps( json_string,
                                                ensure_ascii=False,
                                                separators=(',', ': '), # To prevent Python from adding trailing whitespaces
                                                indent=4,
                                                sort_keys=True)
                    json_file.write(to_unicode(converted_str))

            elif encoding == "ascii" or encoding == "ASCII":
                with open(filename, write_mode) as json_file:     ##open output file
                    json.dump(  json_string,
                                json_file,
                                indent=4,
                                sort_keys=True)
        else:
            raise TypeError(" Can only write dict or str content to json file!! ")
            return CRITICAL
    except Exception as e:
        logging.error ( "Error writing result to JSON file due to ".format(e))
        return CRITICAL
    return OK


def PYEZ_TABLEVIEW_TO_CSV(tabledata,
                          filename,
                          write_mode = "wb",
                          include_hostname = True):
    # type: (tabledata) -> PyEZTableView
    # type: (filename) -> str
    """Recursively convert Juniper PyEZ Table/View items to list of dicts, then to csv"""
    data_list = PYEZ_TABLEVIEW_TO_LIST_OF_DICT(tabledata)
    final_key_list = list()
    import jnpr.junos.factory.optable as TableModule
    if data_list == CRITICAL or data_list == WARNING or data_list is None:
        logging.warning("Table data was not converted to list of dict, csv will not be written, exit code for conversion was " + str(data_list) )
        return WARNING
    elif isinstance(data_list, TableModule.Table):
        logging.info("Table data was not converted to list of dict, csv data will be written to " + str(filename) )

    try:
        if include_hostname == True:
            final_key_list.append('source_hostname')
        for item in data_list:
            #traverse each item, getting the key into the key list
            logging.debug("Getting keylist for item: " + str(item))
            key_list = item.keys()
            for key in key_list:
                if key not in final_key_list:
                    final_key_list.append(key)

            if include_hostname == True:
                item['source_hostname'] = tabledata.hostname
        logging.info("Key list to be written to csv is " + str(final_key_list) )
    except Exception as e:
        logging.error("Failed to get key list from tableview data due to :" + str(e))
        return CRITICAL

    try:
        import csv
        logging.debug("Data to be dumped is " + str(data_list))
        with open(filename, write_mode) as output_file:
            dict_writer = csv.DictWriter(output_file, final_key_list)
            dict_writer.writeheader()
            dict_writer.writerows(data_list)
        logging.info("All data successfully written to " + str(filename) )
        return OK
    except Exception as e:
        logging.error("Failed to write tableview data to csv :" + str(e))
        return CRITICAL

def WRITE_DATAFRAME_TO_FILE(data,
                            filename,
                            write_mode = "w"):
    try:
        import pandas
        from pandas import DataFrame
        if not isinstance(data, DataFrame):
            logging.warning("This function need a pandas dataframe, invalid type provided, exiting")
            return CRITICAL
        if write_mode == "w":
            logging.info ("Writing DataFrame to new file " + filename)
            data.to_csv(filename,mode=write_mode,header=True,index=True, index_label="Index")
        elif write_mode == "a" or write_mode == "a+":
            if not os.path.isfile(filename):
                logging.warning ("Append mode was set but file not found, Writing DataFrame to new file " + filename)
                data.to_csv(filename, mode=write_mode, header=True,index=True, index_label="Index")
            else:
                try:
                    if file_writable(filename) == True:
                        old_data = pandas.read_csv(filename, index_col=0)

                    #if len(data.columns) != len(old_data.columns):
                    #    raise Exception("Columns do not match!! Dataframe has " + str(len(data.columns)) + " columns. CSV file has " + str(len(old_data.columns)) + " columns.")
                    #elif not (data.columns == old_data.columns.all()):
                    #    raise Exception("Columns or column order of dataframe and csv file do not match!!")
                    #else:
                        logging.info ("Data merged, Writing DataFrame to new file " + filename)
                        new_data = pandas.concat([data,old_data],axis=0,join='outer',ignore_index=True)
                        new_data.to_csv(filename, mode='w', header=True,index=True, index_label="Index")
                except Exception as e:
                    logging.warning ( "File csv  " + filename + " exist but failed to read due to {}".format(e))
                    logging.warning ( "Overwriting old csv  " + filename)
                    # data.to_csv(filename, mode=write_mode, header=True,index=True, index_label="Index")
                    if file_writable(filename) == True:
                        data.to_csv(filename, mode=write_mode, header=False,index=True, index_label="Index")

    except Exception as e:
        logging.error ( "Error writing result to csv file due to {}".format(e))
        return CRITICAL
    return OK