import os
import time
import logging
import argparse
import ast
import pandas

import BASE_FUNC

from pprint import pformat
from pprint import pprint


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3






common_argument_init_functions = [ BASE_FUNC.INIT_OUTPUT_FILE_ARGS,
                                   BASE_FUNC.INIT_LOGGING_ARGS]


def PARSE_ARGS():
    """Parse command-line args"""
    global common_argument_init_functions
    parent_parser_obj = argparse.ArgumentParser(description='\nConvert xls data to yaml data')
    #put arguments here to be inherited by all subparser, useful if Gooey is not involved.
    for argument_init_func in common_argument_init_functions:
        argument_init_func(parent_parser_obj)

    parent_parser_obj.add_argument( '-i', 
                                       '--input_file', 
                                       dest = "input_file",
                                       type=str,
                                       default = "CSR-DATA-LAB.xlsx",
                                       help='        Input data file')

    parent_parser_obj.add_argument( '-ds', 
                                       '--data_sheet', 
                                       dest = "data_sheet",
                                       type=str,
                                       default = "Demo",
                                       help='        Data sheet to read from file')

    parent_parser_obj.add_argument( '-hi', 
                                       '--host_identifier', 
                                       dest = "host_identifier",
                                       type=ast.literal_eval,
                                       default = ["hostname","address"],
                                       help='        List of keywork that identify a host, default to ["hostname","address"]')

    parent_parser_obj.add_argument( '-gd', 
                                       '--group_demiliter', 
                                       dest = "group_demiliter",
                                       type=str,
                                       default = ".",
                                       help='       Demiliter that specify grouped structure in xls file, default to "."')

    parent_parser_obj.add_argument( "--custom_setting_file" ,
                                       dest = "custom_setting_file" ,
                                       type = str ,
                                       default = "./xls_to_inventory.setting.py",
                                       help = "Custom setting file to be exported " )

    return parent_parser_obj.parse_args()
    #return parent_parser_obj

def LD_TO_DL(list_of_dict):
    if not isinstance (list_of_dict,list):
        logging.error("This function need a list of dict, exiting!")
        raise Exception("This function need a list of dict, invalid type was provided!")
    
    dict_of_list = dict()
    for d in list_of_dict:
        for k,v in d.items():
            try:
                dict_of_list[k].append(v)
            except KeyError:
                dict_of_list[k]=[v]
    return dict_of_list

def GROUP_LIST_OF_DICT(data,
                       keylist = [],
                       keep_key = False,):
    if not isinstance (data,list):
        logging.error("This function need a list of dict, exiting!")
        raise InputError("This function need a list of dict, invalid type was provided!")

    from operator import itemgetter
    sortkeyfn = itemgetter(*keylist)
    logging.info("sorting items fields using keylist [{}]".format(sortkeyfn))
    data.sort(key=sortkeyfn)
    
    from itertools import groupby 
    grouped_data = list()
    logging.info("Grouping data base on keylist {}".format(keylist))

    for grouping_key,ungrouped_value in groupby(data, key=sortkeyfn):
        grouped_data_item = dict()
        
        i = 0
        for item in keylist:
            grouped_data_item[item] = grouping_key[i]
            i += 1
        
        other_value = []
        for value in ungrouped_value:
            if keep_key == False:
                for item in keylist:
                    value.pop(item,None)
            other_value.append(value)

        logging.debug("Key {} has been grouped".format(grouping_key))
        logging.debug("Ungrouped values is {}".format(other_value))

        grouped_data_item['vars'] = other_value
        grouped_data.append(grouped_data_item)
    return grouped_data

 # Main
