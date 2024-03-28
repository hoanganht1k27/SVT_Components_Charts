from __future__ import print_function
import easysnmp
import logging
import os
import re

def getIfindexFromInterfaceName(host, community, ifName):
    """
    This function gets the interface index from the interface name
    :param host: host name or host ip
    :param community: community name
    :param ifName: interface name
    :return:
    -1 if the interface name is not exist,
    -2 if the session can not be established
    ifindex if success (type: int)
    """
    if_index = -1
    try:
        sess = easysnmp.Session(version=2, hostname=host, community=community, timeout=1, retries=1)
        system_items = sess.walk('ifDescr')

        for item in system_items:
            if ifName == item.value:
                if_index = item.oid_index
                break
    except:
        if_index = -2
    return if_index

def getIfindexFromOperatingDescription(host, community, componentName):
    """
    This function gets the interface index from the component name via Juniper Operating description
    :param host: host name or host ip
    :param community: community name
    :param componentName: the component name
    :return:
    -1 if the interface name is not exist,
    -2 if the session can not be established
    ifindex if success (format: a.b.c.d)
    """
    if_index = -1
    try:
        sess = easysnmp.Session(version=2, hostname=host, community=community, timeout=1, retries=1)
        system_items = sess.walk('1.3.6.1.4.1.2636.3.1.13.1.5') #the Juniper Operating description code is : 1.3.6.1.4.1.2636.3.1.13.1.5
        oid = ""
        for item in system_items:
            if componentName == item.value:
                oid = item.oid
                break
        if "enterprises" in oid:
            oid = oid.replace('enterprises', '1.3.6.1.4.1')
        if oid == "":
            if_index = -1
        else:
            if_index = oid[len('1.3.6.1.4.1.2636.3.1.13.1.5')+1:]
    except:
        if_index = -2
    return if_index

def constructFullOID(listOID, ifindex):
    for i in range(len(listOID)):
        if listOID[i][0] != ".":
            listOID[i] = "." + listOID[i]
        if listOID[i][-1] != ".":
            listOID[i] = listOID[i] + "."
        listOID[i] = listOID[i] + ifindex
    return listOID

def writePerformanceData(listLabel, dictValue, warningDict = None, criticalDict = None, minDict = None, maxDict = None):
    """
    This function print the performance data
    :param listLabel: List of data which user want to write as performance data
    :param dictValue: List measurement data
    :param warningDict: The warning threshold dictionary
    :param criticalDict: The critical threshold dictionary
    :param minDict: The minimal value dictionary
    :param maxDict: The maximal value dictionary
    :return:
    """
    #Verify the input - Start
    if type(listLabel)!=list or type(dictValue)!=dict or len(listLabel)==0 or len(dictValue)==0:
        logging.error("The input function error, can't write performance data")
        raise Exception("The input function error, can't write performance data")
    if not set(listLabel).issubset(set(dictValue.keys())):
        logging.warning("Error list is NOT mapping with the value dictionary")
        raise Exception("Error list is NOT mapping with the value dictionary")
    if warningDict:
        if type(warningDict)!=dict:
            logging.error("The input function error, can't write performance data")
            raise Exception("The input function error, can't write performance data")
        if not set(listLabel).issubset(set(warningDict.keys())):
            logging.warning("Error list is NOT mapping with the warning dictionary")
            raise Exception("Error list is NOT mapping with the warning dictionary")
    if criticalDict:
        if type(criticalDict)!=dict:
            logging.error("The input function error, can't write performance data")
            raise Exception("The input function error, can't write performance data")
        if not set(listLabel).issubset(set(criticalDict.keys())):
            logging.warning("Error list is NOT mapping with the critical dictionary")
            raise Exception("Error list is NOT mapping with the critical dictionary")
    if minDict:
        if type(minDict)!=dict:
            logging.error("The input function error, can't write performance data")
            raise Exception("The input function error, can't write performance data")
        if not set(listLabel).issubset(set(minDict.keys())):
            logging.warning("Error list is NOT mapping with the minimal value dictionary")
            raise Exception("Error list is NOT mapping with the minimal value dictionary")
    if maxDict:
        if type(maxDict)!=dict:
            logging.error("The input function error, can't write performance data")
            raise Exception("The input function error, can't write performance data")
        if not set(listLabel).issubset(set(maxDict.keys())):
            logging.warning("Error list is NOT mapping with the maximal value dictionary")
            raise Exception("Error list is NOT mapping with the maximal value dictionary")
    # Verify the input - End
    for each in listLabel:
        # Write performance data
        # Format: |'label'=value[UOM];[warn];[crit];[min];[max]
        performanceData = "|'{}'={};".format(each, dictValue[each])
        if warningDict:
            if warningDict[each]:
            #If list element is different NONE value
                performanceData += "{};".format(warningDict[each])
            else:
                performanceData += ";"
        else:
            #If warningDict == NONE
            performanceData += ";"
        if criticalDict:
            if criticalDict[each]:
                performanceData += "{};".format(criticalDict[each])
            else:
                performanceData += ";"
        else:
            # If criticalDict == NONE
            performanceData += ";"
        if minDict:
            if minDict[each]:
                performanceData += "{};".format(minDict[each])
            else:
                performanceData += ";"
        else:
            #If minDict == None
            performanceData += ";"
        if maxDict:
            if maxDict[each]:
                performanceData += "{}".format(maxDict[each])
        print (performanceData)
    return 0

