from pysnmp.hlapi import *
import logging
import re
import os
import socket

from ansible.module_utils import SNMPLibrary
from collections import defaultdict
from jnpr.junos import Device
from lxml import etree

model_mapping = {
    '1.3.6.1.4.1.2636.1.1.1.2.1': 'M40',
    '1.3.6.1.4.1.2636.1.1.1.2.2': 'M20',
    '1.3.6.1.4.1.2636.1.1.1.2.3': 'M160',
    '1.3.6.1.4.1.2636.1.1.1.2.4': 'M10',
    '1.3.6.1.4.1.2636.1.1.1.2.5': 'M5',
    '1.3.6.1.4.1.2636.1.1.1.2.6': 'T640',
    '1.3.6.1.4.1.2636.1.1.1.2.7': 'T320',
    '1.3.6.1.4.1.2636.1.1.1.2.8': 'M40e',
    '1.3.6.1.4.1.2636.1.1.1.2.9': 'M320',
    '1.3.6.1.4.1.2636.1.1.1.2.10': 'M7i',
    '1.3.6.1.4.1.2636.1.1.1.2.11': 'M10i',
    '1.3.6.1.4.1.2636.1.1.1.2.13': 'J2300',
    '1.3.6.1.4.1.2636.1.1.1.2.14': 'J4300',
    '1.3.6.1.4.1.2636.1.1.1.2.15': 'J6300',
    '1.3.6.1.4.1.2636.1.1.1.2.16': 'IRM',
    '1.3.6.1.4.1.2636.1.1.1.2.17': 'TX',
    '1.3.6.1.4.1.2636.1.1.1.2.18': 'M120',
    '1.3.6.1.4.1.2636.1.1.1.2.19': 'J4350',
    '1.3.6.1.4.1.2636.1.1.1.2.20': 'J6350',
    '1.3.6.1.4.1.2636.1.1.1.2.21': 'MX960',
    '1.3.6.1.4.1.2636.1.1.1.2.22': 'J4320',
    '1.3.6.1.4.1.2636.1.1.1.2.23': 'J2320',
    '1.3.6.1.4.1.2636.1.1.1.2.24': 'J2350',
    '1.3.6.1.4.1.2636.1.1.1.2.25': 'MX480',
    '1.3.6.1.4.1.2636.1.1.1.2.26': 'SRX5800',
    '1.3.6.1.4.1.2636.1.1.1.2.27': 'T1600',
    '1.3.6.1.4.1.2636.1.1.1.2.28': 'SRX5600',
    '1.3.6.1.4.1.2636.1.1.1.2.29': 'MX240',
    '1.3.6.1.4.1.2636.1.1.1.2.30': 'EX3200',
    '1.3.6.1.4.1.2636.1.1.1.2.31': 'EX4200',
    '1.3.6.1.4.1.2636.1.1.1.2.32': 'EX8208',
    '1.3.6.1.4.1.2636.1.1.1.2.33': 'EX8216',
    '1.3.6.1.4.1.2636.1.1.1.2.34': 'SRX3600',
    '1.3.6.1.4.1.2636.1.1.1.2.35': 'SRX3400',
    '1.3.6.1.4.1.2636.1.1.1.2.36': 'SRX210',
    '1.3.6.1.4.1.2636.1.1.1.2.37': 'TXP',
    '1.3.6.1.4.1.2636.1.1.1.2.38': 'JCS',
    '1.3.6.1.4.1.2636.1.1.1.2.39': 'SRX240',
    '1.3.6.1.4.1.2636.1.1.1.2.40': 'SRX650',
    '1.3.6.1.4.1.2636.1.1.1.2.41': 'SRX100',
    '1.3.6.1.4.1.2636.1.1.1.2.42': 'LN1000V',
    '1.3.6.1.4.1.2636.1.1.1.2.43': 'EX2200',
    '1.3.6.1.4.1.2636.1.1.1.2.44': 'EX4500',
    '1.3.6.1.4.1.2636.1.1.1.2.45': 'FXSeries',
    '1.3.6.1.4.1.2636.1.1.1.2.46': 'IBM4274M02J02M',
    '1.3.6.1.4.1.2636.1.1.1.2.47': 'IBM4274M06J06M',
    '1.3.6.1.4.1.2636.1.1.1.2.48': 'IBM4274M11J11M',
    '1.3.6.1.4.1.2636.1.1.1.2.49': 'SRX1400',
    '1.3.6.1.4.1.2636.1.1.1.2.50': 'IBM4274S58J58S',
    '1.3.6.1.4.1.2636.1.1.1.2.51': 'IBM4274S56J56S',
    '1.3.6.1.4.1.2636.1.1.1.2.52': 'IBM4274S36J36S',
    '1.3.6.1.4.1.2636.1.1.1.2.53': 'IBM4274S34J34S',
    '1.3.6.1.4.1.2636.1.1.1.2.54': 'IBM427348EJ48E',
    '1.3.6.1.4.1.2636.1.1.1.2.55': 'IBM4274E08J08E',
    '1.3.6.1.4.1.2636.1.1.1.2.56': 'IBM4274E16J16E',
    '1.3.6.1.4.1.2636.1.1.1.2.57': 'MX80',
    '1.3.6.1.4.1.2636.1.1.1.2.58': 'SRX220',
    '1.3.6.1.4.1.2636.1.1.1.2.59': 'EXXRE',
    '1.3.6.1.4.1.2636.1.1.1.2.60': 'QFXInterconnect',
    '1.3.6.1.4.1.2636.1.1.1.2.61': 'QFXNode',
    '1.3.6.1.4.1.2636.1.1.1.2.62': 'QFXJVRE',
    '1.3.6.1.4.1.2636.1.1.1.2.63': 'EX4300',
    '1.3.6.1.4.1.2636.1.1.1.2.64': 'SRX110',
    '1.3.6.1.4.1.2636.1.1.1.2.65': 'SRX120',
    '1.3.6.1.4.1.2636.1.1.1.2.66': 'MAG8600',
    '1.3.6.1.4.1.2636.1.1.1.2.67': 'MAG6611',
    '1.3.6.1.4.1.2636.1.1.1.2.68': 'MAG6610',
    '1.3.6.1.4.1.2636.1.1.1.2.69': 'PTX5000',
    '1.3.6.1.4.1.2636.1.1.1.2.71': 'IBM0719J45E',
    '1.3.6.1.4.1.2636.1.1.1.2.72': 'IBMJ08F',
    '1.3.6.1.4.1.2636.1.1.1.2.73': 'IBMJ52F',
    '1.3.6.1.4.1.2636.1.1.1.2.74': 'EX6210',
    '1.3.6.1.4.1.2636.1.1.1.2.75': 'DellJFX3500',
    '1.3.6.1.4.1.2636.1.1.1.2.76': 'EX3300',
    '1.3.6.1.4.1.2636.1.1.1.2.77': 'DELLJSRX3600',
    '1.3.6.1.4.1.2636.1.1.1.2.78': 'DELLJSRX3400',
    '1.3.6.1.4.1.2636.1.1.1.2.79': 'DELLJSRX1400',
    '1.3.6.1.4.1.2636.1.1.1.2.80': 'DELLJSRX5800',
    '1.3.6.1.4.1.2636.1.1.1.2.81': 'DELLJSRX5600',
    '1.3.6.1.4.1.2636.1.1.1.2.82': 'QFXSwitch',
    '1.3.6.1.4.1.2636.1.1.1.2.83': 'T4000',
    '1.3.6.1.4.1.2636.1.1.1.2.84': 'QFX3000',
    '1.3.6.1.4.1.2636.1.1.1.2.85': 'QFX5000',
    '1.3.6.1.4.1.2636.1.1.1.2.86': 'SRX550',
    '1.3.6.1.4.1.2636.1.1.1.2.87': 'ACX',
    '1.3.6.1.4.1.2636.1.1.1.2.88': 'MX40',
    '1.3.6.1.4.1.2636.1.1.1.2.89': 'MX10',
    '1.3.6.1.4.1.2636.1.1.1.2.90': 'MX5',
    '1.3.6.1.4.1.2636.1.1.1.2.91': 'QFXMInterconnect',
    '1.3.6.1.4.1.2636.1.1.1.2.92': 'EX4550',
    '1.3.6.1.4.1.2636.1.1.1.2.93': 'MX2020',
    '1.3.6.1.4.1.2636.1.1.1.2.94': 'Vseries',
    '1.3.6.1.4.1.2636.1.1.1.2.95': 'LN2600',
    '1.3.6.1.4.1.2636.1.1.1.2.96': 'FireflyPerimeter',
    '1.3.6.1.4.1.2636.1.1.1.2.97': 'MX104',
    '1.3.6.1.4.1.2636.1.1.1.2.98': 'PTX3000',
    '1.3.6.1.4.1.2636.1.1.1.2.99': 'MX2010',
    '1.3.6.1.4.1.2636.1.1.1.2.100': 'QFX3100',
    '1.3.6.1.4.1.2636.1.1.1.2.101': 'LN2800',
    '1.3.6.1.4.1.2636.1.1.1.2.102': 'EX9214',
    '1.3.6.1.4.1.2636.1.1.1.2.103': 'EX9208',
    '1.3.6.1.4.1.2636.1.1.1.2.104': 'EX9204',
    '1.3.6.1.4.1.2636.1.1.1.2.105': 'SRX5400',
    '1.3.6.1.4.1.2636.1.1.1.2.106': 'IBM4274S54J54S',
    '1.3.6.1.4.1.2636.1.1.1.2.107': 'DELLJSRX5400',
    '1.3.6.1.4.1.2636.1.1.1.2.108': 'VMX',
    '1.3.6.1.4.1.2636.1.1.1.2.109': 'EX4600',
    '1.3.6.1.4.1.2636.1.1.1.2.110': 'VRR',
    '1.3.6.1.4.1.2636.1.1.1.2.112': 'OCPAcc',
    '1.3.6.1.4.1.2636.1.1.1.2.113': 'ACX1000',
    '1.3.6.1.4.1.2636.1.1.1.2.114': 'ACX2000',
    '1.3.6.1.4.1.2636.1.1.1.2.115': 'ACX1100',
    '1.3.6.1.4.1.2636.1.1.1.2.116': 'ACX2100',
    '1.3.6.1.4.1.2636.1.1.1.2.117': 'ACX2200',
    '1.3.6.1.4.1.2636.1.1.1.2.118': 'ACX4000',
    '1.3.6.1.4.1.2636.1.1.1.2.119': 'ACX500AC',
    '1.3.6.1.4.1.2636.1.1.1.2.120': 'ACX500DC',
    '1.3.6.1.4.1.2636.1.1.1.2.121': 'ACX500OAC',
    '1.3.6.1.4.1.2636.1.1.1.2.122': 'ACX500ODC',
    '1.3.6.1.4.1.2636.1.1.1.2.123': 'ACX500OPOEAC',
    '1.3.6.1.4.1.2636.1.1.1.2.124': 'ACX500OPOEDC',
    '1.3.6.1.4.1.2636.1.1.1.2.125': 'SatelliteDevice',
    '1.3.6.1.4.1.2636.1.1.1.2.126': 'ACX5048',
    '1.3.6.1.4.1.2636.1.1.1.2.127': 'ACX5096',
    '1.3.6.1.4.1.2636.1.1.1.2.128': 'LN1000CC',
    '1.3.6.1.4.1.2636.1.1.1.2.129': 'VSRX',
    '1.3.6.1.4.1.2636.1.1.1.2.130': 'PTX1000',
    '1.3.6.1.4.1.2636.1.1.1.2.131': 'EX3400',
    '1.3.6.1.4.1.2636.1.1.1.2.132': 'EX2300',
    '1.3.6.1.4.1.2636.1.1.1.2.133': 'SRX300',
    '1.3.6.1.4.1.2636.1.1.1.2.134': 'SRX320',
    '1.3.6.1.4.1.2636.1.1.1.2.135': 'SRX340',
    '1.3.6.1.4.1.2636.1.1.1.2.136': 'SRX345',
    '1.3.6.1.4.1.2636.1.1.1.2.137': 'SRX1500',
    '1.3.6.1.4.1.2636.1.1.1.2.138': 'NFX',
    '1.3.6.1.4.1.2636.1.1.1.2.139': 'JNP10003',
    '1.3.6.1.4.1.2636.1.1.1.2.140': 'SRX4600',
    '1.3.6.1.4.1.2636.1.1.1.2.141': 'SRX4800',
    '1.3.6.1.4.1.2636.1.1.1.2.142': 'SRX4100',
    '1.3.6.1.4.1.2636.1.1.1.2.143': 'SRX4200',
    '1.3.6.1.4.1.2636.1.1.1.2.144': 'JNP204',
    '1.3.6.1.4.1.2636.1.1.1.2.145': 'MX2008',
    '1.3.6.1.4.1.2636.1.1.1.2.146': 'MXTSR80',
    '1.3.6.1.4.1.2636.1.1.1.2.147': 'PTX10008',
    '1.3.6.1.4.1.2636.1.1.1.2.150': 'PTX10016',
    '1.3.6.1.4.1.2636.1.1.1.2.151': 'EX9251',
    '1.3.6.1.4.1.2636.1.1.1.2.152': 'MX150',
    '1.3.6.1.4.1.2636.1.1.1.2.153': 'JNP10001',
    '1.3.6.1.4.1.2636.1.1.1.2.154': 'MX10008',
    '1.3.6.1.4.1.2636.1.1.1.2.155': 'MX10016',
    '1.3.6.1.4.1.2636.1.1.1.2.156': 'EX9253',
    '1.3.6.1.4.1.2636.1.1.1.2.157': 'JRR200',
    '1.3.6.1.4.1.2636.1.1.1.2.158': 'ACX5448M',
    '1.3.6.1.4.1.2636.1.1.1.2.159': 'ACX5448D',
    '1.3.6.1.4.1.2636.1.1.1.2.160': 'ACX6360OR',
    '1.3.6.1.4.1.2636.1.1.1.2.161': 'ACX6360OX',
    '1.3.6.1.4.1.2636.1.1.1.2.162': 'ACX710',
    '1.3.6.1.4.1.2636.1.1.1.2.163': 'ACX5800',
    '1.3.6.1.4.1.2636.1.1.1.2.164': 'SRX380',
    '1.3.6.1.4.1.2636.1.1.1.2.165': 'EX4400',
    '1.3.6.1.4.1.2636.1.1.1.2.166': 'R6675',
    '1.3.6.1.4.1.2636.1.1.1.2.508': 'EX4650',
    '1.3.6.1.4.1.2636.1.1.1.2.513': 'PTX1000260C',
    '1.3.6.1.4.1.2636.1.1.1.2.523': 'PTX1000380c',
    '1.3.6.1.4.1.2636.1.1.1.2.524': 'PTX10003160c',
    '1.3.6.1.4.1.2636.1.1.1.2.525': 'QFX1000380c',
    '1.3.6.1.4.1.2636.1.1.1.2.526': 'QFX10003160c',
    '1.3.6.1.4.1.2636.1.1.1.2.555': 'PTX1000136mr',
    '1.3.6.1.4.1.2636.1.1.1.2.570': 'PTX10004',
    '1.3.6.1.4.1.2636.1.1.1.2.576': 'ACX753'
}


