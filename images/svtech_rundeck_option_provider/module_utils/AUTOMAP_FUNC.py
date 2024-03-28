#!/opt/.pyenv/versions/3.6.5/envs/automation36/bin/python
import ast
from datetime import datetime
import time
import re
import os
import argparse
import logging
from pprint import pprint
from jinja2 import Template
import numpy as np
import networkx
import pandas as pd
from networkx.drawing.nx_pydot import to_pydot, write_dot
import math

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../module_utils')))
import shutil
from module_utils.nxgraph import NXGraph


def makeNodeObjectID(node_name):
    # object_id = node_name.lower().replace(".", "").replace("-", "").replace("_", "").replace(" ", "").replace("@", "")
    object_id = re.sub('\W','', node_name.lower().replace("_", ""))
    return object_id

def makeEdgeObjectID(source_id, dest_id, key):
    if key == None:
        key = ""
    object_id = "{}TO{}{}".format(source_id, dest_id, str(key))
    return object_id

def makeShapeObjectID(source_id, dest_id, key):
    if key == None:
        key = ""
    object_id = "{}and{}end{}".format(source_id, dest_id, str(key))
    return object_id

def makeString(*args):
    string = ""
    for i in args:
        string = string + i
    return string

class NagvisAutoMap():
    def __init__(self, ):
        pass

    def getDataFromExcel(self,  excel_file="",
                                sheet_name=""):
        try:
            data = pd.read_excel(   excel_file,
                                    sheet_name="data",
                                    header=0,
                                    index_col=None,
                                    keep_default_na=False
                                )
            pprint(data)
        except Exception as e:
            logging.error("Failed to import xls to dataframe due to [{}]".format(e))
        return data

    def createMapFromGraphviz(self, nxtopo=None,
                                    template_file="./template/template.j2",
                                    output_dir="",
                                    graph_name="",
                                    map_variable=None,
                                    auto_scale=True):
        # nodes_location = networkx.planar_layout(nxtopo,center=[5000, 5000], scale=10000, dim=2)
        # prog='dot'
        # prog='neato'
        # prog='twopi'
        # prog='circo'
        # prog='fdp'
        pos = networkx.nx_pydot.graphviz_layout(nxtopo, prog=map_variable["layout"])
        node_list = list(nxtopo)
        if auto_scale == True:
            if map_variable["layout"] == "dot":
                scale = int(math.sqrt(len(node_list)))*1500
            else:
                scale = int(math.sqrt(len(node_list)))*1000
        else:
            scale = map_variable["scale"]

        pos = np.row_stack([pos[x] for x in node_list])
        nodes_location = networkx.drawing.layout.rescale_layout(pos, scale=scale)
        nodes_location = dict(zip(node_list, pos))

        for node in nodes_location:
            location = [int(nodes_location[node][0] + scale), int(nodes_location[node][1] + scale)]
        min_x = min([nodes_location[i][0] for i in nodes_location])
        min_y = min([nodes_location[i][1] for i in nodes_location])

        for node in nodes_location:
            location = [int(nodes_location[node][0] - min_x + 500), int(nodes_location[node][1] - min_y + 500)]
            nodes_location[node] = location
            nxtopo.nodes[node]["locate"] = location
            nxtopo.nodes[node]["node_name"] = node
            nxtopo.nodes[node]["object_id"] = makeNodeObjectID(node)

        list_pair_node = []
        for x in nodes_location:
            for y in nodes_location:
                if x != y and [y, x] not in list_pair_node:
                    list_pair_node.append([x, y])
        list_shape = []
        for source, dest, key, attr in nxtopo.edges(data=True, keys=True):
            source_locate = nxtopo.nodes[source]["locate"]
            dest_locate = nxtopo.nodes[dest]["locate"]

            source_id = nxtopo.nodes[source]["object_id"]
            dest_id = nxtopo.nodes[dest]["object_id"]
            pair = [source, dest]
            shape_tmp = {}
            shape_locate = self.generateShapeLocation(  map_variable=map_variable,
                                                        source_locate=source_locate,
                                                        dest_locate=dest_locate,
                                                        edge_key=int(key))
            if pair in list_pair_node:
                shape_tmp = {
                    "object_id": makeShapeObjectID(source_id, dest_id, key),
                    "locate": shape_locate
                }
                list_shape.append(shape_tmp)

            else:
                shape_tmp = {
                    "object_id": makeShapeObjectID(dest_id, source_id, key),
                    "locate": shape_locate
                }

            edge_locate1, edge_locate2 = self.generateEdgesLocationByID(map_variable=map_variable,
                                                                        source_locate=source_locate,
                                                                        dest_locate=dest_locate,
                                                                        source_id=source_id,
                                                                        dest_id=dest_id,
                                                                        shape_id=shape_tmp["object_id"])
            edge_object_id = makeEdgeObjectID(source_id, dest_id, key)
            nxtopo.add_edge(source, dest, key, locate=edge_locate1, object_id=edge_object_id)

        self.generateMapFile(nxtopo=nxtopo,
                             list_shape=list_shape,
                             template_file=template_file,
                             output_dir=output_dir,
                             graph_name=graph_name,
                             map_variable=map_variable)

    def generateMapFile(self, nxtopo={},
                              list_shape=[],
                              template_file="",
                              output_dir="",
                              graph_name="",
                              map_variable=None):
        node_data = [attr for node, attr in nxtopo.nodes(data=True)]
        link_data = [attr for source, dest, attr in nxtopo.edges(data=True)]
        if map_variable["backend_id"] != None:
            rendered = Template(open(template_file).read()).render(nodes_data=node_data, links_data=link_data, shape_data=list_shape, backend_id=map_variable["backend_id"])
        else:
            rendered = Template(open(template_file).read()).render(nodes_data=node_data, links_data=link_data, shape_data=list_shape)

        with open('{}/{}.cfg'.format(output_dir, graph_name.replace(".", "")), 'w') as f:
            f.write(rendered)


    def generateEdgesLocationByID(self, map_variable={},
                                        source_locate=[],
                                        dest_locate=[],
                                        source_id="",
                                        dest_id="",
                                        shape_id=""):

        icon_length = str(int(map_variable["icon_length"]/2))
        icon_height = str(int(map_variable["icon_height"]/2))

        shape_lenght = str(int(map_variable["shape_lenght"]))
        shape_height = str(int(map_variable["shape_height"]))

        edge1_locate = [[], []]     # [ [x1, y1], [x2, y2] ]
        edge2_locate = [[], []]     # [ [x1, y1], [x2, y2] ]

        edge1_x1 = makeString(source_id, "%+", icon_length)
        edge1_y1 = makeString(source_id, "%+", icon_height)
        edge1_x2 = shape_id
        edge1_y2 = shape_id

        edge2_x1 = dest_id
        edge2_y1 = dest_id
        edge2_x2 = shape_id
        edge2_y2 = shape_id

        edge1_locate =  [   [ edge1_x1 , edge1_y1 ],
                            [ edge1_x2 , edge1_y2 ]
                        ]

        edge2_locate =  [   [ edge2_x1 , edge2_y1 ],
                            [ edge2_x2 , edge2_y2 ]
                        ]

        return edge1_locate, edge2_locate

    def generateShapeLocation(self, map_variable={},
                                    source_locate=[],
                                    dest_locate=[],
                                    edge_key=0):

        icon_length = int(map_variable["icon_length"]/2)
        icon_height = int(map_variable["icon_height"]/2)
        shapes_distance = map_variable["shapes_distance"]

        edge1_locate = [[], []]     # [ [x1, y1], [x2, y2] ]
        edge1_x1 = source_locate[0] + icon_length
        edge1_y1 = source_locate[1] + icon_height

        if edge_key == 0:
            edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
            edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height

        else:
            check_odd_even = "even" if (edge_key%2 == 0) else "odd"
            shapes_offset = int((edge_key + 1)/2) * shapes_distance

            if abs(source_locate[0] - dest_locate[0]) < 1000:  # x1 = x2
                if check_odd_even == "odd":
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length + shapes_offset
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height + shapes_offset
                else:
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length - shapes_offset
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height - shapes_offset


            elif abs(source_locate[1] - dest_locate[1]) < 1000:  # y1 = y2
                if check_odd_even == "odd":
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height + shapes_offset
                else:
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height - shapes_offset

            else:
                if check_odd_even == "odd":
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height + shapes_offset
                else:
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height - shapes_offset


        shape_locate = [ edge1_x2 , edge1_y2 ]
        return shape_locate

    def generateEdgesLocation(self, map_variable={},
                                    source_locate=[],
                                    dest_locate=[],
                                    edge_key=0):

        icon_length = int(map_variable["icon_length"]/2)
        icon_height = int(map_variable["icon_height"]/2)
        shapes_distance = map_variable["shapes_distance"]

        edge1_locate = [[], []]     # [ [x1, y1], [x2, y2] ]
        edge2_locate = [[], []]     # [ [x1, y1], [x2, y2] ]

        edge1_x1 = source_locate[0] + icon_length
        edge1_y1 = source_locate[1] + icon_height

        if edge_key == 0:
            edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
            edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height

        else:
            check_odd_even = "even" if (edge_key%2 == 0) else "odd"
            shapes_offset = int((edge_key + 1)/2) * shapes_distance

            if abs(source_locate[0] - dest_locate[0]) < 1000:  # x1 = x2
                if check_odd_even == "odd":
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length + shapes_offset
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height + shapes_offset
                else:
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length - shapes_offset
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height - shapes_offset


            elif abs(source_locate[1] - dest_locate[1]) < 1000:  # y1 = y2
                if check_odd_even == "odd":
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height + shapes_offset
                else:
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height - shapes_offset

            else:
                if check_odd_even == "odd":
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height + shapes_offset
                else:
                    edge1_x2 = int((source_locate[0] + dest_locate[0] )/2) + icon_length
                    edge1_y2 = int((source_locate[1] + dest_locate[1] )/2) + icon_height - shapes_offset


        shape_locate = [ edge1_x2 , edge1_y2 ]
        return edge1_locate, edge2_locate

    def generateNewNodeLocaltion(self, nxtopo=None,
                                       start_locate=[],
                                       node_distance=[],
                                       exists_host={},
                                       exists_object=[]):
        # nodes_data = [node for node in list(nxtopo.nodes(data=True)) if node[1] != {}]
        nodes_data = list(nxtopo.nodes(data=True))
        for i in range(len(nodes_data)):
            x = ( ( (i+5)%5 ) + 1 )*node_distance[0] + start_locate[0]
            y = ( ( int((i+5)/5)) + 1)*node_distance[0] + start_locate[1]
            node_name = nodes_data[i][0]
            nxtopo.nodes[node_name]["node_name"] = node_name
            nxtopo.nodes[node_name]["locate"] = [x, y]

            if node_name in exists_host:
                object_id = exists_host[node_name]["object_id"]
                nxtopo.nodes[node_name]["object_id"] = object_id
            else:
                nxtopo.nodes[node_name]["object_id"] = makeNodeObjectID(node_name)

        return nxtopo

    def updateMap(self, nxtopo=None,
                        template_file="./template/template.j2",
                        output_map_file="",
                        map_variable=None,
                        exists_host={},
                        exists_object=[]):
        list_pair_node = []
        for x in list(nxtopo):
            for y in list(nxtopo):
                if x != y and [y, x] not in list_pair_node:
                    list_pair_node.append([x, y])
        list_shape = []
        for source, dest, key, attr in nxtopo.edges(data=True, keys=True):
            # if nxtopo.nodes[dest] != {} and nxtopo.nodes[source] != {}:
            if source in exists_host:
                source_locate = [int(exists_host[source]["x"]), int(exists_host[source]["y"])]
            else:
                source_locate = nxtopo.nodes[source]["locate"]

            if dest in exists_host:
                dest_locate = [int(exists_host[dest]["x"]), int(exists_host[dest]["y"])]
            else:
                dest_locate = nxtopo.nodes[dest]["locate"]

            source_id = nxtopo.nodes[source]["object_id"]
            dest_id = nxtopo.nodes[dest]["object_id"]
            pair = [source, dest]
            shape_tmp = {}

            shape_locate = self.generateShapeLocation(  map_variable=map_variable,
                                                        source_locate=source_locate,
                                                        dest_locate=dest_locate,
                                                        edge_key=int(key))

            shape_id_tmp1 = makeShapeObjectID(source_id, dest_id, key)
            shape_id_tmp2 = makeShapeObjectID(dest_id, source_id, key)

            if "shape" in exists_object:
                list_shape_exists = [ i["object_id"] for i in exists_object["shape"] if i["object_id"][:-1] == shape_id_tmp1[:-1] or i["object_id"][:-1] == shape_id_tmp2[:-1] ]
            else:
                list_shape_exists = []

            shape_key = 0
            if list_shape_exists == []:
                shape_key = key
            else:
                shape_key = len(list_shape_exists) + int(key)

            if pair in list_pair_node:
                shape_tmp = {
                    "object_id": makeShapeObjectID(source_id, dest_id, shape_key),
                    "locate": shape_locate
                }
                list_shape.append(shape_tmp)

            else:
                shape_tmp = {
                    "object_id": makeShapeObjectID(dest_id, source_id, shape_key),
                    "locate": shape_locate
                }
                # list_shape.append(shape_tmp)

            edge_locate1, edge_locate2 = self.generateEdgesLocationByID(map_variable=map_variable,
                                                                        source_locate=source_locate,
                                                                        dest_locate=dest_locate,
                                                                        source_id=source_id,
                                                                        dest_id=dest_id,
                                                                        shape_id=shape_tmp["object_id"])
            edge_object_id = makeEdgeObjectID(source_id, dest_id, key)
            nxtopo.add_edge(source, dest, key, locate=edge_locate1, object_id=edge_object_id)
        list_exists_hostname = []
        for h in exists_host:
            list_exists_hostname.append(h)
        self.updateMapFile(nxtopo=nxtopo,
                           list_shape=list_shape,
                           template_file=template_file,
                           output_map_file=output_map_file,
                           map_variable=map_variable,
                           exists_host=list_exists_hostname)

    def updateMapFile(self, nxtopo={},
                            list_shape=[],
                            template_file="",
                            output_map_file="",
                            map_variable=None,
                            exists_host=[]):
        node_data = [attr for node, attr in nxtopo.nodes(data=True) if node not in exists_host]
        link_data = [attr for source, dest, attr in nxtopo.edges(data=True)]

        if map_variable["backend_id"] != None:
            rendered = Template(open(template_file).read()).render(nodes_data=node_data, links_data=link_data, shape_data=list_shape, backend_id=map_variable["backend_id"])
        else:
            rendered = Template(open(template_file).read()).render(nodes_data=node_data, links_data=link_data, shape_data=list_shape)

        with open(output_map_file, 'a') as f:
            f.write(rendered)

    def NagvisMapParser(self, config_file=""):
        with open(config_file, "r") as f:
            read_file = f.read()
            block_text = re.findall(r".*define\s+[\s\S]*?\}", read_file)
            results = {}
            for block in block_text:
                find_object_type = re.findall(r"^define\s+(.*)\s+\{", block)
                if find_object_type != []:
                    object_type = find_object_type[0]
                    value_line = [i for i in block.splitlines() if "=" in i]
                    item_dict = {}
                    for item in value_line:
                        split_string = item.split("=")
                        key = split_string[0]
                        value = split_string[1]
                        item_dict[key] = value
                    if object_type not in results:
                        results[object_type] = [item_dict]
                    else:
                        results[object_type].append(item_dict)
            return results

    def NagvisMapWriter(self, map_object={}, dest_file=""):
        string_to_write = ""
        template = \