def SNMPGenerateConfig(hostname, community, OIDPrefix, file=None, choice=None, userFilterIndex=None, userFilterValue=None, excludedIndex=None, excludedValue=None, priority = "inclusive"):
    '''
    This function shall filter the result from "SNMP walk" command with the user input filter and excluded user input. This function
    also accept the filter from the file (For example: the physical interface from the netconfig)
    :param hostname: hostname
    :param community: community to access SNMP
    :param OIDPrefix: OID prefix
    :param file: file path if you need to filter from other source
    :param choice: choose between ["snmp_index" and "name"]
    :param userFilterIndex: the index filter from user (type:list)
    :param userFilterValue: the value filter from user (type:list)
    :param excludedIndex: the excluded index (type:list)
    :param excludedValue: the excluded value (type:list)
    :return: a list of dictionary in the format [{"snmp_index": value, "name": value}, ...]
    '''
    # Read content file (key list or value list) - Start
    listFromFile = list()
    if file != None:
        if os.path.isfile(file):
            with open(file, 'r') as infile:
                for line in infile:
                    listFromFile.append(line.replace('\n', ''))
        else:
            logging.error("The file is not existed!")
            raise Exception("The file is not existed!")
    # Read file content (key list or value list) - End
    # Use SNMP walk to get data - Start
    SNMPwalkdata = list()
    type = -1
    session = easysnmp.Session(version=2, hostname=hostname, community=community, timeout=1, retries=1)
    system_items = list()
    try:
        system_items = session.walk(OIDPrefix)
    except Exception as e:
        logging.error("Session error due to: %s" % str(e))
        raise Exception("Session error due to: %s" % str(e))
    if len(system_items) == 0:
        logging.warning("The OID input is not found")
    else:
        if system_items[0].oid_index != '':
            # in the case standard MIB, oid_index is different None
            type = 0
        else:
            type = 1
    if type == 0:
        #Standard MIB
        for item in system_items:
            SNMPwalkdata.append({"name":item.value, "snmp_index":item.oid_index})
    if type == 1:
        # Vendor'MIB
        #Delete the common prefix. Wanring: this work can lead to an error to detect oid index in the case
        #we don't have enough of result. For example, if the "snmp walk" returns only 2 points: x.x.x.7.1.0.0
        # and x.x.x.7.2.0.0, although the true index is "7.x.x.x" but because the "7" is common, this work leads only
        #"1.0.0" and "2.0.0" as index.
        listOID = list()
        for item in system_items:
            listOID.append(item.oid)
        commonPrefix = os.path.commonprefix(listOID)
        for item in system_items:
            SNMPwalkdata.append({"name":item.value, "snmp_index":item.oid.replace(commonPrefix, '')})
    # Use SNMP walk to get data - End
    #Filter the SNMP walk data by file content - Start
    listFilter = list()
    if len(listFromFile) != 0:
        if choice == "snmp_index":
            for eachData in SNMPwalkdata:
                for eachIndex in listFromFile:
                    #Reversion 1.1 - 2018-12-20 - Fix in HAITI
                    if eachIndex == eachData["snmp_index"]:
                        listFilter.append(eachData)
                        break
        elif choice == "name":
            for eachData in SNMPwalkdata:
                for eachValue in listFromFile:
                    #Reversion 1.1 - 2018-12-20 - Fix in HAITI
                    if eachValue == eachData["name"]:
                        listFilter.append((eachData))
                        break
        elif choice == None:
            logging.info("Don't use the filter from file")
        else:
            logging.error("Unknown choice: {}".format(choice))
    else:
        logging.warning("The file content is empty")
        listFilter = SNMPwalkdata
    # Filter the SNMP walk data by file content - End
    # Filter by user input - Start
    reducedList = list()
    if priority.lower() == "inclusive":
        for eachItem in listFilter:
            found = False
            if userFilterIndex:
                for eachIndexFilter in userFilterIndex:
                    # [Kien] - 09/01/2019 - Replace substring check by regex
                    if "^" in eachIndexFilter:
                        if re.match(eachIndexFilter, eachItem["snmp_index"]):
                        #if eachIndexFilter in eachItem["snmp_index"]:
                            found = True
                            break
                        else:
                            pass
                    else:
                        if eachIndexFilter in eachItem["snmp_index"]:
                            found = True
                            break
            if userFilterValue:
                for eachValueFilter in userFilterValue:
                    # [Kien] - 09/01/2019 - Replace substring check by regex
                    if "^" in eachValueFilter:
                        if re.match(eachValueFilter, eachItem["name"]):
                        #if eachValueFilter in eachItem["name"]:
                            found = True
                            break
                        else:
                            pass
                    else:
                        if eachValueFilter in eachItem["name"]:
                            found = True
                            break
            if found == True:
                faulty = False
                if excludedIndex:
                    for eachExcludedIndex in excludedIndex:
                        # [Kien] - 09/01/2019 - Replace substring check by regex
                        if "^" in eachExcludedIndex:
                            if re.match(eachExcludedIndex, eachItem["snmp_index"]):
                            #if eachExcludedIndex in eachItem["snmp_index"]:
                                faulty = True
                                break
                            else:
                                pass
                        else:
                            if eachExcludedIndex in eachItem["snmp_index"]:
                                faulty = True
                                break
                if excludedValue:
                    for eachExcludedValue in excludedValue:
                        # [Kien] - 09/01/2019 - Replace substring check by regex
                        if "^" in eachExcludedValue:
                            if re.match(eachExcludedValue, eachItem["name"]):
                            #if eachExcludedValue in eachItem["name"]:
                                faulty = True
                                break
                            else:
                                pass
                        else:
                            if eachExcludedValue in eachItem["name"]:
                                faulty = True
                                break
                if faulty == False:
                    reducedList.append(eachItem)
            else:
                if userFilterIndex is None and userFilterValue is None:
                    reducedList.append(eachItem)
                else:
                    pass
    # [Kien] - 17/01/2019 - Implement the priority for inclusive and exclusive list according to user requirement.
    elif priority.lower() == "exclusive":
        for eachItem in listFilter:
            faulty = False
            if excludedIndex:
                for eachExcludedIndex in excludedIndex:
                    # [Kien] - 09/01/2019 - Replace substring check by regex
                    if "^" in eachExcludedIndex:
                        if re.match(eachExcludedIndex, eachItem["snmp_index"]):
                        #if eachExcludedIndex in eachItem["snmp_index"]:
                            faulty = True
                            break
                        else:
                            pass
                    else:
                        if eachExcludedIndex in eachItem["snmp_index"]:
                            faulty = True
                            break
            if excludedValue:
                for eachExcludedValue in excludedValue:
                    if "^" in eachExcludedValue:
                        if re.match(eachExcludedValue, eachItem["name"]):
                        #if eachExcludedValue in eachItem["name"]:
                            faulty = True
                            break
                        else:
                            pass
                    else:
                        if eachExcludedValue in eachItem["name"]:
                            faulty = True
                            break
            if faulty == False:
                found = False
                if userFilterIndex:
                    for eachIndexFilter in userFilterIndex:
                        if "^" in eachIndexFilter:
                            if re.match(eachIndexFilter, eachItem["snmp_index"]):
                                found = True
                                break
                            else:
                                pass
                        else:
                            if eachIndexFilter in eachItem["snmp_index"]:
                                found = True
                                break
                if userFilterValue:
                    for eachValueFilter in userFilterValue:
                        if "^" in eachValueFilter:
                            if re.match(eachValueFilter, eachItem["name"]):
                                found = True
                                break
                            else:
                                pass
                        else:
                            if eachValueFilter in eachItem["name"]:
                                found = True
                                break
                if found == True:
                    reducedList.append(eachItem)
                else:
                    if userFilterIndex is None and userFilterValue is None:
                        reducedList.append(eachItem)
                    else:
                        pass
    else:
        logging.warning("The priority is not 'inclusive' or 'exclusive'")
        raise Exception("The priority is not 'inclusive' or 'exclusive'")
    # Filter by user input - End
    return reducedList