def rule1(dest, prefix, suffix, temp_list):
    '''
    This rule is used for Routing Engine, CB, PEM, PDM, FPC, SFB, ADC, PSM. e.g snmp_index: 7.[2].0.0 => name: FPC1
    :param dest: the key to assign the matched value
    :param prefix: The prefix string of the component
    :param suffix: The suffix string of the component
    :param temp_list: The result from "valueGenerator" function
    :return:
    '''
    for i in range(len(temp_list)):
        temp_list[i][dest] = prefix + str(int(temp_list[i][dest]) - 1) + suffix
    return temp_list

def rule2(dest, prefix, suffix, temp_list):
    '''
    This rule is used for Fan Tray, MIC, PIC
    :param dest: the key to assign the matched value
    :param prefix: The prefix string of the component
    :param suffix: The suffix string of the component
    :param temp_list: The result from "valueGenerator" function
    :return:
    '''
    for i in range(len(temp_list)):
        temp_list[i][dest] = prefix + str(temp_list[i][dest]).replace(" ", "_") + suffix
    return temp_list


def valueGenerator(item_name_generator, reducedList):
    '''
    This function generates the filtered key
    :param item_name_generator: dictionary which contains the following keys:
        source: The key which its values will be regexed
        capture: the regex expression. For example: to get the 2nd character in string '7.1.0.0', we use "7\.(.*)\..\.."
        dest: The key which its values will be replaced by regex
        function: string representation of the function to perform conversion
        prefix: prefix of the component to perform regex and conversion
        suffix: suffix of the component to perform regex and conversion
    :param reducedList: the result from individual discovery function in form of list of dicts
    :return: the list of dicts which its elements passed the regex expression
    '''
    resultList = list()
    if item_name_generator is None:
        logging.debug("item_name_generator is empty")
        resultList = reducedList
    else:  
        if (not isinstance(item_name_generator, list) or 
            not all(isinstance(elem, dict) for elem in item_name_generator)):
            logging.error("item_name_generator must be a list of dictionaries")
            pass
        else:
            for elem_dict in item_name_generator:
                source = elem_dict["source"]
                dest = elem_dict["dest"]
                logging.debug("Regex input for component mapping: {}".format(elem_dict["capture"]))
                capture = elem_dict["capture"].replace("\\\\", "\\")
                logging.debug("Regex input for component mapping: {}".format(capture))
                function = elem_dict["function"]
                prefix = elem_dict["prefix"]
                suffix = elem_dict["suffix"]               
                regex = re.compile(capture)
                if capture == "nothing":
                    resultList = reducedList 
                for eachItem in reducedList:
                    if source not in eachItem:
                        logging.error("{} does not exist as key in element {} of reducedList".format(source, eachItem))
                        continue
                    else:
                        match = regex.search(eachItem[source])
                        if match == None:
                            logging.debug("The source {} is not mapping with the capture {}".format(eachItem[source], capture))
                        elif dest is None or dest == "":
                            logging.warning("Value for dest is empty")
                            continue
                        else:
                            resultItem = {k: v for k, v in eachItem.items() if k != dest}
                            resultItem[dest] = match.group(1)
                            resultList.append(resultItem)                 
                resultList = globals()[function](dest, prefix, suffix, resultList)

    return resultList


