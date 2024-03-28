
import argparse
from pprint import pprint

parser_obj = argparse.ArgumentParser(description='\nTest fucking pandas')
parser_obj.add_argument('-p', 
                        '--pandas_mode',
                        dest = "pandas_mode",
                        type = str ,
                        help='\n        Pandas mode to be imported ')
parser_obj.add_argument('-m', 
                        '--method',
                        dest = "method",
                        type = int ,
                        help='\n        Measuring method')

args = parser_obj.parse_args()

def BYTES_TO ( bytes , to = 'm' ,
               bsize = 1024 ) :
    """convert bytes to megabytes, etc.
       sample code:
           print('mb= ' + str(bytesto(314575262000000, 'm')))
       sample output:
           mb= 300002347.946
    """
    a = { 'k' : 1 , 'm' : 2 , 'g' : 3 , 't' : 4 , 'p' : 5 , 'e' : 6 }
    r = float ( bytes/8 )
    for i in range ( a [ to ] ) :
        r = r / bsize
    return (r)


def measure_memory_1(counter):
    import resource
    resource_list =  {'ru_ixrss':'shared_memory',
                      'ru_idrss':'unshared_memory',
                      'ru_isrss':'shared_stack',
                      'ru_maxrss':'maximum_resident_set_size',
                      'ru_utime':'time_user_mode',
                      'ru_stime':'time_sys_mode'}
    for i in range(counter):
        list =  i * 1000
        mem_info = resource.getrusage(resource.RUSAGE_SELF)
        result = "===Test time {}\n".format(i)
        for resource_key, resource_name in resource_list.items():
            result += "{} : {}\t".format(resource_name,getattr(mem_info,resource_key))
        print (result)

def measure_memory_2(counter):
    import psutil
    memory_data_list =  {'rss':' non-swapped_phy_memory',
                      'vms':'total_virtual_memory',
                      'shared':'shared_memory',
                      'text':'mem_executable_code',
                      'data':'mem_non_executables',
                      'lib':'mem_shared_libraries'}
    for i in range(counter):
        list =  i * 1000
        process_info = psutil.Process()
        mem_info = process_info.memory_info()
        result = "===Test time {}\n".format(i)
        for resource_key, resource_name in memory_data_list.items():
            result += "{} : {}\t".format(resource_name,BYTES_TO(getattr(mem_info,resource_key)))
        print (result)

def measure_memory_3(counter):
    import psutil
    memory_data_list =  {'rss':' non-swapped_phy_memory',
                      'vms':'total_virtual_memory',
                      'shared':'shared_memory',
                      'text':'mem_executable_code',
                      'data':'mem_non_executables',
                      'lib':'mem_shared_libraries'}
    for i in range(counter):
        list =  i * 1000
        process_info = psutil.Process()
        mem_info = process_info.memory_info()
        result = "===Test time {}\n".format(i)
        for resource_key, resource_name in memory_data_list.items():
            result += "{} : {}\t".format(resource_name,BYTES_TO(getattr(mem_info,resource_key)))
        print (result)

@profile
def main():
    measure_function_name = "measure_memory_{}".format(args.method)
    print ("Measuring using method {}".format(args.method))
    if args.pandas_mode == "T":
        print ("=======================IMPORTING pandas")
        import pandas
        globals()[measure_function_name](3)
    
        print ("=======================IMPORT pandas again")
        from pandas import DataFrame
        globals()[measure_function_name](3)
    if args.pandas_mode == "F":
        print ("=======================NOT importing pandas")
        globals()[measure_function_name](3)
    if args.pandas_mode == "P":
        from pandas import DataFrame
        print ("=======================PARTIALLY importing pandas")
        globals()[measure_function_name](3)

if __name__ == '__main__':
    main()