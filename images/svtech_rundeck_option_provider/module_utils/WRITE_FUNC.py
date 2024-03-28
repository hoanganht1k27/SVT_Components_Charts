

def WRITE_PY_STRUCT_TO_FILE(py_data, filename, write_mode = "w", encoding = "utf-8"):
    try:
        import io
        from pprint import pformat
        logging.info ("Writing info to file " + filename)
        prettified = pformat(py_data)

        if encoding == "utf-8":
            with io.open(filename, write_mode, encoding='utf-8') as py_file:     ##open output file
                prettified_coded = unicode(prettified,'utf-8')
                py_file.write(prettified_coded)

        elif encoding == "ascii" or encoding == "ASCII":
            with open(filename, write_mode) as py_file:     ##open output file
                py_file.write(prettified)

    except Exception as e:
        logging.error ( "Error writing result to text file due to " + str(e))
        return CRITICAL
    return OK

def WRITE_XML_TO_FILE(xml_list, filename, write_mode = "w"):
    try:
        logging.info ("Writing info to file " + filename)
        with open(filename, write_mode) as xml_file:     ##open output file
            xml_file.write('<root>\n') ##put xml root directive
               
            for xml_element in xml_list:
                xml_content = etree.tostring(xml_element, pretty_print=True) ##parsing xml content to write
                logging.debug("writing " + xml_content + " to file")
                xml_file.write(xml_content)
            
            xml_file.write('</root>') ##put xml root directive
    except Exception as e:
        logging.error ( "Error writing result to XML file due to " + str(e))
        return CRITICAL
    return OK

def WRITE_JSON_TO_FILE(json_data, filename, write_mode = "w", encoding = "utf-8"):


    import codecs,json
    # Make it work for Python 2+3 and with Unicode
    try:
        to_unicode = unicode
    except NameError:
         to_unicode = str
    logging.info ("Writing info to file " + filename)

    try:
        if type(json_data) == str:
            with open(filename, write_mode) as json_file:
                json_file.write(json_data)
        elif type(json_data) == dict:
            if encoding == "utf-8":
                with codecs.open(filename, write_mode, encoding='utf-8') as json_file:     ##codesc.open with encoding set only accepts unicode objects, be absolutely sure json_data is unicode
                    converted_str=  json.dumps(  json_string, 
                                                ensure_ascii=False,
                                                separators=(',', ': '), # To prevent Python from adding trailing whitespaces
                                                indent=4, 
                                                sort_keys=True)
                    json_file.write(to_unicode(converted_str))
            
            elif encoding == "ascii" or encoding == "ASCII":
                with open(filename, write_mode) as json_file:     ##open output file
                    json.dump(  json_string, 
                                json_file,
                                indent=4, 
                                sort_keys=True)
        else:
            raise TypeError(" Can only write dict or str content to json file!! ")
            return CRITICAL
    except Exception as e:
        logging.error ( "Error writing result to JSON file due to " + str(e))
        return CRITICAL
    return OK