###############################################################################
def check_port_open(host, port):
    '''
    Function to check if the input port is open and ready to accept connection 
    :param host: Ip address to check the port.
    :param port: The port number to check.
    :return: True if port is open, otherwise false.
    '''
    result = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    connection = sock.connect_ex((host, port))
    if connection == 0:
        result = True
        sock.shutdown(2)
        sock.close()
    else:
        pass
    return result

def xml_element_to_dict(tree_element):
    '''
    Function to convert an xml tree element to python dictionary
    :param tree_element: lxml.etree._Element, an XML element to convert to dicitonary.
    :return: Equivalent python dictionary from the XML.
    '''
    _dict = {tree_element.tag: {} if tree_element.attrib else None}
    children = list(tree_element)
    if children:
        dd = defaultdict(list)
        for dc in map(xml_element_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        _dict = {tree_element.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if tree_element.attrib:
        _dict[tree_element.tag].update(('@' + k, v)
                        for k, v in tree_element.attrib.items())
    if tree_element.text:
        text = tree_element.text.strip()
        if children or tree_element.attrib:
            if text:
              _dict[tree_element.tag]['#text'] = text
        else:
            _dict[tree_element.tag] = text
    return _dict


def generate_device_to_connect(host_address, username, password, port = 830):
    '''
    Function to generate jnpr.junos.Device based on the open port
    :param host_address: IP address string to check the port.
    :param username: username to authenticate the connection.
    :param password: Password to authenticate the connection.
    :param port: User input port if desired, other than 830, 22, 23. The default is 830.
    :return: jnpr.junos.Device, device with authenticated value to make connection.
    '''
    if not isinstance(port, int):
        port = 830
    device = None
    is_open_user_port = None
    is_open_830 = check_port_open(host_address, 830)
    is_open_22 = check_port_open(host_address, 22)
    is_open_23 = check_port_open(host_address, 23)
    if port not in (830, 23, 22):
        is_open_user_port = check_port_open(host_address, port)
        
    
    if is_open_23 and not is_open_22 and not is_open_830 and not is_open_user_port:
        device = Device(host = host_address,
                        user = username,
                        passwd = password,
                        port = 23,
                        mode = "telnet")
    elif is_open_22 and not is_open_830:
        device = Device(host = host_address,
                        user = username,
                        passwd = password,
                        port = 22) 
    elif not is_open_22 and is_open_830:
        device = Device(host = host_address,
                        user = username,
                        passwd = password,
                        port = 830)    
    elif not is_open_22 and not is_open_830 and is_open_user_port:
        device = Device(host = host_address,
                        user = username,
                        passwd = password,
                        port = port) 
    elif is_open_22 and is_open_830 and is_open_23:
        device = Device(host = host_address,
                        user = username,
                        passwd = password,
                        port = 830)    
    elif is_open_22 and is_open_830 and not is_open_user_port:
        device = Device(host = host_address,
                        user = username,
                        passwd = password,
                        port = 830)    
    else:
        pass

    return device


def rreplace(s, old, new, occurrence):
    '''
    This function replaces the old string by new string from the tail of string to head
    :param s: the input string
    :param old: the old string
    :param new: the new string
    :param occurrence: replace until the number of occurrence reach this parameter
    :return: The replaced string
    '''
    li = s.rsplit(old, occurrence)
    return new.join(li)


def inclusive_value_filter_config(value_filter, listFilter, reducedList):
    for eachItem in listFilter:
        found = False
        if 'userFilterIndex' in value_filter:
            if (not isinstance(value_filter['userFilterIndex'], list) or 
                not all(isinstance(elem, dict) for elem in value_filter['userFilterIndex'])):
                logging.error("userFilterIndex must be a list of dictionaries")
                break
            else:
                for filter_dict in value_filter['userFilterIndex']:
                    filtered_key = filter_dict["filter_key"]
                    filtered_value = filter_dict["filter_value"]   
                    if filtered_key not in eachItem:
                        logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                        break
                    else:
                        for eachIndexFilter in filtered_value:
                            if "^" in eachIndexFilter:
                                if re.match(eachIndexFilter, eachItem[filtered_key]):
                                    found = True
                                    break
                                else:
                                    pass
                            else:
                                if eachIndexFilter in eachItem[filtered_key]:
                                    found = True
                                    break         
        if 'userFilterValue' in value_filter:
            if (not isinstance(value_filter['userFilterValue'], list) or 
                not all(isinstance(elem, dict) for elem in value_filter['userFilterValue'])):
                logging.error("userFilterValue must be a list of dictionaries")
                break
            else:
                for filter_dict in value_filter['userFilterValue']:
                    filtered_key = filter_dict["filter_key"]
                    filtered_value = filter_dict["filter_value"]
                    if filtered_key not in eachItem:
                        logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                        break
                    else:
                        for eachValueFilter in filtered_value:
                            if "^" in eachValueFilter:
                                if re.match(eachValueFilter, eachItem[filtered_key]):
                                    found = True
                                    break
                                else:
                                    pass
                            else:
                                if eachValueFilter in eachItem[filtered_key]:
                                    found = True
                                    break
       
        if found:
            faulty = False
            if 'excludedIndex' in value_filter:
                if (not isinstance(value_filter['excludedIndex'], list) or 
                    not all(isinstance(elem, dict) for elem in value_filter['excludedIndex'])):
                    logging.error("excludedIndex must be a list of dictionaries")
                    break
                else:
                    for filter_dict in value_filter['excludedIndex']:
                        filtered_key = filter_dict["filter_key"]
                        filtered_value = filter_dict["filter_value"]
                        if filtered_key not in eachItem:
                            logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                            break
                        else:
                            for eachExcludedIndex in filtered_value:
                                if "^" in eachExcludedIndex:
                                    if re.match(eachExcludedIndex, eachItem[filtered_key]):
                                        faulty = True
                                        break
                                    else:
                                        pass
                                else:
                                    if eachExcludedIndex in eachItem[filtered_key]:
                                        faulty = True
                                        break

            if 'excludedValue' in value_filter:
                if (not isinstance(value_filter['excludedValue'], list) or 
                    not all(isinstance(elem, dict) for elem in value_filter['excludedValue'])):
                    logging.error("excludedIndex must be a list of dictionaries")
                    break
                else:
                    for filter_dict in value_filter['excludedValue']:
                        filtered_key = filter_dict["filter_key"]
                        filtered_value = filter_dict["filter_value"]
                        if filtered_key not in eachItem:
                            logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                            break
                        else:
                            for eachExcludedValue in filtered_value:
                                if "^" in eachExcludedValue:
                                    if re.match(eachExcludedValue, eachItem[filtered_key]):
                                        faulty = True
                                        break
                                    else:
                                        pass
                                else:
                                    if eachExcludedValue in eachItem[filtered_key]:
                                        faulty = True
                                        break
            if not faulty:
                reducedList.append(eachItem)
        else:
            if 'userFilterIndex' not in value_filter and 'userFilterValue' not in value_filter:
                reducedList.append(eachItem)
            else:
                pass
                
    return reducedList


def exclusive_value_filter_config(value_filter, listFilter, reducedList):
    for eachItem in listFilter:
        faulty = False
        if 'excludedIndex' in value_filter:
            if (not isinstance(value_filter['excludedIndex'], list) or 
                not all(isinstance(elem, dict) for elem in value_filter['excludedIndex'])):
                logging.error("excludedIndex must be a list of dictionaries")
                break
            else:
                for filter_dict in value_filter['excludedIndex']:
                    filtered_key = filter_dict["filter_key"]
                    filtered_value = filter_dict["filter_value"]
                    if filtered_key not in eachItem:
                        logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                        break
                    else:
                        for eachExcludedIndex in filtered_value:
                            if "^" in eachExcludedIndex:
                                if re.match(eachExcludedIndex, eachItem[filtered_key]):
                                    faulty = True
                                    break
                                else:
                                    pass
                            else:
                                if eachExcludedIndex in eachItem[filtered_key]:
                                    faulty = True
                                    break

        if 'excludedValue' in value_filter:
            if (not isinstance(value_filter['excludedValue'], list) or 
                not all(isinstance(elem, dict) for elem in value_filter['excludedValue'])):
                logging.error("excludedValue must be a list of dictionaries")
                break
            else:
                for filter_dict in value_filter['excludedIndex']:
                    filtered_key = filter_dict["filter_key"]
                    filtered_value = filter_dict["filter_value"]
                    if filtered_key not in eachItem:
                        logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                        break
                    else:
                        for eachExcludedValue in filtered_value:
                            if "^" in eachExcludedValue:
                                if re.match(eachExcludedValue, eachItem[filtered_key]):
                                    faulty = True
                                    break
                                else:
                                    pass
                            else:
                                if eachExcludedValue in eachItem[filtered_key]:
                                    faulty = True
                                    break   
        if not faulty:
            found = False
            if 'userFilterIndex' in value_filter:
                if (not isinstance(value_filter['userFilterIndex'], list) or 
                    not all(isinstance(elem, dict) for elem in value_filter['userFilterIndex'])):
                    logging.error("userFilterIndex must be a list of dictionaries")
                    break
                else:
                    for filter_dict in value_filter['userFilterIndex']:
                        filtered_key = filter_dict["filter_key"]
                        filtered_value = filter_dict["filter_value"]   
                        if filtered_key not in eachItem:
                            logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                            break
                        else:
                            for eachIndexFilter in filtered_value:
                                if "^" in eachIndexFilter:
                                    if re.match(eachIndexFilter, eachItem[filtered_key]):
                                        found = True
                                        break
                                    else:
                                        pass
                                else:
                                    if eachIndexFilter in eachItem[filtered_key]:
                                        found = True
                                        break         
            if 'userFilterValue' in value_filter:
                if (not isinstance(value_filter['userFilterValue'], list) or 
                    not all(isinstance(elem, dict) for elem in value_filter['userFilterValue'])):
                    logging.error("userFilterValue must be a list of dictionaries")
                    break
                else:
                    for filter_dict in value_filter['userFilterValue']:
                        filtered_key = filter_dict["filter_key"]
                        filtered_value = filter_dict["filter_value"]
                        if filtered_key not in eachItem:
                            logging.error("{} does not exist in elements of listFilter".format(filtered_key))
                            break
                        else:
                            for eachValueFilter in filtered_value:
                                if "^" in eachValueFilter:
                                    if re.match(eachValueFilter, eachItem[filtered_key]):
                                        found = True
                                        break
                                    else:
                                        pass
                                else:
                                    if eachValueFilter in eachItem[filtered_key]:
                                        found = True
                                        break
            if found:
                reducedList.append(eachItem)
            else:
                if 'userFilterIndex' not in value_filter and 'userFilterValue' not in value_filter:
                    reducedList.append(eachItem)
                else:
                    pass

    return reducedList


###############################################################################
# Start - Pham - 05/04/2021 - Function to discover interface with optic information
def optic_discovery(host, community, device_username, device_password, device_port, udp_port= 161):
    result = []
    
    device = generate_device_to_connect(host, device_username, device_password, device_port)
    if not device:
        return result
    try:
        device.open(auto_probe=2)
        device.timeout = 60
        
        interface_optic = device.rpc.get_interface_optics_diagnostics_information()
        optic_list = []
        interface_result = xml_element_to_dict(interface_optic)
        for elem in interface_result['interface-information']['physical-interface']:
            optic_list.append(elem['name'])
        
        device_result = []
        for interface_name in optic_list:
            intf = device.rpc.get_interface_information(interface_name=interface_name)
            device_result.append(intf)
    
        device.close()
    
        for intf in device_result:
            interface_dict = xml_element_to_dict(intf)
            intf_info = interface_dict['interface-information']['physical-interface']
            concise_dict = {"name": intf_info["name"], 
                            "snmp_index": intf_info["snmp-index"]}
            result.append(concise_dict)
    
        alive_intf = SNMPLibrary.getAliveInterface(host, community)
        final_result = []
        for _dict in result:
            if _dict['name'] in alive_intf:
                final_result.append(_dict)
        
    except Exception:
        return []

    return final_result
# End - Pham - 05/04/2021

###############################################################################
# Start - TuongVX - 19/08/2021 - Function to discover interface with aps information
def aps_discovery(host, community, device_username, device_password, device_port, udp_port= 161):
    result = []
    device = generate_device_to_connect(host, device_username, device_password, device_port)
    if not device:
        return result
    try:
        device.open(auto_probe=2)
        device.timeout = 60
        interface_aps = device.rpc.get_aps_information()
        interf_result = interface_aps.xpath('//aps-interface/aps-interface-name')
        if interf_result:
            for interf in interf_result:
                name = str(interf.xpath("normalize-space(.)"))
                concise_dict = {"name":name, "snmp_index":True}
                result.append(concise_dict)
    except:
        return result
    return result
# End - TuongVX - 19/08/2021

def qos_discovery(host, udp_port, community, mib_source='', mib_file='JUNIPER-COS-MIB', mib_object='jnxCosIfqQedPkts'):
    resultDict = dict()
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData(community, mpModel=1),
                                                                        UdpTransportTarget((host, udp_port)),
                                                                        ContextData(),
                                                                        ObjectType(ObjectIdentity(mib_file,
                                                                        mib_object).addMibSource(mib_source)),
                                                                        lexicographicMode=False):
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for name, val in varBinds:
                mibSymbol = name.getMibSymbol()
                oidString = str(name)  # Full OID string (can be used with snmpget)
                preFixList = name.getMibNode().getName()  # The prefix
                prefixString = ""
                for prefix in preFixList:
                    prefixString += str(prefix) + "."
                oidString = oidString.replace(prefixString, "", 1)  # Remove the prefix in full OID string
                data = mibSymbol[2]
                if len(data) == 2:
                    resultDict[data[1].prettyPrint()] = oidString.replace(data[0].prettyPrint() + ".", "", 1)
                else:
                    raise Exception("The format data is not OK, the process stop")
    listResult = list()
    for key, value in resultDict.items():
        listResult.append({'name': key, 'snmp_index': value})
    return listResult


def rpm_discovery(host, udp_port, community, mib_source='', mib_file='JUNIPER-RPM-MIB', mib_object='jnxRpmResCalcAverage'):
    listResult = list()
    resultIndex = dict()
    resultDecimalIndex = dict()
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData(community, mpModel=1),
                                                                        UdpTransportTarget((host, udp_port)),
                                                                        ContextData(),
                                                                        ObjectType(ObjectIdentity(mib_file,
                                                                        mib_object).addMibSource(mib_source)),
                                                                        lexicographicMode=False):
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for name, val in varBinds:
                mibSymbol = name.getMibSymbol()
                oidString = str(name)  # Full OID string (can be used with snmpget)
                preFixList = name.getMibNode().getName()  # The prefix
                prefixString = ""
                for prefix in preFixList:
                    prefixString += str(prefix) + "."
                oidString = oidString.replace(prefixString, "")  # Remove the prefix in full OID string
                data = mibSymbol[2]
                snmp_name = ""
                snmp_decimal_index = ""
                for element in data:
                    if str(type(element)) == "<class 'SnmpAdminString'>":
                        snmp_name += element.prettyPrint() + "."
                    else:
                        snmp_decimal_index += str(element._value) + "."
                snmp_name = snmp_name[:-1]
                snmp_decimal_index = snmp_decimal_index[:-1]
                # Remove the suffix
                snmp_index = rreplace(oidString, snmp_decimal_index, "", 1)[:-1]
                resultIndex[snmp_name] = snmp_index
                if snmp_name in resultDecimalIndex:
                    resultDecimalIndex[snmp_name].add(snmp_decimal_index)
                else:
                    resultDecimalIndex[snmp_name] = set([snmp_decimal_index])
    for key in resultIndex:
        listResult.append({'name': key, 'snmp_index': resultIndex[key], 'snmp_decimal_index': list(sorted(resultDecimalIndex[key]))})
    return listResult


