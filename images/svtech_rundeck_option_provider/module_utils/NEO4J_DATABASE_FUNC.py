from py2neo import Graph, Node, Relationship
import pandas as pd
import networkx
import json
import sys
import os
import time
from datetime import datetime
import argparse
import logging
from .nxgraph import NXGraph



def ts_to_dt(timestamp):
    from datetime import datetime
    date_time = datetime.fromtimestamp(timestamp)
    return date_time

def dt_to_ts(datetime):
    from datetime import datetime
    timestamp = datetime.timestamp(datetime)
    return timestamp

def convert_data(data_input):
    df = pd.DataFrame()
    # Check the JSON
    if isinstance(data_input, str):
        try:
            json_object = json.loads(data_input)
            try:
                df = pd.DataFrame(json_object)
            except:
                logging.error("The data input {} is valid JSON string, but can't convert to data frame".format(data_input))
                return False
        except:
            logging.error("The data input {} is not a valid JSON string".format(data_input))
            return False

    # Check the list of dict
    elif isinstance(data_input, list):
        if len(data_input) > 0:
            if isinstance(data_input[0], dict):
                try:
                    df = pd.DataFrame(data_input)
                except Exception as err:
                    logging.error("The data input {} can NOT be converted to data frame: {}".format(data_input, err))
                    return False
            else:
                logging.error("The type of first element is {}, require a dict".format(type(data_input[0])))
                return False
        else:
            logging.warning("The data input is empty")
            return True

    # Check the dictionary
    elif isinstance(data_input, dict):
        if len(data_input) > 0:
            try:
                df = pd.DataFrame(data_input)
            except Exception as err:
                logging.error("The data input {} can NOT be converted to data frame: {}".format(data_input, err))
                return False
        else:
            logging.warning("The data input is empty")
            return True

    # Check the data frame
    elif isinstance(data_input, pd.DataFrame):
        if len(data_input) > 0:
            df = data_input
            del data_input
        else:
            logging.warning("The data input is empty")
            return True

    else:
        logging.error("Other type of data input is not support. Please give: Data Frame, list of dict, dict or JSON")
        return False
    return df

def insert_data_to_neo4j(host=None,
                         port=7687,
                         username=None,
                         password=None,
                         data_type=None,
                         label=None,
                         data_input=None,
                         node_column={"Source": "source", "Dest": "dest", "Attr": ["attr1", "attr2"]},
                         edge_column={"Source_edge": "source_edge", "Dest_edge": "dest_edge", "Attr": ["attr1", "attr2"]},
                         hostname=None):

    graph = Graph("bolt://{}:{}".format(host, port), username=username, password=password)

    df = convert_data(data_input)
    df.fillna('', inplace=True)
    now = datetime.now()
    time_update_dB = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    df["time"] = time_update_dB
    data_converted = df.to_dict("records")

    if data_type == "node":
        graph.run("MATCH (n:`{}`) WHERE n.hostname='{}' DETACH DELETE n".format(label, hostname))
        tx = graph.begin()
        for each_data in data_converted:
            node = Node(label, **each_data)
            tx.create(node)
            # list_key = list(each_data.keys())
            # list_key.remove('time')
            # list_key = ["hostname", "address", "tableview_key"]
            # tx.merge(subgraph=node, primary_label=label, primary_key=keys)
        tx.commit()

    elif data_type == "relationship":
        nxtopo = NXGraph().create_Topo( dataframe=df,
                                        node_column=node_column,
                                        edge_column=edge_column)
        graph.run("MATCH (n:`{}`) WHERE n._name='{}' DETACH DELETE n".format(label, hostname))
        graph.run("CREATE CONSTRAINT ON (n:`{}`) ASSERT n._name IS UNIQUE".format(label))
        for node, attr in nxtopo.nodes(data=True):
            node_attr_str = ', '.join(['{}:{!r}'.format(k, v) for k, v in attr.items()])
            create_node_str =   "MERGE (n:`%(label)s` { %(attr)s } ) \
                                ON CREATE SET n.time = '%(time)s' \
                                ON MATCH SET n.time = '%(time)s' \
                                "%{ "label": label,
                                    "attr": node_attr_str,
                                    "time": str(time_update_dB)
                                    }
            graph.run(create_node_str)
        tx = graph.begin()
        for source,dest,key,attr in nxtopo.edges(data=True,keys=True):
            find_exists_relationship_str =  "MATCH (s:`%(label)s`)-[r:`%(label)s`]->(d:`%(label)s`)\
                                            WHERE r.source = '%(source)s' AND r.dest = '%(dest)s' AND r._name = '%(name)s' \
                                            RETURN r \
                                            "%{ "label": label,
                                                "source": source,
                                                "dest": dest,
                                                "name": attr["name"]
                                            }

            find_exists_relationship = graph.run(find_exists_relationship_str).data()
            logging.info(find_exists_relationship)
            if find_exists_relationship == []:
                str_attr = ', '.join(['{}:{!r}'.format(k, v) for k, v in attr.items()])
                create_relationship_str =   "MATCH (s:`%(label)s`),(d:`%(label)s`)\
                                            WHERE s._name = '%(source)s' AND d._name = '%(dest)s' \
                                            CREATE (s)-[r:`%(label)s` { %(attr)s, time: '%(time)s' } ]->(d) \
                                            "%{ "label": label,
                                                "source": source,
                                                "dest": dest,
                                                "attr": str_attr,
                                                "time": str(time_update_dB)
                                            }
                tx.run(create_relationship_str)

            else:
                str_attr = ', '.join(['{}:{!r}'.format(k, v) for k, v in attr.items()])
                update_relationship_str =  "MATCH (s:`%(label)s`)-[r:`%(label)s`]->(d:`%(label)s`)\
                                            WHERE s._name = '%(source)s' AND d._name = '%(dest)s' \
                                            SET r = { %(attr)s, time: '%(time)s' } \
                                            "%{ "label": label,
                                                "source": source,
                                                "dest": dest,
                                                "attr": str_attr,
                                                "time": str(time_update_dB)
                                            }
                tx.run(update_relationship_str)
        tx.commit()

