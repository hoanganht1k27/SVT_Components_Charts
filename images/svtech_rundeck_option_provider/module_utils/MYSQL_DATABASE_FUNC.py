import pandas as pd
import pymysql
import logging
from sqlalchemy import create_engine
import traceback
import json
import sys
import os
import time
import datetime

# from ansible.module_utils import BASE_FUNC
# BASE_FUNC.LOGGER_INIT("INFO", "/tmp/MYSQL.log", print_log_init = False,shell_output= True)


def insert_data_from_junos_collect_tableview(data_input, host, user, pw, db, data_type, host_name, port=3306, runtime=None):
    """
    This function compares data in dataframe pandas (receive from other module) and information in database to identify
    the different data which need to be stored in "historical" table. This function also replaces old data in "current"
    table by using data from dataframe.
    :param data_input: The data source input, it can be data frame pandas, list of dict object, list of dict string,
    json string, or csv file path
    :param host: mysql server hostname
    :param user: mysql user to login
    :param pw: mysql user password to login
    :param db: mysql database name
    :param data_type: data type (e.g. cb, pem, sfb, etc.)
    :param host_name: the host name - to whom the data belongs
    :param port: the mysql server port
    list of dict (string), json and data frame pandas
    :return: True if insert data successfully, False if otherwise
    """
    success = False
    df = None
    # [Kien] - 13/03/2020 - Verify the type of input - Start
    # Check the data frame
    if isinstance(data_input, pd.DataFrame):
        if len(data_input) > 0:
            df = data_input
            del data_input
        else:
            logging.warning("The data input is empty")
            return True
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
    # Check the JSON string
    elif isinstance(data_input, str):
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
    else:
        logging.error("Other type of data input is not support. Please give: Data Frame, list of dict, dict or JSON")
        return False

    # [Ha] - 28/05/2020 - Add force column type to string - Start
    for d in df:
        # if df.dtypes[d] == "object":
        df[d] = df[d].astype(str)
    # [Ha] - 28/05/2020 - Add force column type to string - End

    # [Kien] - 27/05/2020 - Add the runtime to database - Start
    if runtime is None:
        df["runtime"] = datetime.datetime.now()
    else:
        if isinstance(runtime, str):
            try:
                df["runtime"] = pd.to_datetime(runtime, format="%Y-%m-%d %H:%M:%S")
            except:
                logging.error("The format runtime is not OK. Please give a string with format: YYYY-MM-DD hh:mm:ss".format(
                    type(runtime)))
                return False
        else:
            logging.error("The runtime type is {}. Please give a string with format: YYYY-MM-DD hh:mm:ss".format(type(runtime)))
            return False
    # [Kien] - 27/05/2020 - Add the runtime to database - End
    # [Kien] - 13/03/2020 - Verify the type of input - End

    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}:{port}/{db}"
                           .format(user=user,
                                   pw=pw,
                                   host=host,
                                   port=port,
                                   db=db))
    try:
        conn = engine.connect()
        # Check if the table exists - Start
        cursor = conn.execute("SELECT count(*) FROM information_schema.TABLES WHERE (TABLE_SCHEMA = '{}')"
                              " AND (TABLE_NAME = '{}_current')".format(db, data_type))
        # Check if the table exists - End
        result = cursor.fetchall()
        if result[0][0] == 0:
            # Table does not exist
            df.to_sql(name=data_type + "_current", con=conn, if_exists='append', index=False)
            result = conn.execute("SELECT count(*) FROM information_schema.TABLES WHERE (TABLE_SCHEMA = '{}')"
                                  " AND (TABLE_NAME = '{}_history')".format(db, data_type)).fetchall()
            if result[0][0] == 0:
                df.to_sql(name=data_type + "_history", con=conn, if_exists='append', index=False)
                conn.execute("ALTER TABLE `{}_history` ADD `lastUpdated` TIMESTAMP "
                             "NOT NULL DEFAULT CURRENT_TIMESTAMP".format(data_type))
            else:
                df.to_sql(name=data_type + "_history", con=conn, if_exists='append', index=False)
        else:
            # Table exists
            # Get old value to compare and drop old value in "current" table (contains only lasted information) - Start
            query = "SELECT * FROM `{}_current` WHERE hostname = '{}'".format(data_type, host_name)
            df_temp = pd.read_sql(query, conn)
            if df_temp.empty:
                # The information of host name "X" does not exist, so, just write new data to current table and
                # historical table
                logging.debug(
                    "The information of host name '{}' does not exist in table '{}'. Write new data to current"
                    " table and historical table".format(host_name, data_type + "_current"))
                df.to_sql(name=data_type + "_current", con=conn, if_exists='append', index=False)
                result = conn.execute("SELECT count(*) FROM information_schema.TABLES WHERE (TABLE_SCHEMA = '{}')"
                                      " AND (TABLE_NAME = '{}_history')".format(db, data_type)).fetchall()
                if result[0][0] == 0:
                    # Historical table does not exist, need to "ALTER TABLE" to add the lastUpdated time
                    logging.debug("Historical table does not exist, need to 'ALTER TABLE' to add the lastUpdated time")
                    df.to_sql(name=data_type + "_history", con=conn, if_exists='append', index=False)
                    conn.execute("ALTER TABLE `{}_history` ADD `lastUpdated` TIMESTAMP "
                                 "NOT NULL DEFAULT CURRENT_TIMESTAMP".format(data_type))
                else:
                    logging.debug("Just write new data to historical table")
                    df.to_sql(name=data_type + "_history", con=conn, if_exists='append', index=False)
            else:
                logging.debug("Compare the data in dafaframe and current table to write data to historical table")
                # Drop old data and write new data to current table. For historical table, write only updated and new
                # data
                conn.execute("DELETE FROM `{}_current` WHERE hostname = '{}'".format(data_type, host_name))
                # Write new data to current table
                df.to_sql(name=data_type + "_current", con=conn, if_exists='append', index=False)
                # Check the difference between 2 data frames and write the difference to historical data - Start
                columns_name = list(df.columns)
                columns_name.remove('runtime')
                df_diff = pd.merge(df, df_temp, how='left', on=columns_name, indicator=True)
                df_diff = df_diff[df_diff['_merge'] == 'left_only']
                df_diff.drop(['_merge'], axis=1, inplace=True)
                logging.debug(df)
                logging.debug(df_temp)
                logging.debug(df_diff)
                if df_diff.empty:
                    logging.debug("There are no new data, don't write data to historical table")
                else:
                    logging.debug("Write different data to historical table")
                    result = conn.execute("SELECT count(*) FROM information_schema.TABLES WHERE (TABLE_SCHEMA = '{}')"
                                          " AND (TABLE_NAME = '{}_history')".format(db, data_type)).fetchall()
                    if result[0][0] == 0:
                        df_diff.to_sql(name=data_type + "_history", con=conn, if_exists='append', index=False)
                        conn.execute("ALTER TABLE `{}_history` ADD `lastUpdated` TIMESTAMP "
                                     "NOT NULL DEFAULT CURRENT_TIMESTAMP".format(data_type))
                    else:
                        df_diff.to_sql(name=data_type + "_history", con=conn, if_exists='append', index=False)
                # Check the difference between 2 data frames and write the difference to historical data - End
            # Get old value to compare and drop old value in "current" table (contains only lasted information) - End
        success = True
    except Exception as err:
        logging.error("The process to import {} of {} is error due to {}".format(data_type, host_name, err))
        logging.exception(err)
    return success