def rsvp_lsp_discovery(host, udp_port, community, mib_source='', remove_option=[], mib_file='JUNIPER-RSVP-MIB', mib_object='jnxRsvpSessionRole'):
    listResult = list()
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData(community, mpModel=1),
                                                                        UdpTransportTarget((host, udp_port)),
                                                                        ContextData(),
                                                                        ObjectType(ObjectIdentity(mib_file,
                                                                                                  mib_object).addMibSource(
                                                                            mib_source)),
                                                                        lexicographicMode=False):
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            resultDict = dict()
            for name, val in varBinds:
                # Check the value is equal to 1
                if val._value == 1:
                    mibSymbol = name.getMibSymbol()
                    oidString = str(name)  # Full OID string (can be used with snmpget)
                    preFixList = name.getMibNode().getName()  # The prefix
                    prefixString = ""
                    for prefix in preFixList:
                        prefixString += str(prefix) + "."
                    oidString = oidString.replace(prefixString, "", 1)  # Remove the prefix in full OID string
                    data = mibSymbol[2]
                    if len(data) == 2:
                        snmp_name = data[0].prettyPrint()
                        found = False
                        for regex in remove_option:
                            if re.match(regex, snmp_name):
                                found = True
                                break
                            else:
                                pass
                        if not found:
                            resultDict['name'] = snmp_name
                            resultDict['snmp_decimal_index'] = data[1].prettyPrint()
                            resultDict['snmp_index'] = rreplace(oidString, resultDict['snmp_decimal_index'], "", 1)[:-1]
                            listResult.append(resultDict)
                    else:
                        raise Exception("The format data is not OK, the process stop")
    return listResult