"""
define %(object_type)s {
%(contents)s
}
"""
        for key, value in map_object.items():
            object_type = key
            for item in value:
                contents = ""
                for k, v in item.items():
                    line = "{}={}\n".format(k, v)
                    contents += line
                block_text = template %{ "object_type": object_type,
                                        "contents": contents
                                        }
                string_to_write += block_text
        with open(dest_file, "w") as f:
            f.write(string_to_write)




def convert_LLDP_data(LLDP_neigbor_df=None,
                      SNMP_intf_index_df=None):

    LLDP_neigbor_df.replace(to_replace ='.RE[01]', value = '', regex = True, inplace = True)
    SNMP_intf_index_df.replace(to_replace ='.RE[01]', value = '', regex = True, inplace = True)
    for index, row in LLDP_neigbor_df.iterrows():
        source = row["hostname"]
        dest = row["neighbor_name"]
        try:
            # neighbor_physical_interface = ast.literal_eval(row["neighbor_physical_interface"])
            neighbor_physical_interface = int(row["neighbor_physical_interface"])
        except Exception as e:
            neighbor_physical_interface = row["neighbor_physical_interface"]

        if isinstance(neighbor_physical_interface, int):
            # find_neighbor_ip = LLDP_neigbor_df.loc[(LLDP_neigbor_df['hostname'] == dest) & (LLDP_neigbor_df['neighbor_name'] == source)]
            find_neighbor_ip = SNMP_intf_index_df.loc[(SNMP_intf_index_df['hostname'] == dest)]
            if find_neighbor_ip.empty == False:
                neighbor_ip = list(find_neighbor_ip.address)[0]
                # logging.info("Host has Interface index: {}, {}".format(neighbor_ip, neighbor_physical_interface))
                find_mapping_intf = SNMP_intf_index_df.loc[(SNMP_intf_index_df['address'] == neighbor_ip) & (SNMP_intf_index_df['interface_snmp_index'] == str(neighbor_physical_interface))]
                # logging.info(find_mapping_intf)
                if find_mapping_intf.empty == False:
                    interface_name = list(find_mapping_intf.interface_name)[0]
                    # logging.info("Interface name to change: {}, {}".format(interface_name, index))
                    LLDP_neigbor_df.at[index, "neighbor_physical_interface"] = interface_name

    LLDP_neigbor_df.drop_duplicates(  subset=["hostname", "neighbor_name", "physical_interface", "neighbor_physical_interface"],
                                keep = "first",
                                inplace = True)

    loopback_intf_index = LLDP_neigbor_df[ LLDP_neigbor_df['hostname'] == LLDP_neigbor_df['neighbor_name'] ].index
    if list(loopback_intf_index) != []:
        LLDP_neigbor_df.drop(loopback_intf_index , inplace=True)

    return LLDP_neigbor_df




