import ftplib
import logging
import os
import re
import telnetlib
import time
import ipaddress
from threading import Thread
from .BASE_FUNC import PRINT_W_TIME

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3




def VERIFY_IPV4_ADDRESS ( ip_address ) :
    """VERIFY IPV4 ADDRESS"""
    match = re.match ( '^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$' , ip_address )  # simple regex to check range 0-3 + 4 quarter

    if not match :
        logging.error ( "Provided IP [ {} ] out of digit range".format(ip_address) )
        return CRITICAL

    quarter = [ ]
    for number in match.groups ( ) :
        quarter.append ( int ( number ) )  # 4 element list for simple further check

    if quarter [ 0 ] < 1 :  # 0.x.x.x is incorrect
        logging.error ( "Provided IP [ {} ] include 0 in first octet".format(ip_address) )
        return CRITICAL
    for number in quarter :
        if number > 255 or number < 0 :  # 255 max
            logging.error ( "Provided IP [ {} ] include number of out range 255".format(ip_address) )
            return CRITICAL
    return OK

def VERIFY_IPV4_ADDRESS_LIST ( ip_address_list ) :
    """VERIFY A LIST OF IPV4 ADDRESS, ONLY RETURN CORRECT ONES"""
    if isinstance ( ip_address_list , list ) is False :
        logging.error ( "Provided variable is not a list, exiting" )
        return CRITICAL
    else :
        verified_ip_list = list ( )
        for ip_address in ip_address_list :
            if VERIFY_IPV4_ADDRESS ( ip_address ) == OK :
                verified_ip_list.append ( ip_address )
            else :
                logging.error ( "Skipping wrong address " + ip_address )

    if len(verified_ip_list) > 0:
        return verified_ip_list
    else:
        logging.error("All provided IP is wrong")
        return CRITICAL

def TEST_HOST_PING ( ip_address ,
                     interval = 0.2,
                     count = 3) :
    """VERIFY HOST REACHABILITY ADDRESS"""
    try :
        logging.debug ( "Pinging host " + ip_address )
        if VERIFY_IPV4_ADDRESS(ip_address) != OK:
            logging.warning("Provided hostname is not an address, can significantly increase pingtest time")
        # [Kien] - 21/12/2018 - Version 1.1 - Modify the argument from "W" to "w"
        response = os.system ( "ping -c" + str ( count ) + "-w" + str ( interval ) + " " + ip_address + " > /dev/null 2>&1" )
    except Exception as local_except :
        logging.error ( "Exception when pinging host caused by " + str ( local_except ) )
        return CRITICAL

    if response == 0 :
        logging.info ('{} is UP!'.format(ip_address) )
        return OK
    else :
        logging.info ('{} is DOWN!'.format(ip_address) )
        return CRITICAL



def TEST_HOST_PING_MULTIPROCESS(queue_index, 
                                ping_queue, 
                                aliveHost,
                                interval = 0.2,
                                count = 3):
    """Pings subnet"""
    while True:
        ip_address = ping_queue.get()
        if ip_address is None:
            ping_queue.put(None)
            break
        logging.debug("Getting address {} into queue job index: {} ".format(ip_address,queue_index))
        return_code = TEST_HOST_PING(ip_address)
        if return_code == 0:
            aliveHost.append(ip_address)
        else:
            #logging  is possible but let the logging be handled by the original ping function
            pass
        ping_queue.task_done()
   


def GET_ALIVE_HOST(networkAdress,
                  interval = 0.2,
                  count = 3):
    import sys
    is_py2 = sys.version[0] == '2'
    if is_py2:
        from Queue import Queue
    else:
        from queue import Queue
    num_threads = 6
    ping_queue = Queue()
    # [Kien] - 21/12/2018 - Version 1.1 - Update /32 case
    all_hosts = list()
    try:
        logging.info ("Resolving provided subnet {} into list of host".format(networkAdress))
        # [Kien] - 21/12/2018 - Version 1.1 - Update /32 case - Start
        if "/32" in networkAdress:
            all_hosts.append(networkAdress.replace("/32", ""))
        # [Kien] - 21/12/2018 - Version 1.1 - Update /32 case - End
        else:
            # [Kien] - 21/12/2018 - Version 1.1 - Use argument "False" for the broadcast case.
            if is_py2:
                ip_net = ipaddress.ip_network(unicode(networkAdress), False)
            else:
                ip_net = ipaddress.ip_network(str(networkAdress), False)
            all_hosts = list(ip_net.hosts())
        logging.debug("List of host to be tested:{}".format(all_hosts))
    except Exception as local_e:
        logging.error("Failed to result the provided subnet {} into host ip address".format(networkAdress))
        return CRITICAL


    aliveHost = list()

    for queue_index in range(num_threads):
        worker = Thread(target=TEST_HOST_PING_MULTIPROCESS,
                       args=(  queue_index,
                               ping_queue,
                               aliveHost,
                               interval,
                               count))
        worker.setDaemon(True)
        worker.start()
    # For each IP address in the subnet,
    # run the ping command with subprocess.popen interface
    for ip in all_hosts:
        logging.debug ("Putting host {} in queue".format(ip,ping_queue.unfinished_tasks))
        ping_queue.put(str(ip))

    ping_queue.join()
    ping_queue.put(None)
    return aliveHost


