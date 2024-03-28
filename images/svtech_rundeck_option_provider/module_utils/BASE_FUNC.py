#!/usr/bin/python


import fnmatch
import hashlib
import locale
import logging
import os
import re
import sys
import time

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def INIT_LOGGING_ARGS(parser):
    # ===================================================Logging Parameter======================================================
    log_group = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
         "Log Options", 
         "Customize the log options"
    )
    log_group.add_argument('--log_size',
                        dest = "log_size",
                        type=int,
                        default=2 * 1024 * 1024,
                        help='        Size for log file ')

    log_group.add_argument('--log_count',
                        dest = "log_count",
                        type=int,
                        default=2,
                        help='        Number of log file ')

    log_group.add_argument('--log_prefix',
                        dest = "log_prefix",
                        type=str,
                        default="",
                        help='        Prefix for log file ')

    log_group.add_argument('--log_surfix',
                        dest = "log_surfix",
                        type=str,
                        default="",
                        help='        Surfix for log file ')

    log_group.add_argument('--log_timestamp', 
                        dest = "log_timestamp",
                        type=str,
                        default="%Y-%m-%d",
                        help='         timestamp in strftime format for log file')

    log_group.add_argument('--log_level',
                        dest = "log_level",
                        choices = [ 'DEBUG' , 'INFO' , 'WARNING' , 'ERROR' , 'CRITICAL' ] ,
                        default="WARNING",
                        help='        log level')

    if "win" in sys.platform.lower() and 'gooey' in sys.modules:
        log_group.add_argument('--log_dir',
                            dest = "log_dir",
                            type=str,
                            default=".",
                            widget = "DirChooser", #require Gooey on Windows platform
                            help='        dir to store log file ')
    else:
        log_group.add_argument('--log_dir',
                            dest = "log_dir",
                            type=str,
                            default=".",
                            help='        dir to store log file ')


def INIT_OUTPUT_FILE_ARGS(parser):
# ===================================================OUTPUT PARAMETER=======================================================
    output_group = parser.add_argument_group( #actually not neccessary, for Gooey GUI only
         "Output Options", 
         "Customize the output file name  options"
    )
    output_group.add_argument('-op', 
                        '--output_prefix', 
                        dest = "output_prefix" ,
                        type=str,
                        default="",
                        help='        prefix for output file to store results')

    output_group.add_argument( '-ot', 
                         '--output_timestamp', 
                         dest = "output_timestamp",
                         type=str,
                         default="%Y-%m-%d-%Hh",
                         help='         timestamp in strftime format for output file')

    output_group.add_argument('-os', 
                        '--output_surfix', 
                        dest = "output_surfix",
                        type=str,
                        default="",
                        help='    surfix (file extension) for output file to store results')

    if "win" in sys.platform.lower() and 'gooey' in sys.modules:
        output_group.add_argument('-od', 
                            '--output_dir', 
                            dest = "output_dir",
                            type=str, 
                            default=".",
                            widget = "DirChooser", #require Gooey on Windows platform
                            help='        output dir to store results')
    else:
        output_group.add_argument('-od', 
                            '--output_dir', 
                            dest = "output_dir",
                            type=str, 
                            default=".",
                            help='        output dir to store results')

