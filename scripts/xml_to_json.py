import xmltodict
import json
import os

# parse an xml string into a json object using xmltodict.parse and write to the json file
def output_patent(xml_string, json_filename):
    patent = xmltodict.parse(xml_string)
    with open(json_filename, 'a') as f:
        json.dump(patent, f, indent=4)

# read an xml file and convert it to a json file 
def read_file(xml_filename, json_filename):
    xml_string = ''
    with open(xml_filename, 'r') as f:
        print('Reading file: ' + xml_filename)
        for line in f:
            if (line.startswith('<?xml version') and xml_string != '') or line.startswith('\n'):
                output_patent(xml_string, json_filename)
                with open(json_filename, 'a') as f:
                    f.write(',\n')
                xml_string = ''
            xml_string += line
        output_patent(xml_string, json_filename)


# loop through all xml files from year 2002 through 2022
# all json files created were stored in the json folder
# Note: pgb20020716.json does not exist because there was a format error in pgb20020716.xml that caused failure in conversion
for i in range(2002, 2023):
    year = str(i)
    for filename in os.listdir('xml/' + year):
        f = filename[0:12] + '.json'
        if f in os.listdir('json/' + year):
            continue
        json_filename = 'json/' + year + '/' + filename[0:12] + '.json'
        f = open(json_filename, 'w+')
        f.write('[\n')
        f.close()

        xml_filename = 'xml/' + year + '/' + filename
        read_file(xml_filename, json_filename)

        f = open(json_filename, 'a')
        f.write(']')
        f.close()