class FTP_UPLOAD_TRACKER :
    size_written = 0
    totalSize = 0
    lastShownPercent = 0

    def __init__ ( self , totalSize ) :
        self.totalSize = totalSize

    def handle ( self , block ) :
        self.size_written += 1024
        percent_complete = round ( (float ( self.size_written ) / float ( self.totalSize )) * 100 )

        if self.lastShownPercent != percent_complete :
            self.lastShownPercent = percent_complete
            logging.info ( str ( percent_complete ) + " percent complete" )


def FTP_UPLOAD ( ip_address = '',
                 username = '' ,
                 password = '' ,
                 local_filename = '' ,
                 remote_filename = '' ) :
    """VERIFY HOST REACHABILITY ADDRESS"""

    try :
        ftp_token = ftplib.FTP ( ip_address )
        ftp_token.connect ( )
        ftp_token.login ( username , password )
        logging.info ( 'Opened FTP connection to ' + ip_address + ', uploading file, taking while....' )

    except Exception as local_except :
        PRINT_W_TIME ( 'Failed to connect via FTP to host ' + ip_address + ' due to ' + str ( local_except ) )
        logging.error ( 'Failed to connect via FTP to host ' + ip_address + ' due to ' + str ( local_except ) )
        return CRITICAL

    try :
        logging.info ( ' Uploading file (' + local_filename + ') as (' + remote_filename + ') onto + (' + ip_address + ')' )
        upload_tracker = FTP_UPLOAD_TRACKER ( int ( os.path.getsize ( local_filename ) ) )
        upload_result = ftp_token.storbinary ( 'STOR ' + remote_filename , open ( local_filename , 'rb' ) , 1024 , upload_tracker.handle )
        ftp_token.close ( )
        logging.info ( 'Uploaded ' + local_filename + ' to :' + remote_filename + ' at ' + ip_address )
        return OK
    except Exception as local_except :
        PRINT_W_TIME ( 'Failed to upload via FTP to host ' + ip_address + ' due to ' + str ( local_except ) )
        logging.error ( 'Failed to upload via FTP to host ' + ip_address + ' due to ' + str ( local_except ) )
        return CRITICAL


def FTP_RM_TREE ( ftp , path ) :
    """Recursively delete a directory tree on a remote server."""
    current_dir = ftp.pwd ( )

    try :
        file_list = ftp.nlst ( path )
    except ftplib.all_errors as e :
        # some FTP servers complain when you try and list non-existent paths or empty directory
        logging.error ( 'Could not list ' + str ( path ) + ' due to ' + str ( e ) )
        if 'No files found' in str ( e ) :
            logging.error ( 'Directory ' + str ( path ) + ' is empty' )
            file_list = [ ]
        else :
            return CRITICAL

    for file_name in file_list :
        if os.path.split ( file_name ) [ 1 ] in ('.' , '..') :
            continue
        logging.info ( ' Checking ' + str ( file_name ) + ' for removal' )

        try :
            ftp.cwd ( file_name )  # if we can cwd to it, it's a folder
            ftp.cwd ( current_dir )  # don't try to nuke a folder we're in
            FTP_RM_TREE ( ftp , file_name )
        except ftplib.all_errors :
            ftp.delete ( file_name )

    try :
        ftp.rmd ( path )
        logging.info ( ' Removing folder ' + str ( path ) )
    except ftplib.all_errors as e :
        logging.error ( 'Could not remove ' + str ( path ) + ' due to ' + str ( e ) )
    
    return OK



