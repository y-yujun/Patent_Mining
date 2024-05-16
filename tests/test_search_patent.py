import unittest
from src.process_namelist import process_file
from src.search_patents import search_patents, create_faculty_database, populate_faculty_database

class Testing(unittest.TestCase):
    clean_namelist = process_file('tests/test_set.txt')
    dbname = create_faculty_database('University of Illinois')
    populate_faculty_database(dbname, clean_namelist)
    results = search_patents(dbname, 'University of Illinois')
    
    def test_length(self):
        self.assertEqual(len(self.results), 31)

    def test_grantee(self):
        for r in self.results:
            self.assertIn('universityofillinois', r[5].lower().replace(' ', ''))

    def test_specific_entry(self):
        reid_count = 0
        do_count = 0
        hwu_count = 0
        for r in self.results:
            if r[2] == 'Reid':
                reid_count += 1
            if r[2] == 'Do':
                do_count += 1
            if r[2] == 'Hwu':
                hwu_count += 1
        self.assertEqual(reid_count, 7)
        self.assertEqual(do_count, 3)
        self.assertEqual(hwu_count, 3)

if __name__ == '__main__':
    unittest.main()