def PARSE_BOOLEAN_ARGS(argument):
    # type: (argument) -> string
    """Check provided argument and return boolean type"""

    if argument.lower() in ('yes', 'y','true', 't', '1'):
        return True
    elif argument.lower() in ('no', 'n', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Invalid input for boolean option provided')

    parser.add_argument('-op', 
                        '--output_prefix', 
                        dest = "output_prefix" ,
                        type=str,
                        default="",
                        help='        prefix for output file to store results')

    parser.add_argument( '-ot', 
                         '--output_timestamp', 
                         dest = "output_timestamp",
                         type=str,
                         default="%Y-%m-%d-%Hh%Mm%S",
                         help='         timestamp in strftime format for output file')

    parser.add_argument('-os', 
                        '--output_surfix', 
                        dest = "output_surfix",
                        type=str,
                        default="xml",
                        help='    surfix (file extension) for output file to store results')

    parser.add_argument('-od', 
                        '--output_dir', 
                        dest = "output_dir",
                        type=str, 
                        default=".",
                        help='        output dir to store results')


def CREATE_EXPORT_DIR ( directory = "./" ) :
    # type: (directory) -> string
    """CREATE DIR"""
    if not os.path.exists ( directory ) :
        os.makedirs ( directory )
        logging.debug ( 'Created new directory: ' + directory )
    else :
        logging.debug ( 'Directory already existed ' + directory )
    return directory


def REMOVE_EXPORT_DIR ( directory = "./" ) :
    # type: (directory) -> string
    """CREATE DIR"""
    if os.path.exists ( directory ) :
        try :
            os.removedirs ( directory )
        except Exception as e :
            logging.error ( ' Error removing directory due to ' + str ( e ) )
            logging.error ( ' Trying to remove all sub directory and files' )
            
            for root , dirs , files in os.walk ( directory , topdown = False ) :
                for name in files :
                    os.remove ( os.path.join ( root , name ) )
                for name in dirs :
                    os.rmdir ( os.path.join ( root , name ) )
            os.removedirs ( directory )

        logging.debug ( 'Removed directory: ' + directory )
    else :
        logging.debug ( 'Directory does not existed ' + directory )
    return directory


def WALKDIR ( root = '.' ,
              verbose = False ) :
    if not os.path.exists ( root ) :
        logging.error ( '!!    Provided root import path do not exist - exiting !!' )
        return None
    else :
        DIR = [ ]
        for root , dirs , files in os.walk ( root , topdown = True ) :
            for name in files :
                fullName = os.path.join ( root , name )
                (parentDir , relativeDir) = os.path.split ( root )
                
                if verbose == True :
                    full_dir = os.path.join ( parentDir , relativeDir )
                    logging.info ( "Reading files from " + full_dir )
                
                DIR.append ( { 'fileName' : name , 'relativeDir' : relativeDir , 'parentDir' : parentDir } )
        return DIR


def WALK_DIR_FILTERED ( root = '.' ,
                        dir_filter = "*" ,
                        file_filter = "*" ,
                        verbose = False ) :
    if not os.path.exists ( root ) :
        logging.error ( '!!    Provided root import path do not exist - exiting !!' )
        return None
    else :
        DIR = [ ]
        for root , dirs , files in os.walk ( root , topdown = True ) :
            for name in files :
                fullName = os.path.join ( root , name )
                (parentDir , relativeDir) = os.path.split ( root )
                
                if fnmatch.fnmatch ( root , dir_filter ) :
                    if fnmatch.fnmatch ( name , file_filter ) :
                        DIR.append ( { 'fileName' : name , 'relativeDir' : relativeDir , 'parentDir' : parentDir } )
                        
                        if verbose == True :
                            full_dir = os.path.join ( parentDir , relativeDir )
                            logging.info ( "Reading files from " + full_dir )
        return DIR


def PRINT_W_TIME ( message = "" ,
                   timestamp = time.strftime ( '%x' ) + "  " + time.strftime ( '%X' ) ) :
    #timestamp = "avoiding error, break-fix"
    for lines in message.splitlines ( ) :
        print ("{}\t{}".format(timestamp,message))


def TIME_INIT ( ) :
    # =====================Checking datetime & locale variable==================#
    current_time = dict ( )
    logging.debug ( 'initiating time parameter' )
    # Check and set locale
    if locale.getlocale ( ) == (None , None) :  #
        locale.setlocale ( locale.LC_ALL , '' )  #

    # Check datetime and save variable
    # Check datetime and save variable
    logging.info ( '==================================================================' )
    current_time [ 'Full_Date' ] = time.strftime ( '%x' )
    logging.debug ( 'Current date is ' + current_time [ 'Full_Date' ] )

    current_time [ 'Full_Time' ] = time.strftime ( '%X' )
    logging.debug ( 'Current time is ' + current_time [ 'Full_Time' ] )

    current_time [ 'Day' ] = time.strftime ( '%d' )
    logging.debug ( 'Current day is ' + current_time [ 'Day' ] )

    current_time [ 'Month' ] = time.strftime ( '%B' )
    logging.debug ( 'Current month is ' + current_time [ 'Month' ] )

    current_time [ 'MonthNum' ] = time.strftime ( '%m' )
    logging.debug ( 'Current month is ' + current_time [ 'MonthNum' ] )

    current_time [ 'Year' ] = time.strftime ( '%Y' )
    logging.debug ( 'Current year is ' + current_time [ 'Year' ] )

    current_time [ 'Hour' ] = time.strftime ( '%H' )
    logging.debug ( 'Current hour is ' + current_time [ 'Day' ] )

    current_time [ 'Min' ] = time.strftime ( '%M' )
    logging.debug ( 'Current minutes is ' + current_time [ 'Month' ] )

    current_time [ 'Sec' ] = time.strftime ( '%S' )
    logging.debug ( 'Current sec is ' + current_time [ 'Year' ] )

    return current_time


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result) # or format into one line however you want to

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '') + '|'
        return s