"""
def valueGenerator(source, capture, reducedList):
    '''
    This function generates the "name"
    :param source: choose between ["snmp_index", "name"]
    :param capture: the regex expression. For example: to get the 2nd character in string '7.1.0.0', we use "7\.(.*)\..\.."
    :param reducedList: the list of dict in the following format: [{"snmp_index": value, "name": value}]
    :return: the list of dict whose element pass the regex expression, in the following format:[{"snmp_index": value, "name": value}]
    '''
    import re
    resultList = list()
    regex = re.compile(capture)
    if source == "snmp_index":
        for eachItem in reducedList:
            match = regex.search(eachItem["snmp_index"])
            if match == None:
                logging.debug("The SNMP index {} is not mapping with the capture {}".format(eachItem["snmp_index"], capture))
            else:
                resultList.append({"name":match.group(1), "snmp_index":eachItem["snmp_index"]})
    elif source == "name":
        for eachItem in reducedList:
            match = regex.search(eachItem["name"])
            if match == None:
                logging.debug("The SNMP item name {} is not mapping with the capture {}".format(eachItem["name"], capture))
            else:
                resultList.append({"name": match.group(1), "snmp_index": eachItem["snmp_index"]})
    else:
        logging.error("Please check your choice {}, choose between snmp_index or name".format(source))
        raise Exception("Please check your choice {}, choose between snmp_index or name".format(source))
    return resultList
"""