def IP_LIST_TEXT_PARSING ( filename = 'MissingInput' ) :
    logging.info (
            '\n\n\-------------------------------opening host list file ' + str ( filename ) + '------------------------------------' )
    try :
        with open ( filename , 'r' ) as f :
            line = f.readlines ( )
        f.close ( )

    except Exception as local_e :
        raise StandardError ( "ERROR OCCUR READING HOST LIST FILE" + filename + "- CHECK THE LOG" )
        logging.error ( "Exception when opening file cause by:     " + str ( local_e ) )
        sys.exit ( CRITICAL )

    logging.info (
            '\n\n\------------------------------------finished reading input file, checking md5------------------------------------' )

    try :
        ip_list = list ( )
        for content in line :
            input_address = content.strip ( '\n' )
            ip_verification = VERIFY_IPV4_ADDRESS ( input_address )

            if ip_verification != OK :
                logging.error ( 'Host IP ' + input_address + ' in wrong format, skipping' )
            else :
                logging.info ( 'Host IP ' + input_address + ' OK, appending ' )
                ip_list.append ( input_address )

        PRINT_W_TIME ( "FINISHED PARSING FILE (CHECK LOG FOR DETAIL) - START UPLOAD? (Y to continue) " )

    # For interactive debugging only
    # user_input =  raw_input(" " + "    " +  "FINISHED PARSING FILE (CHECK LOG FOR DETAIL) - START UPLOAD? (Y to continue) " )
    # if user_input != 'Y' and user_input != 'y' and user_input != 'YES' and user_input != 'yes':
    #    print "DID NOT SEE (Y), EXITING"
    #    sys.exit (0)
    # else:
    #    print "PROCEEDING"

    except Exception as local_e :
        logging.error ( "Exception when creating IP list from " + filename + " cause by:     " + str ( local_e ) )
        raise StandardError ( "ERROR OCCUR WHEN READING IP LIST ON FILE FROM" + filename + " - CHECK THE LOG" )
        sys.exit ( CRITICAL )

    # pprint ( ip_list )
    return ip_list



def VERIFY_OUTPUT_MD5_JUNIPER ( original_buffer = 'MissingInput' ,
                                username = 'MissingInput' ,
                                filename = 'MissingInput' ,
                                md5 = 'MissingInput' ,
                                prompt = '>' ) :
    try :
        full_prompt = username + '\@.*' + prompt
        logging.debug ( 'full prompt is ' + '"' + full_prompt + '"' )
        full_command = full_prompt + '[.\s]*\\n'
        logging.debug ( 'full command is ' + '"' + full_command + '"' )

        stripped_buffer = re.sub ( r'{master}' , '' , original_buffer )
        stripped_buffer = re.sub ( full_command , '' , stripped_buffer )
        stripped_buffer = re.sub ( full_prompt , '' , stripped_buffer )
        stripped_buffer = re.sub ( r'file checksum.*' , '' , stripped_buffer )
        stripped_buffer = re.sub ( r'\n' , '' , stripped_buffer )

        logging.debug ( 'stripped buffer is ' + stripped_buffer )

    except Exception as local_except :
        PRINT_W_TIME ( 'Error when parsing telnet output due to ' + str ( local_except ) )
        logging.error ( 'Error when parsing telnet output due to ' + str ( local_except ) )
        return CRITICAL

    try :
        md5_output_sequence = 'MD5 (' + filename + ')'
        logging.debug ( 'path to file should be:  ' + md5_output_sequence )

        if 'error' in stripped_buffer and 'No such file' in stripped_buffer :
            logging.info ( 'File is not present on device - upload should start soon' )
            return WARNING
        elif 'error' in stripped_buffer :
            PRINT_W_TIME ( 'Unknown error message when checking md5 on device, will not try to re-upload' )
            logging.info ( 'Unknown error message when checking md5 on device, will not try to re-upload' )
            return CRITICAL
        elif md5_output_sequence in stripped_buffer :
            stripped_buffer = re.sub ( r'.*= ' , '' , stripped_buffer )
            stripped_buffer = re.sub ( r'\s' , '' , stripped_buffer )

            logging.info ( 'MD5 of file on device is "' + stripped_buffer + '\"' )
            logging.info ( 'MD5 of input for file is "' + md5 + '\"' )

            if stripped_buffer == md5 :
                logging.info ( 'MD5 found on device match user-input md5, skipping this host ' )
                return OK
            else :
                logging.error ( 'file is found on device but MD5 do NOT match, re-upload should start soon"' )
                return WARNING
        else :
            PRINT_W_TIME ( 'Got undefined response when checking md5 "' + str ( stripped_buffer ) + '"- will not try to re-upload' )
            logging.error ( 'Got undefined response when checking md5 "' + str ( stripped_buffer ) + '"- will not try to re-upload' )
            return CRITICAL
    except Exception as local_except :
        PRINT_W_TIME ( 'Error when comparing md5 output from device due to ' + str ( local_except ) )
        logging.error ( 'Error when comparing md5 output from device due to ' + str ( local_except ) )
        return CRITICAL