def LOGGER_INIT ( log_level = logging.INFO ,
                  log_file = 'unconfigured_log.log' ,
                  file_size = 2 * 1024 * 1024 ,
                  file_count = 2 ,
                  shell_output = False ,
                  log_file_mode = 'a' ,
                  log_format = '%(asctime)s %(levelname)s %(funcName)s(%(lineno)d)     %(message)s',
                  print_log_init = False) :
    try :
        main_logger = logging.getLogger ( )
        main_logger.setLevel ( log_level )
        # add a format handler
        log_formatter = OneLineExceptionFormatter ( log_format )

    except Exception as e :
        PRINT_W_TIME ( "Exception  when format logger cause by:    {}".format( e ) )
        logging.error ( "Exception  when format logger cause by:    {}".format( e ) )
    
    log_dir = os.path.dirname( os.path.abspath(log_file) ) 
    if print_log_init == True: PRINT_W_TIME("Creating log directory ()".format(log_dir))
    

    try :
        main_logger.handlers = [] #init blank handler first otherwise the stupid thing will create a few and print to console
        main_logger.propagate = False #Only need this if basicConfig is used

        # add a rotating handler
        from logging.handlers import RotatingFileHandler
        log_rorate_handler = RotatingFileHandler ( log_file , 
                                                   mode = log_file_mode , 
                                                   maxBytes = file_size , 
                                                   backupCount = file_count ,
                                                   encoding = None , 
                                                   delay = 0 )
        log_rorate_handler.setFormatter ( log_formatter )
        log_rorate_handler.setLevel ( log_level )
        #add the rotation handler only
        main_logger.addHandler ( log_rorate_handler )

    except Exception as e :
        PRINT_W_TIME ( "Exception when creating main logger handler cause by:    {}".format( e ) )
        logging.error ( "Exception when creating main logger handler cause by:    {}".format( e ) )

    try :
        CREATE_EXPORT_DIR ( log_dir ) # Only do this after the 2 above step, otherwise fcking main_logger will spam debug log to stdout
        if shell_output == True :
            stdout_log_handler = logging.StreamHandler ( sys.stdout )
            stdout_log_handler.setFormatter ( log_formatter )
            stdout_log_handler.setLevel ( log_level )
            #add the stdout handler properly
            main_logger.addHandler ( stdout_log_handler )
    except Exception as e :
        PRINT_W_TIME ( "Exception when creating log directory and setup log stdout handler cause by:    {}".format( e ) )
        logging.error ( "Exception when creating log directory and setup log stdout handler cause by:    {}".format ( e ) )

    if print_log_init == True: PRINT_W_TIME("Done, logging level " + log_level + " to " + os.path.abspath(log_file))

def WRITE_SINGLE_LINE_TO_FILE ( filename ,
                                text_line = "none" ,
                                append = False ) :
    try :
        if append == False :
            with open ( filename , "w+" ) as target_file :
                target_file.write ( text_line )
                logging.debug ( "Overwritten text (" + text_line + ") to  file :" + target_file.name )
            return OK
        else :
            with open ( filename , "r+" ) as target_file :
                target_file.write ( text_line )
                logging.debug ( "Append text (" + text_line + ") to  file :" + target_file.name )
            return OK
    except Exception as e :
        logging.debug ( "Exception writing text (" + text_line + ") to  file (" + target_file.name + "), cause by:     " + str ( e ) )
        raise


def READ_SINGLE_LINE_FROM_FILE ( filename ,
                                 line_position = 0 ) :
    try :
        with open ( filename , "r+" ) as target_file :
            lines = target_file.readlines ( )
        
        logging.debug ( "Opened file (" + filename + ") for reading line No: " + str ( line_position ) )
        if len ( lines ) > 0 :
            line = lines [ line_position ]
            return line
        else :
           logging.warning("File do not have any lines to read")
           return None
    except Exception as e :
        logging.debug (
            "Exception reading line position (" + str ( line_position ) + ") from  file (" + filename + "), cause by:     " + str ( e ) )
        raise


