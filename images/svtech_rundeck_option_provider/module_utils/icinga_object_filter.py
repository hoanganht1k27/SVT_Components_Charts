# This library queries to livestatus with user filter to return the icinga_object (host or service only). This library can
# aslo query to ido db to get the object_id if id_flag=True and return the object id which is passed the filter.
# The ido connection is not necessary if the function return object name (host name or service name)
import liveStatusWrapper
import mysql.connector
import logging
import pandas as pd


def icinga_object_filter(object_type: str, user_filter: list, id_flag: bool = False, livestatus_connection: dict = {'livestatus_ip': 'localhost', 'livestatus_port': 6558}, ido_connection: dict = {'ido_host': 'localhost', 'ido_port': 3306, 'user': 'juniper', 'password': 'juniper@123', 'database': 'icinga'}) -> list:
    '''
    This function will return the icinga object name or id based on user filter. If the object id should be returned then
    ido connection need to be specified by user because the object id exists only in ido db
    param: object_type: the icinga object type (host or service only)
    param: user_filter: the user filter (a list contains all user filter, the logic filter is AND)
    param: id_flag: return object_id or not
    param: livestatus_connection: the livestatus connection e.g. {'livestatus_ip': 'localhost', 'livestatus_port': 6558}
    param: ido_connection: the ido db connection {'ido_host': 'localhost', 'ido_port': 3306, 'user': 'juniper', 'password': 'juniper@123', 'database': 'icinga'}
    '''
    result = []
    # Check the argument - Start
    if object_type not in ['host', 'service']:
        logging.error('The support object type is host or service only')
        return []
    if not isinstance(user_filter, list):
        logging.error('The user_filter must be a list')
        return []
    if not isinstance(livestatus_connection, dict):
        logging.error('The livestatus_connection should be a dict')
    if not isinstance(ido_connection, dict):
        logging.error('The ido_connection should be a dict')
    # Check the argument - End
    if object_type == 'host':
        object_type = 'hosts'
        live_result = liveStatusWrapper.getInfos(livestatus_connection['livestatus_ip'], livestatus_connection['livestatus_port'], object_type, user_filter, 'display_name')
        if not id_flag:
            for element in live_result:
                result.append({'host': element['display_name']})
        else:
            df1 = pd.DataFrame(live_result)
            db_connection = mysql.connector.connect(host=ido_connection['ido_host'], port=ido_connection['ido_port'], user=ido_connection['user'], password=ido_connection['password'], database=ido_connection['database'])
            df2 = pd.read_sql('SELECT object_id, name1 FROM icinga_objects WHERE objecttype_id = 1;', con=db_connection)
            logging.debug('livestatus result:')
            logging.debug(df1)
            logging.debug('IDO result:')
            logging.debug(df2)
            merge_df = pd.merge(df1, df2, left_on='display_name', right_on='name1')
            merge_df.rename(columns={"display_name": "host"}, inplace=True)
            result = merge_df[['object_id', "host"]].to_dict('records')
    else:
        object_type = 'services'
        live_result = liveStatusWrapper.getInfos(livestatus_connection['livestatus_ip'], livestatus_connection['livestatus_port'], object_type, user_filter, 'display_name', 'host_name')
        if not id_flag:
            for element in live_result:
                result.append({'host': element['host_name'], 'service': element['display_name']})
        else:
            df1 = pd.DataFrame(live_result)
            db_connection = mysql.connector.connect(host=ido_connection['ido_host'], port=ido_connection['ido_port'], user=ido_connection['user'], password=ido_connection['password'], database=ido_connection['database'])
            df2 = pd.read_sql('SELECT object_id, name1, name2 FROM icinga_objects WHERE objecttype_id = 2;', con=db_connection)
            logging.debug('livestatus result:')
            logging.debug(df1)
            logging.debug('IDO result:')
            logging.debug(df2)
            merge_df = pd.merge(df1, df2, left_on=['display_name', 'host_name'], right_on=['name2', 'name1'])
            merge_df.rename(columns={"host_name": "host", "display_name": "service"}, inplace=True)
            result = merge_df[['object_id', 'host', 'service']].to_dict('records')
    return result


if __name__ == '__main__':
    print(icinga_object_filter('host', ['display_name ~ AGG'], True, {'livestatus_ip': '10.98.0.116', 'livestatus_port': 6558},
    {'ido_host': '10.98.0.116', 'ido_port': 3306, 'user': 'juniper', 'password': 'juniper@123', 'database': 'icinga'}))
    print(icinga_object_filter('host', ['display_name ~ AGG'], False, {'livestatus_ip': '10.98.0.116', 'livestatus_port': 6558},
    {'ido_host': '10.98.0.116', 'ido_port': 3306, 'user': 'juniper', 'password': 'juniper@123', 'database': 'icinga'}))
    print(icinga_object_filter('service', ['display_name ~ IfCheck'], True, {'livestatus_ip': '10.98.0.116', 'livestatus_port': 6558},
    {'ido_host': '10.98.0.116', 'ido_port': 3306, 'user': 'juniper', 'password': 'juniper@123', 'database': 'icinga'}))
    print(icinga_object_filter('service', ['display_name = ping4'], False, {'livestatus_ip': '10.98.0.116', 'livestatus_port': 6558},
    {'ido_host': '10.98.0.116', 'ido_port': 3306, 'user': 'juniper', 'password': 'juniper@123', 'database': 'icinga'}))