def convert_OSPF_data(OSPF_neighbor_df=None,
                      OSPF_routerID_df=None,
                      OSPF_Intf_Addr_df=None):
    OSPF_neighbor_df.replace(to_replace ='.RE[01]', value = '', regex = True, inplace = True)
    OSPF_routerID_df.replace(to_replace ='.RE[01]', value = '', regex = True, inplace = True)
    OSPF_Intf_Addr_df.replace(to_replace ='.RE[01]', value = '', regex = True, inplace = True)

    OSPF_merge_router_id = pd.merge(OSPF_neighbor_df, OSPF_routerID_df[['router_id', "hostname", "address"]], how='inner', left_on=['neighbor_id'], right_on=['router_id'], suffixes=('', '_neighbor_router_id') )
    OSPF_final_data = pd.merge(OSPF_merge_router_id, OSPF_Intf_Addr_df[['hostname', "address", "interface_name", "interface_address"]], how='left', left_on=["neighbor_address"], right_on=["interface_address"], suffixes=('', '_neighbor') )
    loopback_intf_index = OSPF_final_data[ OSPF_final_data['hostname'] == OSPF_final_data['hostname_neighbor'] ].index
    if list(loopback_intf_index) != []:
        OSPF_final_data.drop(loopback_intf_index , inplace=True)

    return OSPF_final_data