def CALCULATE_FILE_MD5 ( filename ,
                         buffersize = 65536 ) :
    try :
        with open ( filename , 'rb' ) as f :
            f = open ( filename , 'rb' )
            m = hashlib.md5 ( )
    except Exception as local_except :
        PRINT_W_TIME ( 'Error opening file ' + filename + ' for md5 calculation, due to ' + str ( local_except ) )
        logging.error ( 'Error opening file ' + filename + ' for md5 calculation, due to ' + str ( local_except ) )
        raise

    try :
        while True :
            data = f.read ( buffersize )
            if not data :
                break
            m.update ( data )
    except Exception as local_except :
        PRINT_W_TIME ( 'Error calculating file ' + filename + ' md5 hash due to ' + str ( local_except ) )
        logging.error ( 'Error calculating file ' + filename + ' md5 hash due to ' + str ( local_except ) )
        raise

    return m.hexdigest ( )


def GET_TEXT_GROUP ( regex_pattern ,
                     main_string ,
                     delimiter = '\n' ) :
    # type: (regex_pattern) -> string
    # type: (main_string) -> string
    # type: (delimiter) -> string
    """MATCH A REGEX STRING TO CHECK FOR TEXT ELEMENT WITH THE SAME HEADER IN A STRING (ELEMENT ARE IDENTIFY BY DELIMITER)
       RETURN A DICTIONARY CONTAIN TEXT GROUPS's HEADER AS KEYS(the part that match the regex pattern, without repeat) """
    try :
        regex_header = re.compile ( regex_pattern )
        config_group = dict ( )
    except Exception as local_e :
        logging.error ( 'Error to create pattern for text group analysis caused by: ' + str ( local_e ) )
        raise

    try :
        logging.info ( ' Reading desired config to getting all config header that match provided pattern: ' + regex_header.pattern )
        for lines in main_string.split ( delimiter ) :
            text_header = re.match ( regex_header , lines )
            if text_header != None and text_header.group ( 0 ) not in config_group.keys ( ) :
                config_group.update ( { text_header.group ( 0 ) : '' } )
                logging.debug ( "Created text group's header " + text_header.group ( 0 ) )
            else :
                continue
    except Exception as local_e :
        logging.error ( 'Error when getting string group using regex analysis caused by: ' + str ( local_e ) )
        raise
    return config_group


def GET_SUB_TEXT_GROUP ( main_dict ,
                         main_string ) :
    # type: (main_dict) -> dict
    # type: (main_string) -> string

    """ANALYZE A STRING TO GET TEXT GROUPS IN A STRING
       MAIN DICT MUST BE A DICTIONARY WITH KEY ALREADY CONTAIN THE HEADER USE TO GROUP TEXT'S ELEMENT
       RETURN A DICTIONARY IN WHICH KEY IS GROUP's HEADER AND VALUE IS A LIST OF THE TEXT ELEMENTS THAT START WITH THAT HEADER"""

    try :
        if isinstance ( main_dict , dict ) is not True :
            logging.error ( ' Wrong parameter type when parsing sub-string-block using header pattern analysis, skipping' )
            raise InputError(' Wrong parameter type when parsing sub-string-block using header pattern analysis, skipping')

        for text_group_header in main_dict :

            text_group_patern = text_group_header + ".*"
            logging.info ( ' Grouping all config start with: ' + text_group_patern )
            
            text_group = GET_TEXT_GROUP ( text_group_patern , main_string )
            text_group_element = [ v for v in text_group.keys ( ) ]  # convert back to a string due to GET_TEXT_GROUP return a dict

            main_dict.update ( { text_group_header : text_group_element } )
            logging.debug ( " updated text lines into group: " + text_group_header )
    except Exception as local_e :
        logging.error (
            'Error when parsing sub-string-block of header pattern(' + text_group_header + ') analysis caused by: ' + str ( local_e ) )
        raise

    return main_dict


