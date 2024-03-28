import networkx
import pandas as pd
import logging
import os
from pprint import pprint
from networkx.drawing.nx_pydot import to_pydot, write_dot
import ast
from tabulate import tabulate


class NXGraph():
    def __init__(self, ):
        pass

    def create_Topo(self,   dataframe=None,
                            node_column={"Source": "source", "Dest": "dest", "Attr": ["attr1", "attr2"]},
                            edge_column={"Source_edge": "source_edge", "Dest_edge": "dest_edge", "Attr": ["attr1", "attr2"]}):
        if edge_column["Attr"] == False:
            edge_column["Attr"] = []

        if node_column["Attr"] == None or node_column["Attr"] == False:
            node_column["Attr"] = []

        list_edge_attr = []

        if isinstance(edge_column["Attr"], str):
            edge_column["Attr"] = [edge_column["Attr"]]

        topo1 = networkx.convert_matrix.from_pandas_edgelist(   dataframe,
                                                                source=node_column["Source"],
                                                                target=node_column["Dest"],
                                                                edge_attr=True,
                                                                create_using=networkx.MultiDiGraph())
        if node_column["Attr"] != [] :
            for col in node_column["Attr"]:
                for source, dest, key, attr in topo1.edges(data=True,keys=True):
                    attribute_name = col
                    topo1.nodes[source]["_name"] = source

                    if attribute_name == node_column["Source"]:
                        topo1.nodes[source][node_column["Source"]] = source

                    else:
                        topo1.nodes[source][attribute_name] = attr[attribute_name]
        else:
            for node, attr in topo1.nodes(data=True):
                topo1.nodes[node]["_name"] = node

        for source,dest,key,intf_name in topo1.edges(data=True,keys=True):
            list_edge_attr_name = list(intf_name.keys())
            topo1.add_edge(source, dest, key, name=intf_name[edge_column["Source_edge"]], label=intf_name[edge_column["Source_edge"]], source=source, dest=dest)
            for edge_attr_name in list_edge_attr_name:
                if edge_attr_name not in edge_column["Attr"]:
                    topo1.edges[source,dest,key].pop(edge_attr_name)
        # print(topo1.nodes(data=True))
        # print(topo1.edges(data=True))
        topo2 = networkx.convert_matrix.from_pandas_edgelist(   dataframe,
                                                                source=node_column["Dest"],
                                                                target=node_column["Source"],
                                                                edge_attr=True,
                                                                create_using=networkx.MultiDiGraph())

        if node_column["Attr"] != [] :
            for col in node_column["Attr"]:
                for source, dest, key, attr in topo2.edges(data=True,keys=True):
                    attribute_name = col
                    topo2.nodes[source]["_name"] = source

                    if attribute_name == node_column["Source"]:
                        topo2.nodes[source][node_column["Source"]] = source
                    if "time" in attribute_name:
                        topo2.nodes[source][attribute_name] = attr[attribute_name]
                    # else:
                    #     topo2.nodes[source][attribute_name] = attr[attribute_name]
        else:
            for node, attr in topo2.nodes(data=True):
                topo2.nodes[node]["_name"] = node

        for source,dest,key,intf_name in topo2.edges(data=True,keys=True):
            list_edge_attr_name = list(intf_name.keys())
            topo2.add_edge(source, dest, key, name=intf_name[edge_column["Dest_edge"]], label=intf_name[edge_column["Dest_edge"]], source=source, dest=dest)
            for edge_attr_name in list_edge_attr_name:
                # if edge_attr_name not in edge_column["Attr"]:
                topo2.edges[source,dest,key].pop(edge_attr_name)


        final_topo = networkx.MultiDiGraph()
        final_topo.add_nodes_from(topo1.nodes(data=True))
        final_topo.add_nodes_from(topo2.nodes(data=True))
        final_topo.add_edges_from(topo1.edges(data=True,keys=True))
        final_topo.add_edges_from(topo2.edges(data=True,keys=True))

        return final_topo