def getInterfaceNameAndInterfaceIndex(host, community, include_hostname=True):
    '''
    This function get Interface name from Interface index
    :param host: host name or host IP
    :param community: community name to connect the host
    :return: - empty string if there are no host name correspond to the interface index
             - "Error" string if the SNMP connection can NOT be established
             - The mapping of interface name and IFindex if successful
    '''
    try:
        sess = easysnmp.Session(version=2, hostname=host, community=community, timeout=1, retries=1)
        system_items = sess.walk('ifDescr')
        hostname = CHECK_SNMP_HOSTNAME(host, community)
        IfNameIndex = []
        if include_hostname == True:
            for item in system_items:
                IfNameIndex.append({"hostname": hostname, "address": host , "interface_name": item.value, "interface_index": item.oid_index})
        else:
            for item in system_items:
                IfNameIndex.append({"address": host , "interface_name": item.value, "interface_index": item.oid_index})
    except:
        IfNameIndex = "Error"
    return IfNameIndex


def getAliveInterface(host, community):
    '''
    This function get the interface which has status is up and has interface description
    :param host: host name or host IP
    :param community: community to connect host via SNMP
    :return: The list of alive interface
    '''
    listAliveInterface = list()
    try:
        sess = easysnmp.Session(version=2, hostname=host, community=community, timeout=1, retries=1)
        # Get interface Description - Start
        system_items = sess.walk('ifAlias')
        IfDescription = dict()
        for item in system_items:
            if item.value != "":
                IfDescription[item.oid_index] = item.value
        # Get interface Description - End
        # Get interface name and interface index - Start
        system_items = sess.walk('ifDescr')
        IfName = dict()
        for item in system_items:
            IfName[item.oid_index] = item.value
        # Get interface name and interface index - End
        # [Kien] - 08/01/2019 - Remove the admin status
        for eachIfindex in IfDescription.keys():
            listAliveInterface.append(IfName[eachIfindex])
    except Exception as e:
        logging.error("Error connection to host '{}' with community '{}'".format(host, community))
        logging.exception(e)
    return listAliveInterface