def MULTI_REGEX_REPLACE ( regex_dict ,
                          text ) :
    # type: (regex_dict) -> dict
    # type: (text) -> string
    """REPLACE MULTIPLE REGEX/SUBTITION PAIR
       REGEX_DICT MUST BE A DICTIONARY CONTAIN REGEX MATCH PATTERN AND VALUE TO BE REPLACE"""
    try :
        for key , value in regex_dict.items ( ) :
            source = re.compile ( key )
            text = re.sub ( source , value , text )
        return text
    except Exception as local_e :
        logging.error ( "Error replacing text using regex caused by: " + str ( local_e ) )
        raise


def REPEAT_MULTI_REGEX_REPLACE ( regex_dict ,
                                 text ,
                                 repeat_time = 5 ) :
    # type: (regex_dict) -> dict
    # type: (text) -> string
    # type: (repeat_time) -> int
    """REPEAT THE REGEX REPLACE ACTION MULTIPLE TIME"""

    try :
        for i in range ( 0 , repeat_time ) :
            text = MULTI_REGEX_REPLACE ( regex_dict , text )
        return text
    except Exception as local_e :
        logging.error ( "Error replacing text multiple time using regex caused by: " + str ( local_e ) )
        raise


def SUB_LIST_IN_LIST ( sublist ,
                       mainlist ) :
    # type: (sublist) -> list
    # type: (sublist) -> list
    """RETURN A LIST OF MATCHES OF SUBLIST ELEMENT IN A MAINLIST"""

    matches = [ ]
    for i in range ( len ( mainlist ) ) :
        regex = re.compile ( str ( sublist [ 0 ] ) + ".*" )
        if re.search ( regex , str ( mainlist [ i ] ) ) != None and mainlist [ i :i + len ( sublist ) ] == sublist :
            matches.append ( sublist )
    return matches


def FORMAT_EXCEL_TO_TEXT ( text ) :
    # type: (text) -> string
    """REPEAT THE REGEX REPLACE ACTION MULTIPLE TIME"""

    try :
        excel_formatter = dict ( )
        excel_formatter.update ( { '[    \s]*\r?\n' : '\n' } )
        excel_formatter.update ( { '(    )*\r?\n' : '\n' } )
        excel_formatter.update ( { '  ' : ' ' } )
        excel_formatter.update ( { '\r?\n.*#.*\r?\n' : '\n' } )
        excel_formatter.update ( { '\r?\n\r?\n' : '\n' } )
        excel_formatter.update ( { '    ' : ' ' } )
        text = REPEAT_MULTI_REGEX_REPLACE ( excel_formatter , text )
    except Exception as local_e :
        logging.error ( "Error converting excel-formatted text tring to simple text firm, caused by: " + str ( local_e ) )
        raise
    return text


def BYTES_TO ( bytes , to = 'm' ,
               bsize = 1024 ) :
    """convert bytes to megabytes, etc.
       sample code:
           print('mb= ' + str(bytesto(314575262000000, 'm')))
       sample output:
           mb= 300002347.946
    """
    a = { 'k' : 1 , 'm' : 2 , 'g' : 3 , 't' : 4 , 'p' : 5 , 'e' : 6 }
    r = float ( bytes )
    for i in range ( a [ to ] ) :
        r = r / bsize
    return (r)


