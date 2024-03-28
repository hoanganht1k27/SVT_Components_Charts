import logging
import json
import socket

try:
    from livestatus import Socket
except:
    from ansible.module_utils.livestatus import Socket

keywords =['hosts', 'services', 'hostgroups', 'servicegroups', 'contactgroups',
           'servicesbygroup', 'servicesbyhostgroup', 'hostsbygroup', 'contacts',
           'commands', 'timeperiods', 'downtimes', 'comments', 'log', 'status',
           'columns', 'statehist']


def getInfos(ip, port, userInput, filter, *columns):
    '''
    This function get data from livestatus
    :param userInput: The object which user want to get information. E.x. hosts, services, etc.
    :param filter: The filter applied on the query (can be a list, in the case the filter is a list, the result need to pass all filter)
    :param columns: The output column
    :return: empty list if there are no result, otherwise, a list of dict with the required data
    '''
    result = list()
    if userInput not in keywords:
        logging.error("The input {} is not in the accepted keywords {}".format(userInput, keywords))
        raise Exception("The input {} is not in the accepted keywords {}".format(userInput, keywords))
    else:
        socket = Socket((ip, port))
        query = getattr(socket, userInput)
        if columns:
            query = query.columns(*columns)
        if filter:
            if type(filter) == str:
                query = query.filter(filter)
            elif type(filter) == list:
                for eachFilter in filter:
                    query = query.filter(eachFilter)
            else:
                logging.error("The type of filter is not suppported: {}".format(type(filter)))
                raise Exception("The type of filter is not suppported: {}".format(type(filter)))
        result = query.call()
    return result


def getCount(ip, port, userInput, filter = None, statFilter = None):
    '''
    This function count the result data by using the The Livestatus Query Language
    :param userInput: The object which user want to get information. E.x. hosts, services, etc.
    :param filter: The filter applied on the query (can be a list, in the case the filter is a list, the result need to pass all filter)
    :param statFilter: The condition to count (user can add the condition to count other variable). Note that the counter shall perform
    after the filter. That means "livestatus" shall count the filtered result with the condition in the "statFilter"
    :return: empty list if there are no result, otherwise, a list of dict with the required data
    '''
    result = list()
    if userInput not in keywords:
        logging.error("The input {} is not in the accepted keywords {}".format(userInput, keywords))
        raise Exception("The input {} is not in the accepted keywords {}".format(userInput, keywords))
    else:
        socket = Socket((ip, port))
        query = getattr(socket, userInput)
        if filter:
            if type(filter) == str:
                query = query.filter(filter)
            elif type(filter) == list:
                for eachFilter in filter:
                    query = query.filter(eachFilter)
            else:
                logging.error("The type of filter is not suppported: {}".format(type(filter)))
                raise Exception("The type of filter is not suppported: {}".format(type(filter)))
        if statFilter:
            if type(statFilter) == str:
                query = query.stats(statFilter)
            elif type(statFilter) == list:
                for eachFilter in statFilter:
                    query = query.stats(eachFilter)
            else:
                logging.error("The type of stats filter is not suppported: {}".format(type(filter)))
                raise Exception("The type of stats filter is not suppported: {}".format(type(filter)))
        result = query.call()
    return result


def getDataByUsingRawLQL(ip, port, queryString):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        queryString = queryString[:-1] + 'OutputFormat: json\n\n'
        # [Kien] - 26/12/2018 - Add encode function because Python3 need to encode the string before sending.
        s.send(queryString.encode())
        s.shutdown(socket.SHUT_WR)
        # [Kien] - 15/10/2019 - Hard encoding to "latin1" because some error with "utf-8" from icinga2
        rawdata = s.makefile(encoding="latin1").read()
        if not rawdata:
            return []
        data = json.loads(rawdata)
        return data
    finally:
        s.close()


def sendCommand(ip, port, command):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        if command[-1] == "\n":
            command = command + "ResponseHeader: fixed16\n\n"
        else:
            command = command + "\nResponseHeader: fixed16\n\n"
        s.send(command.encode())
        s.shutdown(socket.SHUT_WR)
        rawdata = s.makefile().read()
        if not rawdata:
            return 452
        status_code = rawdata[0:3]
        if status_code.isdigit():
            status_code = int(status_code)
        return status_code
    finally:
        s.close()


if __name__ == "__main__":
    pass
    # print getInfos('localhost', 6558, 'services', ['state = 3', 'host_name = AGG01', 'description ~ FPC'], 'host_name', 'description', 'state', 'in_notification_period')
    print(getInfos('10.98.0.116', 6558, 'hosts', ['display_name = bot1_AGG21'], 'display_name', 'state'))
    # print getCount('localhost', 6558, 'services', None, ['state = 0', 'state = 1', 'state = 2'])
    # print(getDataByUsingRawLQL('10.98.0.116', 6558, "GET services\nColumns: display_name host_name host_groups groups\nFilter: host_groups >= linux-servers\nFilter: groups >= ping\n\n"))
    # import time
    # t = int(time.time())
    # command = "COMMAND [{}] SCHEDULE_FORCED_SVC_CHECK;AGG01;IfCRC-ge-0/0/1;{}".format(t, t)
    # command = "COMMAND [{}] ENABLE_SVC_NOTIFICATIONS;AGG03;IfCRC-ge-0/0/1".format(t)
    # command = "COMMAND [{}] DISABLE_SVC_NOTIFICATIONS;AGG03;IfCRC-ge-0/0/1".format(t)
    # command = "COMMAND [{}] SCHEDULE_FORCED_HOST_CHECK;AGG03;{}".format(t, t)
    # command = "COMMAND [{}] ENABLE_HOST_NOTIFICATIONS;AGG01".format(t)
    # command = "COMMAND [{}] DISABLE_HOST_NOTIFICATIONS;AGG01".format(t)
    # print(command)
    # print(sendCommand('10.98.0.116', 6558, command))