def ospf_discovery(host, udp_port, community, mib_source='', mib_file='OSPF-MIB', mib_object='ospfNbrIpAddr'):
    resultDict = dict()
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData(community, mpModel=1),
                                                                        UdpTransportTarget((host, udp_port)),
                                                                        ContextData(),
                                                                        ObjectType(ObjectIdentity(mib_file,
                                                                                                  mib_object).addMibSource(
                                                                            mib_source)),
                                                                        lexicographicMode=False):
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for name, val in varBinds:
                mibSymbol = name.getMibSymbol()
                oidString = str(name)  # Full OID string (can be used with snmpget)
                preFixList = name.getMibNode().getName()  # The prefix
                prefixString = ""
                for prefix in preFixList:
                    prefixString += str(prefix) + "."
                oidString = oidString.replace(prefixString, "", 1)  # Remove the prefix in full OID string
                data = mibSymbol[2]
                if len(data) == 2:
                    resultDict[data[0].prettyPrint()] = oidString
                else:
                    raise Exception("The format data is not OK, the process stop")
    listResult = list()
    for key, value in resultDict.items():
        listResult.append({'name': key, 'snmp_index': value})
    return listResult


def lsp_discovery(host, udp_port, community, mib_source='', mib_file='MPLS-MIB', mib_object='mplsLspInfoName'):
    result = list()
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData(community, mpModel=1),
                                                                        UdpTransportTarget((host, udp_port)),
                                                                        ContextData(),
                                                                        ObjectType(ObjectIdentity(mib_file,
                                                                                                  mib_object).addMibSource(
                                                                            mib_source)),
                                                                        lexicographicMode=False):
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for name, val in varBinds:
                snmp_index = str(name)  # Full OID string
                preFixList = name.getMibNode().getName()  # The prefix
                prefixString = ""
                for prefix in preFixList:
                    prefixString += str(prefix) + "."
                snmp_index = snmp_index.replace(prefixString, "", 1)  # Remove the prefix in full OID string
                result.append({'name': str(val.prettyPrint()), 'snmp_index': snmp_index})
    return result