def VERIFY_FILE_MD5 ( filename = 'MissingInput' ,
                      user_md5 = None ) :
    logging.info ( '\n\n-------------------------------checking md5 of the file ' + str (
            filename ) + '------------------------------------' )
    try :
        if os.path.getsize ( filename ) < 10485760 :  # SMALLFILE
            logging.info ( "File size is small - recalculating hash for safety" )
            file_md5_hash = CALCULATE_FILE_MD5 ( filename , 65536 )

        elif os.path.isfile ( filename + '.md5' ) is False :  # BIG FILE BUT HASH FILE MISSING
            logging.info ( "File size is a little big but hash file is missing - recalculating hash for safety and save to hash file" )

            file_md5_hash = CALCULATE_FILE_MD5 ( filename , 65536 )
            WRITE_SINGLE_LINE_TO_FILE ( filename + '.md5' , file_md5_hash )

        elif os.path.isfile ( filename + '.md5' ) is True :
            logging.info ( "File size is a little big but hash file is found - using it" )
            file_md5_hash = READ_SINGLE_LINE_FROM_FILE ( filename + '.md5' , 0 )

            if file_md5_hash == None :
                logging.warning ( "Read md5 from hash file error, re-calculating and re-writing" )

                file_md5_hash = CALCULATE_FILE_MD5 ( filename , 65536 )
                WRITE_SINGLE_LINE_TO_FILE ( filename + '.md5' , file_md5_hash )

    except Exception as e :
        logging.error ( "Exception when checking file's md5 cause by:     " + str ( e ) )
        raise

    try :
        if file_md5_hash == None :
            logging.error ( "Error when checking input file md5 - skipping verify function !!!" )
            raise InputError('"Error when checking input file md5 - skipping verify function !!!"')

        elif user_md5 is None :
            logging.warning ( "User did not provide file's md5 , using  calculated result  MD5 !!!" + str ( file_md5_hash ) )
            # PRINT_W_TIME ( "User did not provide file's md5 , using newcalculated result  MD5 !!!" + str(file_md5_hash) )
            return file_md5_hash

        elif file_md5_hash != user_md5 :
            logging.error ( "WARNING!!! USER-INPUT MD5 (" + user_md5 + ") AND CALCULATED MD5 (" + str (
                file_md5_hash ) + ") FOR " + filename + " DO NOT MATCH - EXITING" )
            PRINT_W_TIME ( "WARNING!!! USER-INPUT MD5 (" + user_md5 + ") AND CALCULATED MD5 (" + str (
                file_md5_hash ) + ") FOR " + filename + " DO NOT MATCH - EXITING" )
            raise

        else :
            PRINT_W_TIME ( "File is present AND MD5 provided - matched provided MD5" + str ( file_md5_hash ) + "- Continuing " )
            logging.info ( "File is present AND MD5 provided - matched provided MD5" + str ( file_md5_hash ) + "- Continuing " )
            # For interactive debugging only
            # user_input =  raw_input(" " + "    "  "FILE IS PRESENT AND MD5 IS PROVIDED - MATCHED CALCULATED MD5- CONTINUE?
            # (Y to continue) " )
            # if user_input != 'Y' and user_input != 'y' and user_input != 'YES' and user_input != 'yes':
            #    PRINT_W_TIME (  "DID NOT SEE (Y), EXITING"
            #    sys.exit ( 0 )
            # else:
            #    PRINT_W_TIME (  "PROCEEDING"
    except Exception as e :
        logging.error ( "Exception when comparing file's md5 with use input md5 cause by:     " + str ( e ) )
        raise StandardError ( "ERROR OCCUR WHEN COMPARING FILE' MD5 HASH WITH USER INPUT MD5" )

    logging.info (
            '\n\n\--------------------finished checking md5 of the file to be uploaded, parsing IP------------------' )
    return file_md5_hash

def SET_UNBUFFERED_STDOUT():
    class Unbuffered(object):
        def __init__(self, stream):
            self.stream = stream
        def write(self, data):
            self.stream.write(data)
            self.stream.flush()
        def writelines(self, datas):
            self.stream.writelines(datas)
            self.stream.flush()
        def __getattr__(self, attr):
            return getattr(self.stream, attr)

    sys.stdout = Unbuffered(sys.stdout)

def GET_MODULE_VARIABLE ( module = None ) :
    
    """GET ALL VARIABLE OF A MODULE INTO A LIST - FOR ATTRIBUTE TRAVERSING (IGNORE ALL METHOD) """
    try:
        if module != None:
            var_list = list()
            for item in dir(module):
                if not item.startswith("__"):
                    var_list.append(item)
            return var_list
    except Exception as e :
        logging.error ( "Exception when getting variable list for module" + module +" cause by:     " + str ( e ) )