def FILE_AVAI_CHECK_ON_JUNIPER ( ip_address = 'MissingInput' ,
                                 username = 'MissingInput' ,
                                 password = 'MissingInput' ,
                                 destination_file = 'MissingInput' ,
                                 md5 = 'MissingInput' ) :
    """VERIFY FILE AVAILABILITY """

    juniper_prompt = '>'
    try :
        telnet_token = telnetlib.Telnet ( ip_address )
        telnet_token.expect ( [ r".*login.* " ] )
        telnet_token.write ( username + '\r\n' )
        telnet_token.expect ( [ r".*assword.*" ] )
        telnet_token.write ( password + '\r\n' )

    except Exception as local_except :
        PRINT_W_TIME ( 'Failed to telnet to  host ' + ip_address + ' due to ' + str ( local_except ) )
        logging.error ( 'Failed to telnet to  host ' + ip_address + ' due to ' + str ( local_except ) )
        return CRITICAL

    try :
        response_object = telnet_token.expect ( [ r".*\>" , r".*incorrect.*" ] , timeout = 5 )
        response_messages = response_object [ 2 ]
    # FUCKING stupid lib return 3 value with message in slot 2 of list
    except Exception as local_except :
        PRINT_W_TIME ( 'Unknown error after sending login info to ' + ip_address + ' due to ' + str ( local_except ) )
        logging.error ( 'Unknown error after sending login info to ' + ip_address + ' due to ' + str ( local_except ) )
        return CRITICAL

    try :
        if 'incorrect' in response_messages :
            PRINT_W_TIME ( 'Wrong telnet login info for ' + ip_address + ' skipping this host' )
            logging.info ( 'Wrong telnet login info for ' + ip_address + ' skipping this host' )
            return CRITICAL

        elif '>' in response_messages :
            logging.info ( 'Logged in, checking file availability for ' + ip_address )
            logging.debug ( 'Send remote checksum command: "' + 'file checksum md5 ' + destination_file + '"' )

            telnet_token.write ( 'file checksum md5 ' + destination_file + '\r\n' )
            time.sleep ( 10 )
            read_buffer = telnet_token.read_very_eager ( )
            time.sleep ( 1 )

            logging.debug ( 'collected buffer is\n' + read_buffer )
            logging.debug ( 'running md5 analysis' )
            md5_check = VERIFY_OUTPUT_MD5_JUNIPER ( read_buffer ,
                                                    username ,
                                                    destination_file ,
                                                    md5 ,
                                                    juniper_prompt )

            telnet_token.write ( 'exit\r\n' )
            # buffer = telnet_token.read_very_eager ( )

            # logging.debug('exit buffer is\n' + buffer)
            # buffer = telnet_token.read_all ( )

            if md5_check == CRITICAL :
                logging.debug ( 'Got an exception when analyzing md5 check output from device - skipping' )
                return CRITICAL
            elif md5_check == WARNING :
                logging.info ( 'MD5 for file is not found on host or mismatched, will try to re-upload' )
                return WARNING
            elif md5_check == OK :
                logging.info ( 'MD5 for file is found and matched expected MD5, upload will be skipped' )
                return OK

        else :
            PRINT_W_TIME (
                ' Logged in ' + ip_address + ' but got abnormal login messages: ' + str ( response_messages ) + '\n Skipping this host' )
            logging.info (
                ' Logged in ' + ip_address + ' but got abnormal login messages: ' + str ( response_messages ) + '\n Skipping this host' )
            return CRITICAL

    except Exception as local_except :
        PRINT_W_TIME (
            'Failed execute md5 checksum for file' + destination_file + ' on host ' + ip_address + ' due to ' + str ( local_except ) )
        logging.error (
            'Failed execute md5 checksum for file' + destination_file + ' on host ' + ip_address + ' due to ' + str ( local_except ) )
        return CRITICAL