def model_discovery(host, udp_port, community, mib_source='', mib_file='SNMPv2-MIB', mib_object='sysObjectID'):
    result = list()
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                        CommunityData(community, mpModel=1),
                                                                        UdpTransportTarget((host, udp_port)),
                                                                        ContextData(),
                                                                        ObjectType(ObjectIdentity(mib_file,
                                                                                                  mib_object).addMibSource(
                                                                            mib_source)),
                                                                        lexicographicMode=False):
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for name, val in varBinds:
                result.append({'name': model_mapping[str(val)], 'snmp_index': str(name)})
    return result

def interface_discovery(host, community, oid_prefix, udp_port=161):
    result = list()
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((host, udp_port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid_prefix)),
        lexicographicMode=False
    )
    for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for name, val in varBinds:
                snmp_index = str(name)  # Full OID string
                snmp_index = snmp_index.replace(oid_prefix, "", 1)
                if snmp_index[0] == '.':
                    snmp_index = snmp_index[1:]
                result.append({'name': str(val.prettyPrint()), 'snmp_index': snmp_index})
    
    # Start - Pham - 05/04/2021 - Function to discover alive interface 
    # Start - Tam - 19/10/2021 - Fix bug "can not remove elements of list when looping this list"
    alive_intf = SNMPLibrary.getAliveInterface(host, community)
    final_result = []
    for dict_ in result:
        if dict_['name'] in alive_intf:
            final_result.append(dict_)
    # End - Pham - 05/04/2021
    # End - Tam - 19/10/2021
    return final_result