def ARGS_SETTING_OVERRIDE ( custom_setting_file = 'custom_setting.py', args = None ) :
    """OVERRIDE ALL CUSTOM SETTING FROM FILE TO ARGUMENT PARSER """

    logging.debug("Overridding custom setting from " + str(custom_setting_file) + "to argument parser")
    try:
        if not args:
            logging.warning("Received argument parser object is None, custom setting will not be set")
            return None
        elif custom_setting_file is None:
            logging.warning("Received custom setting file is None, custom setting will not be set")
            return None
        elif os.path.isfile(custom_setting_file):
            logging.info("Importing custom setting module name : " + str(custom_setting_file))
            custom_setting_module = os.path.basename(custom_setting_file) #get file name only 
            custom_setting_module = custom_setting_module.strip('.py') #move file extension to get module name
            
            #import importlib
            #imported_custom_setting = importlib.import_module(custom_setting_module)
            import imp
            imported_custom_setting = imp.load_source(custom_setting_module, custom_setting_file)
        else:
            logging.warning("Custom setting file not found: " + str(custom_setting_file) + " !!! args will not be modified")
            return None
    except Exception as e :
        logging.error ( "Exception when import custom setting file " + str(custom_setting_file) +" cause by:     " + str ( e ) )
        raise
    
    try: 
        custom_setting_list = GET_MODULE_VARIABLE(imported_custom_setting)
        for custom_setting_element in custom_setting_list:
            custom_setting_value = getattr(imported_custom_setting, custom_setting_element)
            if custom_setting_value != None:
                setattr(args, custom_setting_element, custom_setting_value)
                logging.debug ( "Imported custom setting [" + str(custom_setting_element) + "] to args")
    except Exception as e :
        logging.error ( "Exception when override setting from " + str(custom_setting_module) + " to argument parser - cause by:     " + str ( e ) )
        raise

def LD_TO_DL(list_of_dict):
    if not isinstance (list_of_dict,list):
        logging.error("This function need a list of dict, exiting!")
        raise Exception("This function need a list of dict, invalid type was provided!")
    
    dict_of_list = dict()
    for d in list_of_dict:
        for k,v in d.items():
            try:
                dict_of_list[k].append(v)
            except KeyError:
                dict_of_list[k]=[v]
    return dict_of_list

def GROUP_LIST_OF_DICT(data,
                       keylist = [],
                       keep_key = False,):
    if not isinstance (data,list):
        logging.error("This function need a list of dict, exiting!")
        raise InputError("This function need a list of dict, invalid type was provided!")

    from operator import itemgetter
    sortkeyfn = itemgetter(*keylist)
    logging.info("sorting items fields using keylist [{}]".format(sortkeyfn))
    data.sort(key=sortkeyfn)
    
    from itertools import groupby 
    grouped_data = list()
    logging.info("Grouping data base on keylist {}".format(keylist))

    for grouping_key,ungrouped_value in groupby(data, key=sortkeyfn):
        grouped_data_item = dict()
        
        i = 0
        for item in keylist:
            grouped_data_item[item] = grouping_key[i]
            i += 1
        
        other_value = []
        for value in ungrouped_value:
            if keep_key == False:
                for item in keylist:
                    value.pop(item,None)
            other_value.append(value)

        logging.debug("Key {} has been grouped".format(grouping_key))
        logging.debug("Ungrouped values is {}".format(other_value))

        grouped_data_item['vars'] = other_value
        grouped_data.append(grouped_data_item)
    return grouped_data

def MERGE_LIST_CSV_TO_XLSX(files_path, output_file):
    os.system("rm -rf " + files_path +output_file)
    list_files = os.listdir(files_path)
    import pandas as pd
    writer =  pd.ExcelWriter(files_path + output_file)
    for file in list_files:
        df = pd.read_csv(files_path + file)
        df.to_excel(writer, sheet_name=file, index=False)
    writer.save()
    writer.close()


def PROTECT_FILENAME(filename,keepcharacters = [".","_"],invalid_char_replacer = "_"):
    def CHECK_SAFE_CHAR(c):
        if c.isalnum():
            return c
        elif c in keepcharacters:
            return c
        else:
            return invalid_char_replacer
    try:
        return "".join(CHECK_SAFE_CHAR(c) for c in filename).rstrip(invalid_char_replacer)
    except Exception as e:
        logging.error("Error trying to remove illegal char from filename [{}] due to [{}]".format(filename,e))
        raise


def file_writable(file, timeout=None):
    def file_isbeing_written(file):
        size1 = os.stat(file).st_size
        time.sleep(0.5)
        size2 = os.stat(file).st_size
        if size1 != size2:
            return True
        else:
            return False

    time_start = time.time()
    time_end = time.time()
    while file_isbeing_written(file) == True:
        logging.info("File is being written by another process, wait ...")
        if timeout != None:
            runtime = time.time() - time_start
            if runtime > timeout:
                logging.info("Timeout !!!")
                return False
    return True