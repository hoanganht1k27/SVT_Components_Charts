import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
import logging
import time
try:
    import PYEZ_BASE_FUNC
except:
    from ansible.module_utils import PYEZ_BASE_FUNC


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# List module type
def GET_JUNOS_PORTMODULE_DETAIL(dev = None,
                                tableview_file = "hardware_inventory.yml", #the two bloody table must be on the same file to avoid code complexity
                                pic_data_definition = "PICStatus",
                                port_module_data_definition = "PortModuleDetail",
                                port_module_output_format = "list_of_dict",
                                pic_rpc_kwargs=None,
                                include_hostname = False):

    try:
        PicStatusResult = PYEZ_BASE_FUNC.GET_PYEZ_TABLEVIEW_FORMATTED( dev = dev,
                                                                       data_type = pic_data_definition,
                                                                       tableview_file = tableview_file,
                                                                       rpc_kwargs = pic_rpc_kwargs,
                                                                       output_format = "list_of_dict",
                                                                       include_hostname = False)

        PortModule_result = list()
        for item in PicStatusResult:
            rpc_kwargs = dict()
            rpc_kwargs['fpc-slot'] = item['fpc_slot']
            rpc_kwargs['pic-slot'] = item['pic_slot']
            result_item = dict()
            result_item["item_fetching_arguments"] = rpc_kwargs

            result_item["result"] = PYEZ_BASE_FUNC.GET_PYEZ_TABLEVIEW_FORMATTED( dev = dev,
                                                                           data_type = port_module_data_definition,
                                                                           tableview_file = tableview_file,
                                                                           rpc_kwargs = rpc_kwargs,
                                                                           output_format = port_module_output_format,
                                                                           include_hostname = include_hostname)

            PortModule_result.append(result_item)
    except Exception as e:
        logging.error("Exception during collecting PortModule detail due to " + str(e))
        return CRITICAL
    return PortModule_result 


def GET_JUNOS_BNG_SUB_PER_VLAN( dev = None,
                                tableview_file = "bng.yml", #the two bloody table must be on the same file to avoid code complexity
                                pre_data_definition = "BNG_Vlan",
                                post_data_definition = "BNG_sub_per_vlan",
                                output_format = "list_of_dict",
                                include_hostname = False):

    try:
        dev.timeout = 2000
        Pre_Result = PYEZ_BASE_FUNC.GET_PYEZ_TABLEVIEW_FORMATTED(dev = dev,
                                                                data_type = pre_data_definition,
                                                                tableview_file = tableview_file,
                                                                rpc_kwargs = None,
                                                                output_format = "list_of_dict",
                                                                include_hostname = False)
        Post_result = list()
        count = 0
        for item in Pre_Result:
            if "0x8100" not in item['vlan_id']:
                rpc_kwargs = dict()
                rpc_kwargs['vlan_id'] = item['vlan_id']
                rpc_kwargs['count'] = ''
                result_item = dict()
                result_item["item_fetching_arguments"] = rpc_kwargs

                data = PYEZ_BASE_FUNC.GET_PYEZ_TABLEVIEW_FORMATTED( dev = dev,
                                                                    data_type = post_data_definition,
                                                                    tableview_file = tableview_file,
                                                                    rpc_kwargs = rpc_kwargs,
                                                                    output_format = output_format,
                                                                    include_hostname = include_hostname)

                data_frame = PYEZ_BASE_FUNC.PYEZ_TABLEVIEW_TO_DATAFRAME(dev=dev, tableview_obj=data, include_hostname=True)
                data_frame['vlan_id'] = "vlan-" + item['vlan_id']
                Post_result.append(data_frame)
                time.sleep(5)
                count = count + 1
                # if count == 2:
                #     break

        return Post_result
    except Exception as e:
        logging.error("Exception during collecting BNG-COUNT- detail due to " + str(e))
        return CRITICAL