def convert_BGP_data(BGP_Neighbor_df=None,
                     BGP_local_id_df=None):
    BGP_Neighbor_df.replace(to_replace ='.RE[01]', value = '', regex = True, inplace = True)
    BGP_local_id_df.replace(to_replace ='.RE[01]', value = '', regex = True, inplace = True)

    BGP_lod = BGP_Neighbor_df.to_dict('records')
    for item in BGP_lod:
        regex_peer_address = re.findall(r"(\d+\.\d+\.\d+\.\d+)", item["peer_address"])
        if regex_peer_address != []:
            item["peer_id"] = regex_peer_address[0]

        regex_local_address = re.findall(r"(\d+\.\d+\.\d+\.\d+)", item["local_address"])
        if regex_local_address != []:
            item["local_id"] = regex_local_address[0]

    BGP_Neighbor_data = pd.DataFrame(BGP_lod)

    BGP_id_lod = BGP_local_id_df.to_dict('records')
    for item in BGP_id_lod:
        regex_peer_address = re.findall(r"(\d+\.\d+\.\d+\.\d+)", item["peer_address"])
        if regex_peer_address != []:
            item["peer_id"] = regex_peer_address[0]

        regex_local_address = re.findall(r"(\d+\.\d+\.\d+\.\d+)", item["local_address"])
        if regex_local_address != []:
            item["local_id"] = regex_local_address[0]

    BGP_id_data = pd.DataFrame(BGP_id_lod)
    BGP_id_data.drop_duplicates(subset=["hostname", "address", "local_id"], keep = "first", inplace = True)
    BGP_final_data = pd.merge(BGP_Neighbor_data, BGP_id_data, how='inner', left_on=['peer_id'], right_on=['local_id'], suffixes=('', '_neighbor') )
    BGP_final_data.drop_duplicates(subset=["hostname", "hostname_neighbor", "local_id", "peer_id"],
                                    keep = "first",
                                    inplace = True)
    loopback_intf_index = BGP_final_data[ BGP_final_data['hostname'] == BGP_final_data['hostname_neighbor'] ].index

    if list(loopback_intf_index) != []:
        BGP_final_data.drop(loopback_intf_index , inplace=True)

    return BGP_final_data

