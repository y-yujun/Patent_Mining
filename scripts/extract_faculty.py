import json
import os
import sys

def get_faculty_from_json(json_file, output_file):
    faculty = []

    with open(json_file, 'r') as f:
        data = json.load(f)

    for i in range(len(data)):
        dt = data[i]['Faculty information']
        for f in dt:
            name = str(f['Name']).strip()
            if name not in faculty:
                faculty.append(name)
    
    if os.path.exists(output_file):
        os.remove(output_file)
    file = open(output_file, 'a+')
    for n in faculty:
        file.write(n + '\n')
    file.close()
    print(output_file + " created.")

if len(sys.argv) != 3:
    print("Usage: python extract_faculty.py [json_file] [output_file]")
else:
    get_faculty_from_json(sys.argv[1], sys.argv[2])