if __name__ == "__main__":
    pass
    # data = [
    #     {   'physical_interface': 'ge-1/1/3',
    #         'tableview_key': 'ge-1/1/3',
    #         'parent_interface': '-',
    #         'neighbor_name': 'AGG01_RE0',
    #         'neighbor_physical_interface': 'ge-0/3/8',
    #         'hostname': 'SRT01',
    #         'address': '10.96.10.101',
    #         'time': '2020-05-22T14:01:23Z'
    #     },

    #     {
    #         'physical_interface': 'xe-1/3/0',
    #         'tableview_key': 'xe-1/3/0',
    #         'parent_interface': '-',
    #         'neighbor_name': 'AGG01_RE0',
    #         'neighbor_physical_interface': 'xe-1/0/0',
    #         'hostname': 'SRT01',
    #         'address': '10.96.10.101',
    #         'time': '2020-05-22T14:01:23Z'
    #       },

    #       {
    #         'physical_interface': 'xe-1/3/1',
    #         'tableview_key': 'xe-1/3/1',
    #         'parent_interface': '-',
    #         'neighbor_name': 'SRT02',
    #         'neighbor_physical_interface': 'xe-1/3/0',
    #         'hostname': 'SRT01',
    #         'address': '10.96.10.101',
    #         'time': '2020-05-22T14:01:23Z'
    #       }
    # ]
    # insert_data_to_neo4j(host="localhost",
    #                      port=7687,
    #                      username="neo4j",
    #                      password="juniper@123",
    #                      data_type="relationship",
    #                      label="LLDP",
    #                      data_input=data,
    #                      node_column={  "Source": "hostname",
    #                                     "Dest": "neighbor_name",
    #                                     "Attr": ["hostname", "address"]},
    #                      edge_column={  "Source_edge": "physical_interface",
    #                                     "Dest_edge": "neighbor_physical_interface",
    #                                     "Attr": ["physical_interface", "neighbor_physical_interface"]},
    #                      hostname="SRT01")
    # graph = Graph("http://localhost:7474/db/data/", username="neo4j", password="juniper@123")
    # # default_db = Database("http://localhost:7474/db/data/", username="neo4j", password="juniper@123")