def remove_row_match_value(df=None, value=None, column=None):
    nan_value = float("NaN")
    df.replace(value, nan_value, inplace=True)
    if column == None:
        df.dropna(inplace=True)
    else:
        df.dropna(subset=column, inplace=True)
    return df

def remove_row_match_regex(df=None, column_name=None, regex=""):
    m = ~df[column_name].str.contains(regex)
    result = df[m]
    return result


def validate_and_fix_nagvis_config(config_file=""):
    nagvismap_config = NagvisAutoMap().NagvisMapParser(config_file=config_file)
    changed = False
    list_object_id_changed = []
    for item in nagvismap_config["host"]:
        regex_x = re.findall(r"(^\d+$)", item["x"])
        regex_y = re.findall(r"(^\d+$)", item["y"])

        if regex_x == [] or regex_y == []:
            item["x"] = "1000"
            item["y"] = "1000"

        expect_object_id = makeNodeObjectID(item["host_name"])
        exists_object_id = item["object_id"]
        if expect_object_id != exists_object_id:
            changed = True
            dict_tmp = {
                "old_id": exists_object_id,
                "new_id": expect_object_id
            }
            list_object_id_changed.append(dict_tmp)
            item["object_id"] = expect_object_id

    if "service" in nagvismap_config and "shape" in nagvismap_config:
        if list_object_id_changed != []:
            changed = True
            for i in list_object_id_changed:

                for item in nagvismap_config["service"]:
                    if i["old_id"] in item["object_id"]:
                        item["object_id"] = item["object_id"].replace(i["old_id"], i["new_id"])

                    if i["old_id"] in item["x"]:
                        item["x"] = item["x"].replace(i["old_id"], i["new_id"])
                    if i["old_id"] in item["y"]:
                        item["y"] = item["y"].replace(i["old_id"], i["new_id"])

                for item in nagvismap_config["shape"]:
                    if i["old_id"] in item["object_id"]:
                        item["object_id"] = item["object_id"].replace(i["old_id"], i["new_id"])
    if "shape" in nagvismap_config:
        new_shape_object = []
        for item in nagvismap_config["shape"]:
            if "and" in item["object_id"] and "end" in item["object_id"]:
                new_shape_object.append(item)
        if new_shape_object != []:
            changed = True
            nagvismap_config["shape"] = new_shape_object

    if changed == True:
        NagvisAutoMap().NagvisMapWriter(map_object=nagvismap_config, dest_file=config_file)