def UPLOAD_SINGLE_HOST_SINGLE_FILE_JU ( ip_address = 'MissingInput' ,
                                        username = 'MissingInput' ,
                                        password = 'MissingInput' ,
                                        local_filename = 'MissingInput' ,
                                        remote_filename = 'MissingInput' ,
                                        md5 = 'MissingInput' ) :
    """ Deprecated, DO NOT USE"""
    ip_reachability = TEST_HOST_PING ( ip_address , 0.1 , 3 )

    if ip_reachability != OK :
        PRINT_W_TIME ( ip_address + 'is unreachable, next!' )
        logging.error ( ip_address + 'is unreachable, next!' )
        return CRITICAL
    else :
        logging.info ( 'Node ' + ip_address + ' is up, starting telnet session to check for file\'s avaiability first' )

        file_check_result = FILE_AVAI_CHECK_ON_JUNIPER ( ip_address ,
                                                         username ,
                                                         password ,
                                                         remote_filename ,
                                                         md5 )
        if file_check_result == CRITICAL :  # if upload return  OK ,re-check the file
            PRINT_W_TIME (
                '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload FAILED , SEE LOG ABOVE FOR '
                                                                                                'DETAIL' )
            logging.error (
                '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload FAILED , SEE LOG ABOVE FOR '
                                                                                                'DETAIL' )
            return CRITICAL
        elif file_check_result == OK :
            PRINT_W_TIME ( '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload OK ' )
            logging.info ( '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload OK ' )
            return OK
        elif file_check_result == WARNING :
            logging.info ( '     Upload or Re-uploading.....' )

        indices = 0
        while file_check_result != OK and file_check_result != CRITICAL :  # if not CRITICAL or OK, try to reupload

            # reupload operation
            ftp_check_result = FTP_UPLOAD ( ip_address ,
                                            username ,
                                            password ,
                                            local_filename ,
                                            remote_filename )
            indices += 1

            if ftp_check_result == OK :  # if upload return  OK ,re-check the file
                logging.info ( 'Upload operation looked ok - Re-checking md5 after upload on host ' + ip_address )
                file_check_result = FILE_AVAI_CHECK_ON_JUNIPER ( ip_address ,
                                                                 username ,
                                                                 password ,
                                                                 remote_filename ,
                                                                 md5 )
            elif ftp_check_result == CRITICAL :  # if upload return CRITICAL ,break immediately
                logging.error ( 'FTP operation failed, this host ' + ip_address + ' will be skipped ' )
                return CRITICAL

            # re-check the file after upload
            if file_check_result == CRITICAL :
                PRINT_W_TIME (
                    '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload FAILED , SEE LOG ABOVE FOR '
                                                                                                    'DETAIL' )
                logging.error (
                    '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload FAILED , SEE LOG ABOVE FOR '
                                                                                                    'DETAIL' )
                return CRITICAL
            elif file_check_result == OK :
                PRINT_W_TIME ( '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload OK ' )
                logging.info ( '    UPLOAD_REPORT for file (' + local_filename + ') :   HOST (' + ip_address + ') upload OK ' )
                return OK
            elif file_check_result == WARNING :
                logging.info ( '     Upload or Re-uploading.....' )

            # cancel after 3 fail attemPT
            if indices > 2 :
                logging.error (
                        '    UPLOAD_REPORT for file (' + local_filename + ') :    FILE RE-UPLOADED TO ' + ip_address + ' 3 TIMES BUT MD5 '
                                                                                                                       'IS STILL WRONG - '
                                                                                                                       'CHECK MD5 AGAIN?' )
                PRINT_W_TIME (
                        '    UPLOAD_REPORT for file (' + local_filename + ') :    FILE RE-UPLOADED TO ' + ip_address + ' 3 TIMES BUT MD5 '
                                                                                                                       'IS STILL WRONG - '
                                                                                                                       'CHECK MD5 AGAIN?' )
                return CRITICAL


#import smtplib
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEBase import MIMEBase
#from email.MIMEText import MIMEText
#from email.Utils import COMMASPACE , formatdate
#from email import Encoders
#
#
#def sendMail ( to , fro , subject , text , files = [ ] , server = "localhost" ) :
#    assert type ( to ) == list
#    assert type ( files ) == list
#
#    msg = MIMEMultipart ( )
#    msg [ 'From' ] = fro
#    msg [ 'To' ] = COMMASPACE.join ( to )
#    msg [ 'Date' ] = formatdate ( localtime = True )
#    msg [ 'Subject' ] = subject
#    logging.info ( '\tSending email from' + fro )
#    logging.info ( '\tSending email to' + str ( to ) )
#
#    msg.attach ( MIMEText ( text ) )
#
#    for file in files :
#        logging.info ( '\tAttaching file ' + file )
#        part = MIMEBase ( 'application' , "octet-stream" )
#        part.set_payload ( open ( file , "rb" ).read ( ) )
#        Encoders.encode_base64 ( part )
#        part.add_header ( 'Content-Disposition' , 'attachment; filename="%s"'
#                          % os.path.basename ( file ) )
#        msg.attach ( part )
#
#    smtp = smtplib.SMTP ( server )
#    smtp.sendmail ( fro , to , msg.as_string ( ) )
#    smtp.close ( )