def main(args = PARSE_ARGS(),current_time = BASE_FUNC.TIME_INIT()):

    ##=======================================Import custom setting if available===============================================#
    if args.custom_setting_file != None:
        BASE_FUNC.ARGS_SETTING_OVERRIDE(args.custom_setting_file,args)
    #=======================================Creating log and reviewing arguments===============================================#
    log_file    =    os.path.join( args.log_dir, 
                                   "{}_{}_{}.log".format(args.log_prefix,
                                                          time.strftime(args.log_timestamp),
                                                          args.log_surfix)
                                 )
    BASE_FUNC.LOGGER_INIT(args.log_level, log_file, print_log_init = True,shell_output= True)
    logging.info("List of received arguments: [ {} ] ".format(args))


    try:
        logging.info("Reading data from sheet [{}] of spreadsheet file [{}]".format(args.data_sheet, args.input_file))
        with open(args.input_file,'rb') as spreadsheet_file:
            raw_df = pandas.read_excel(spreadsheet_file, sheet_name=args.data_sheet, keep_default_na=False)

        #=======================================Grouping data according to Hostname and address=====================================#
        raw_data = raw_df.to_dict('index').values()
        data = list(raw_data)
        logging.debug ("The following data from spreadsheet will be processed")
        logging.debug(pformat(data))

    except Exception as e:
        logging.error("Error parsing data from sheet [{}] of spreadsheet file [{}] due to [{}]".format(args.data_sheet, args.input_file,e))
        raise

    
    #=======================================Grouping data according to Hostname and address=====================================#

    grouped_data = BASE_FUNC.GROUP_LIST_OF_DICT(data,args.host_identifier)
    #=======================================Creating vars group================================================#

    for host in grouped_data:
        host_vars = dict()
        for host_data in host['vars']:
            if not isinstance(host_data,dict):
                logging.warning("Invalid host var format loaded, exiting!")
                continue
            
            for key,value in host_data.items():
                if "." in key:
                    group_key = key.split('.')[0] #get the first element of a column name as key group

                    if group_key not in host_vars:
                        host_vars[group_key] = list()

                else:
                    host_vars[key] = value

        #host.pop('vars')
        host['host_vars'] = host_vars

    #=======================================Grouping data according to var group================================================#

    for host in grouped_data:
        host_vars = host['host_vars']
        for host_data in host['vars']:
            if not isinstance(host_data,dict):
                logging.warning("Invalid host var format loaded, exiting!")
                continue
            
            data_block = dict()
            #initiate all group key in data block first, to insert depend datakey later
            for key,value in host_data.items():
                if "." in key:
                    group_key = key.split('.')[0] #get the first element of a column name as key group
                    if group_key not in data_block:
                        data_block[group_key] = dict()
                else:
                    host_vars[key] = value

            #Loop again to get final value
            for key,value in host_data.items():
                if "." in key:
                    var_element = key.split('.') #get the first element of a column name as key group

                    group_key = var_element[0]
                    data_key = var_element[1]

                    data_block[group_key][data_key] = value

                    if data_key == "logical_interface" and "RI" in data_block:
                        data_block["RI"][data_key] = value

                    if data_key == "local_ip_ipv4" and "RI" in data_block:
                        data_block["RI"][data_key] = value

                    if data_key == "RI_name" and "RI" in data_block:
                        data_block["interfaces"][data_key] = value

                    if data_key == "RI_gateway" and "interfaces" in data_block:
                        data_block["interfaces"][data_key] = value
                else:
                    host_vars[key] = value

            for key in data_block:
                host_vars[key].append( data_block[key])
        host.pop('vars')
        host['host_vars'] = host_vars
    #=======================================Grouping var group data into sub-vargroup ================================================#
    # for host in grouped_data:
    #     host['host_vars']["RI"] = BASE_FUNC.GROUP_LIST_OF_DICT(data = host['host_vars']["RI"] ,
    #                                                  keylist = ["RI_name","EXPORT_NAME","EXPORT_VALUE","IMPORT_NAME","IMPORT_VALUE","RD","remote_pingable"],
    #                                                  keep_key = False)
    #     for item in host['host_vars']["RI"]:
    #         item['vars'] = LD_TO_DL(item['vars'])
    #         for key,value in item['vars'].items():
    #             item[key] = value
    #         item.pop('vars')

    #=======================================Dump host var to yaml ================================================#
    import yaml
    rundeck_list_host = []
    ansible_inv_host = []

    for host in grouped_data:
        hostname_writer = BASE_FUNC.PROTECT_FILENAME(host[args.host_identifier[0]])
        try:
            rundeck_list_host.append("{}_{}".format(hostname_writer,host[args.host_identifier[1]] ))
            output_file_name = os.path.join(args.output_dir,
                                "host_vars",
                                "{}.yml".format(hostname_writer))
    
            BASE_FUNC.CREATE_EXPORT_DIR(os.path.join(args.output_dir,"host_vars"))
            logging.info("Writing host_vars to files: {}".format(output_file_name))
            with open( output_file_name , 'w') as output_file:
                yaml.dump(host['host_vars'], output_file,  allow_unicode=True, default_flow_style=False)
                
            ansible_inv_host.append("{} ansible_host={}\n".format(hostname_writer,host[args.host_identifier[1]] ))
        except Exception as e:
            logging.error("Error during writing host_vars for host [{}] due to [{}], host data will not be written".format(hostname_writer,e))
            continue 

        BASE_FUNC.CREATE_EXPORT_DIR(os.path.join(args.output_dir,"host_vars"))
        logging.info("Writing host_vars to files: {}".format(output_file_name))
        try:
            with open( output_file_name.strip("\n") , 'w') as output_file:
                yaml.dump(host['host_vars'], output_file,  allow_unicode=True, default_flow_style=False)
        except Exception as e:
            logging.error("Failed to write data for host [{}] to [{}] due to [{}]".format(host["hostname"],output_file_name,e))

    with open( os.path.join(args.output_dir,"inventory") , 'w') as output_file:
        logging.info("Writing inventory host list to file: {}".format(output_file.name))
        for inventory_item in ansible_inv_host:
            output_file.write(format (inventory_item))
    #pprint(grouped_data)





if __name__ == "__main__":
    main()