# Start - Pham - 06/04/2021 - Add data type to default_discovery to remove the 
# standalone ItemNameGenerator task
def default_discovery(host, community, oid_prefix, udp_port=161):
    result = list()
    iterator = nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((host, udp_port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid_prefix)),
        lexicographicMode=False
    )
    for (errorIndication, errorStatus, errorIndex, varBinds) in iterator:
        if errorIndication:
            logging.error(errorIndication)
            break
        elif errorStatus:
            logging.error('%s at %s' % (errorStatus.prettyPrint(),
                                        errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for name, val in varBinds:
                snmp_index = str(name)  # Full OID string
                snmp_index = snmp_index.replace(oid_prefix, "", 1)
                if snmp_index[0] == '.':
                    snmp_index = snmp_index[1:]
                result.append({'name': str(val.prettyPrint()), 'snmp_index': snmp_index})
        
    return result
# End - Pham - 06/04/2021


# Start - Pham - 19/04/2021 - Refactor generate_discovery_config to remove 
# hardcoded keys to filter
def generate_discovery_config(function_definition, value_filter):
    """
    This function shall filter the result from "function_definition" command with 
    the user input filter and excluded these filtered value. This function
    also accept the filter from an external file (For example: the physical 
                                                  interface from the netconfig)
    :param function_definition: (python dictionary) contains the information to
    connect to the device and get data by using snmpwalk, netconf, or telnet. The
    format of the dictionary is {function_name: function_1, 
                                 function_argument: {arg1: val1, 
                                                     arg2: val2, 
                                                     argn: valn}
                                 }
    The function_name key is the discovery function that you wish to use to discover 
    a particular component (lsp, fpc) and the function_argument dictionary contains
    the corresponding input arguments of the function_name such as username, password,
    and netconf port number (if the function utilizes NetConf) or community, oid_prefix
    (if the function utilizes SNMP)
    :param value_filter: (python dictionary) contains the information to filter 
    the result from functions that utilize SNMP to retrieve the data, such as
    'userFilterIndex', 'userFilterValue', 'excludedIndex', 'excludedValue', 'priority'
        - userFilterIndex: the index filter from user (type:list of dicts)
        - userFilterValue: the value filter from user (type:list of dicts)
        - excludedIndex: the excluded index (type:list of dicts)
        - excludedValue: the excluded value (type:list of dicts)
        - priority: priority (inclusive or exclusive)
    :return: a list of dictionary with its dictionary keys defined in the corresponding function
    """
    # Use SNMP walk to get data - Start
    discovery_func_init = list()
    # Start - Pham - 12/04/2021 - Combine all arguments into kwarg
    # Remove all if-else
    if "function_name" not in function_definition.keys():
        logging.error("The function_name is not sepcified as a key")
        raise Exception("The function_name is not sepcified as a key")
    if function_definition["function_name"] is None:
        logging.error("The function name is empty")
        raise Exception("The function name is empty")  
    func_name = function_definition["function_name"]
    if "function_argument" not in function_definition.keys():
        logging.error("The function_argument is not sepcified as a key")
        raise Exception("The function_arguments is not sepcified as a key")
    func_arg = function_definition["function_argument"]
    discovery_func_init = globals()[func_name](**func_arg)
    # End - Pham - 12/04/2021
    # Use SNMP walk to get data - End   
    # Filter by user input - Start
    reducedList = list()
    if 'priority' not in value_filter:
        value_filter['priority'] = 'inclusive'  
    
    if value_filter['priority'].lower() == 'inclusive':
        reducedList = inclusive_value_filter_config(value_filter, discovery_func_init, reducedList)
    elif value_filter['priority'].lower() == 'exclusive':
        reducedList = exclusive_value_filter_config(value_filter, discovery_func_init, reducedList)
    else:
        logging.warning("The priority is not 'inclusive' or 'exclusive'")
        raise Exception("The priority is not 'inclusive' or 'exclusive'")

    return reducedList


if __name__ == '__main__':
    from pprint import pprint
    # pprint(qos_discovery('10.96.10.13', 161, 'public',
    #                      '/home/kien/backup/DuAn/SVTECH-Junos-Automation/Ansible-Demo/library/mibs'))
    # pprint(rpm_discovery('10.96.10.13', 161, 'public',
    #                      '/home/kien/backup/DuAn/SVTECH-Junos-Automation/Ansible-Demo/library/mibs'))
    # Test IfDescr - Start
    # snmp_walk = {
    #     'function_name': 'default_discovery',
    #     'host': '10.96.10.13',
    #     'udp_port': 161,
    #     'community': 'public',
    #     'oid_prefix': '1.3.6.1.2.1.2.2.1.2'
    # }
    # file_filter = {
    #     'file': '/tmp/test.tmp',
    #     'filter': 'name'
    # }
    # value_filter = {
    #     'priority': 'inclusive',
    #     'userFilterValue': ['xe', 'ge', 'et', 'ae'],
    #     'excludedValue': ['.']
    # }
    # Test IfDescr - End
    # Test FPC - Start
    # snmp_walk = {
    #     'function_name': 'default_discovery',
    #     'host': '10.96.10.13',
    #     'udp_port': 161,
    #     'community': 'public',
    #     'oid_prefix': '1.3.6.1.4.1.2636.3.1.13.1.5'
    # }
    # file_filter = None
    # value_filter = {}
    # Test IfDescr - End
    # Test model - Start
    # snmp_walk = {
    #     'function_name': 'model_discovery',
    #     'host': '10.96.10.13',
    #     'udp_port': 161,
    #     'community': 'public',
    #     'mib_source': '/home/kien/backup/DuAn/SVTECH-Junos-Automation/module_utils/mibs',
    #     'mib_file': 'SNMPv2-MIB',
    #     'mib_object': 'sysObjectID'
    # }
    # file_filter = None
    # value_filter = {}
    # Test model - End
    # Test lsp_discovery - Start
    # snmp_walk = {
    #     'function_name': 'lsp_discovery',
    #     'host': '10.96.10.13',
    #     'udp_port': 161,
    #     'community': 'public',
    #     'mib_source': '/home/kien/backup/DuAn/SVTECH-Junos-Automation/module_utils/mibs',
    #     'mib_file': 'MPLS-MIB',
    #     'mib_object': 'mplsLspInfoName'
    # }
    # file_filter = None
    # value_filter = {}
    # Test lsp_discovery - End
    # Test ospf_discovery - Start
    # snmp_walk = {
    #     'function_name': 'ospf_discovery',
    #     'host': '10.96.10.13',
    #     'udp_port': 161,
    #     'community': 'public',
    #     'mib_source': '/home/kien/backup/DuAn/SVTECH-Junos-Automation/module_utils/mibs',
    #     'mib_file': 'OSPF-MIB',
    #     'mib_object': 'ospfNbrIpAddr'
    # }
    # file_filter = None
    # value_filter = {}
    # Test ospf_discovery - End
    # Test rsvp_lsp_discovery - Start
    # snmp_walk = {
    #     'function_name': 'rsvp_lsp_discovery',
    #     'host': '100.100.100.11',
    #     'udp_port': 161,
    #     'community': 'METRO',
    #     'mib_source': 'Developper/SVTECH-Junos-Automation/module_utils/mibs',
    #     'mib_file': 'JUNIPER-RSVP-MIB',
    #     'mib_object': 'jnxRsvpSessionRole'
    # }
    # file_filter = None
    # value_filter = {}
    # Test rsvp_lsp_discovery - End
    # Test rpm_discovery - Start
    # snmp_walk = {
    #     'function_name': 'rpm_discovery',
    #     'host': '100.100.100.1',
    #     'udp_port': 161,
    #     'community': 'METRO',
    #     'mib_source': 'Developper/SVTECH-Junos-Automation/module_utils/mibs',
    #     'mib_file': 'JUNIPER-RPM-MIB',
    #     'mib_object': 'jnxRpmResCalcAverage'
    # }
    # file_filter = None
    # value_filter = {}
    # Test rpm_discovery - End
    # Test qos_discovery - Start
    #snmp_walk = {
    #    'function_name': 'qos_discovery',
    #    'host': '10.96.10.13',
    #    'udp_port': 161,
    #    'community': 'public',
    #    'mib_source': '/home/kien/backup/DuAn/SVTECH-Junos-Automation/module_utils/mibs',
    #    'mib_file': 'JUNIPER-COS-MIB',
    #    'mib_object': 'jnxCosIfqQedPkts'
    #}
    #file_filter = None
    #value_filter = {}
    # pprint(SNMPGenerateConfig(snmp_walk, file_filter, value_filter))