def CHECK_SNMP_HOSTNAME(hostIP, community):
    hostname = ""
    try:
        sess = easysnmp.Session(version=2, hostname=hostIP, community=community, timeout=1, retries=1)
        system_items = sess.walk('sysName')
        hostname = system_items[0].value
    except Exception as e:
        logging.error(e)
        hostname = ""
    return hostname


def GET_SNMP_VALUES_FROM_LIST_OID(hostIP, community, list_full_oid):
    result = dict()
    sess = easysnmp.Session(version=2, hostname=hostIP, community=community, timeout=1, retries=1)
    for oid_full in list_full_oid:
        snmp_result = 'None'
        try:
            snmp_result = sess.get(oid_full).value
        except Exception as e:
            logging.error(e)
        result[oid_full] = snmp_result
    return result


def snmp_discovery(hostname, community, OIDPrefix):
    """
    This function is used for BGP, because it fall in the note of function "SNMPGenerateConfig": Delete the common
    prefix. Wanring: this work can ...
    :param hostname: hostname
    :param community: community
    :param OIDPrefix: OID prefix
    :return: The snmp name and snmp index
    """
    snmp_walk_data = list()
    session = easysnmp.Session(version=2, hostname=hostname, community=community, timeout=1, retries=1)
    system_items = list()
    type_data = 0
    try:
        system_items = session.walk(OIDPrefix)
    except Exception as e:
        logging.error("Session error due to: %s" % str(e))
        raise Exception("Session error due to: %s" % str(e))
    if len(system_items) == 0:
        logging.warning("The OID input is not found")
    else:
        if system_items[0].oid_index != '':
            # in the case standard MIB, oid_index is different None
            type_data = 0
        else:
            type_data = 1
    if type_data == 0:
        #Standard MIB
        for item in system_items:
            snmp_walk_data.append({"name": item.value, "snmp_index": item.oid_index})
    if type_data == 1:
        for item in system_items:
            snmp_index = item.oid.replace('mib-2', '1.3.6.1.2.1')
            snmp_index = snmp_index.replace(OIDPrefix, '', 1)
            if snmp_index[0] == '.':
                snmp_index = snmp_index[1:]
            snmp_walk_data.append({"name": item.value, "snmp_index": snmp_index})
    return snmp_walk_data


def constructConfig():
    #To be defined
    pass

def constructAnsible():
    #To be defined
    pass


def get_bulk(hostname, community, oids_prefix, oids_index, kwargs):
    result = []
    session = easysnmp.Session(hostname=hostname, community=community, version=2, **kwargs)
    for oid in oids_index:
        temp_list = list()
        temp_dict = dict()
        for key, value in oids_prefix.items():
            if value[-1] == ".":
                temp_list.append(value[-1] + "." + oid)
            else:
                temp_list.append(value + "." + oid)
        logging.debug("Collect snmpget for index: {}".format(oid))
        result_snmp = session.get(temp_list)
        keys = list(oids_prefix.keys())
        for i in range(len(keys)):
            temp_dict[keys[i]] = result_snmp[i].value
        ifname = session.get('1.3.6.1.2.1.2.2.1.2.' + oid) #Get interface name from ifDesc
        temp_dict["ID"] = ifname.value
        result.append(temp_dict)
    return result

if __name__ == '__main__':
    #print getAliveInterface("10.96.10.37", "public")
    from pprint import pprint
    #pprint(SNMPGenerateConfig("10.98.100.12", "Viettel2016", "ifDescr", None, "name", None, ["xe", "ae", "ge", "et"], None, [".", "^ae1*"]))
    # pprint(GET_SNMP_VALUES_FROM_LIST_OID('10.96.10.13', 'public', ['1.3.6.1.4.1.2636.3.1.13.1.5.7.1.0.0',
    #                                                                '1.3.6.1.4.1.2636.3.1.13.1.5.7.2.0.0']))
    pprint(snmp_discovery('10.96.10.16', 'public', '1.3.6.1.2.1.15.3.1.1'))
    pprint(snmp_discovery('10.96.10.16', 'public', '1.3.6.1.2.1.15.3.1.5'))
    pprint(SNMPGenerateConfig("10.96.10.37", "public", "1.3.6.1.4.1.2636.3.2.5.1.1", None, "snmp_index"))
