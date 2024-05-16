from process_namelist import process_file
from search_patents import create_faculty_database, populate_faculty_database, search_patents, remove_temp_table
import sys

def find_all_patents(faculty_namelist, university_name):
    clean_namelist = process_file(faculty_namelist)
    dbname = create_faculty_database(university_name)
    populate_faculty_database(dbname, clean_namelist)
    results = search_patents(dbname, university_name)
    remove_temp_table(dbname)

    print("Patent Records:")
    print("(inventor_first_name, faculty_first_name, faculty_last_name, inventor_city, inventor_state, grantee_name, patent_document_number, document_date, title_of_invention)")
    for r in results:
        print(r)
    print("Number of patents found: " + str(len(results)))


if len(sys.argv) != 3:
    print("Usage: python main.py [faculty_namelist_file] [university_name]")
    exit()

faculty_namelist_file = sys.argv[1]
university_name = sys.argv[2]
find_all_patents(faculty_namelist_file, university_name)