if __name__ == '__main__':
    # df1 = pd.read_csv("/home/kien/Documents/testpython/VNPT_hardware/data_CB__123.29.4.1.csv", index_col='Index')
    # list_of_dict = [{'desc': 'Kien789', 'hostname': '123.29.4.1', 'model': 'CB-TXP-S', 'name': 'CB 0', 'pn': '710-022606', 'sn': 'CAFR9002', 'tableview_key': 'CB 0', 'ver': 'REV 22'},
    #                 {'desc': 'SFC Control Board', 'hostname': '123.29.4.1', 'model': 'CB-TXP-S', 'name': 'CB 1', 'pn': '710-022606', 'sn': 'ABDB7868', 'tableview_key': 'CB 1', 'ver': 'REV 17'},
    #                 {'desc': 'LCC Control Board', 'hostname': '123.29.4.1', 'model': 'CB-LCC-S', 'name': 'CB 0', 'pn': '710-022597', 'sn': 'CACX2549', 'tableview_key': 'CB 0', 'ver': 'REV 13'},
    #                 {'desc': 'LCC Control Board', 'hostname': '123.29.4.1', 'model': 'CB-LCC-S', 'name': 'CB 1', 'pn': '710-022597', 'sn': 'CADA7478', 'tableview_key': 'CB 1', 'ver': 'REV 14'},
    #                 {'desc': 'LCC Control Board', 'hostname': '123.29.4.1', 'model': 'CB-LCC-S', 'name': 'CB 0', 'pn': '710-022597', 'sn': 'CACR0617', 'tableview_key': 'CB 0', 'ver': 'REV 13'},
    #                 {'desc': 'LCC Control Board', 'hostname': '123.29.4.1', 'model': 'CB-LCC-S', 'name': 'CB 1', 'pn': '710-022597', 'sn': 'CACR0607', 'tableview_key': 'CB 1', 'ver': 'REV 13'}]
    # result_insert = insert_data_from_junos_collect_tableview(df1, '10.98.0.154', 'juniper', 'juniper@123',
    #                                                          'test_collect_tbv', 'cb', '123.29.4.1')
    dict_of_list = {'desc': {0: 'Kien45', 1: 'SFC Control Board', 2: 'LCC Control Board', 3: 'LCC Control Board', 4: 'LCC Control Board', 5: 'LCC Control Board', 6: 'LCC Control Board', 7: 'LCC Control Board', 8: 'LCC Control Board', 9: 'LCC Kien', 10: 'LCC Kien2', 11: 'LCC Kien4'}, 'hostname': {0: '123.29.4.1', 1: '123.29.4.1', 2: '123.29.4.1', 3: '123.29.4.1', 4: '123.29.4.1', 5: '123.29.4.1', 6: '123.29.4.1', 7: '123.29.4.1', 8: '123.29.4.1', 9: '123.29.4.1', 10: '123.29.4.1', 11: '123.29.4.1'}, 'model': {0: 'CB-TXP-S', 1: 'CB-TXP-S', 2: 'CB-LCC-S', 3: 'CB-LCC-S', 4: 'CB-LCC-S', 5: 'CB-LCC-S', 6: 'CB-LCC-S', 7: 'CB-LCC-S', 8: 'CB-LCC-S', 9: 'CB-LCC-S', 10: 'CB-LCC-S', 11: 'CB-LCC-S'}, 'name': {0: 'CB 0', 1: 'CB 1', 2: 'CB 0', 3: 'CB 1', 4: 'CB 0', 5: 'CB 1', 6: 'CB 0', 7: 'CB 1', 8: 'CB 0', 9: 'CB 1', 10: 'CB 1', 11: 'CB 1'}, 'pn': {0: '710-022606', 1: '710-022606', 2: '710-022597', 3: '710-022597', 4: '710-022597', 5: '710-022597', 6: '710-022597', 7: '710-022597', 8: '710-022597', 9: '710-022597', 10: '710-022597', 11: '710-022597'}, 'sn': {0: 'CAFR9002', 1: 'ABDB7868', 2: 'CACX2549', 3: 'CADA7478', 4: 'CACR0617', 5: 'CACR0607', 6: 'CAFS1710', 7: 'CAFS1729', 8: 'CAFV0228', 9: 'CAFS1727', 10: 'CAFS1727', 11: 'CAFS1727'}, 'tableview_key': {0: 'CB 0', 1: 'CB 1', 2: 'CB 0', 3: 'CB 1', 4: 'CB 0', 5: 'CB 1', 6: 'CB 0', 7: 'CB 1', 8: 'CB 0', 9: 'CB 1', 10: 'CB 1', 11: 'CB 1'}, 'ver': {0: 'REV 22', 1: 'REV 17', 2: 'REV 13', 3: 'REV 14', 4: 'REV 13', 5: 'REV 13', 6: 'REV 14', 7: 'REV 14', 8: 'REV 14', 9: 'REV 14', 10: 'REV 14', 11: 'REV 14'}}
    # result_insert = insert_data_from_junos_collect_tableview(list_of_dict, '10.98.0.154', 'juniper', 'juniper@123',
    #                                                          'test_collect_tbv', 'cb', '123.29.4.1')
    json_string = json.dumps(dict_of_list)
    result_insert = insert_data_from_junos_collect_tableview(json_string, '10.98.0.117', 'juniper', 'juniper@123',
                                                             'testing', 'cb', '123.29.4.1', 3306, '2020-05-27 12:00:00')
