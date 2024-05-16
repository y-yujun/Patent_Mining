import sqlite3
import pathlib
import json
import os

# get connection to database
def get_database(dp_path: str) -> sqlite3.Connection:
    path_to_lib = pathlib.Path(dp_path).absolute().as_uri()
    connection = None
    try:
        connection = sqlite3.connect(f"{path_to_lib}?mode=rw", uri=True)
    except sqlite3.OperationalError:
        print("Error: Database not found")
        exit(1)
    return connection

def create_table_patents():
    connection = get_database("patents.db")
    db_cursor = connection.cursor()
    sql = """CREATE TABLE IF NOT EXISTS patents (
        document_number TEXT PRIMARY KEY,
        SIR_flag BOOLEAN,
        document_kind TEXT,
        document_date TEXT,
        application_filing_data TEXT,
        national_main_classifications TEXT,
        title_of_invention TEXT,
        not_new_invention_flag BOOLEAN
        )"""
    db_cursor.execute(sql)
    print("Table patents created successfully...")
    connection.commit()
    connection.close()

def create_table_inventors():
    connection = get_database("patents.db")
    db_cursor = connection.cursor()
    sql = """CREATE TABLE IF NOT EXISTS inventors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_number TEXT,
        first_name TEXT,
        surname TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        FOREIGN KEY (document_number) REFERENCES patents(document_number)
        )"""
    db_cursor.execute(sql)
    print("Table inventors created successfully...")
    connection.commit()
    connection.close()

def create_table_grantees():
    connection = get_database("patents.db")
    db_cursor = connection.cursor()
    sql = """CREATE TABLE IF NOT EXISTS grantees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_number TEXT,
        name TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        type TEXT,
        FOREIGN KEY (document_number) REFERENCES patents(document_number)
    )"""
    db_cursor.execute(sql)
    print("Table grantees created successfully...")
    connection.commit()
    connection.close()

# populate the database with patent records from year 2002 through 2004
# uses special encoding (e.g. B110, B220) in the xml file 
# to learn more about the encoding, refer to the Grant Red Book provided by the USPTO Office of Information Dissemination Service 
# https://www.uspto.gov/sites/default/files/products/PatentGrantSGMLv19-Documentation.pdf
# Note: the data in pgb20020430.json and pgb20020528.json were not populated into the database due to format error
def populate2002Through2004():
    connection = get_database("patents.db")
    db_cursor = connection.cursor()
    for i in range(2002, 2005):
        year = str(i)
        for filename in os.listdir('json/' + year):
            if filename == '.DS_Store' or filename == 'pgb20020430.json' or filename == 'pgb20020528.json':
                continue
            filename = 'json/' + year + '/' + filename
            with open(filename, 'r') as f:
                data = json.load(f)
            for i in range(len(data)):

                # patents
                patent = data[i]
                document_number = patent['PATDOC']['SDOBI']['B100']['B110']['DNUM']['PDAT']
                SIR_flag = 'B122US' in patent['PATDOC']['SDOBI']['B100']
                document_kind = patent['PATDOC']['SDOBI']['B100']['B130']['PDAT']
                document_date = patent['PATDOC']['SDOBI']['B100']['B140']['DATE']['PDAT']
                application_filing_date = patent['PATDOC']['SDOBI']['B200']['B220']['DATE']['PDAT']
                national_main_classification = patent['PATDOC']['SDOBI']['B500']['B520']['B521']['PDAT']
                title_of_invention = patent['PATDOC']['SDOBI']['B500']['B540']['STEXT']['PDAT']
                if 'B600' not in patent['PATDOC']['SDOBI']:
                    not_new_invention_flag = False
                else:
                    not_new_invention_flag = \
                    'B640' in patent['PATDOC']['SDOBI']['B600'] or \
                    'B641US' in patent['PATDOC']['SDOBI']['B600'] or \
                    'B645' in patent['PATDOC']['SDOBI']['B600'] or \
                    'B645US' in patent['PATDOC']['SDOBI']['B600'] or \
                    'B660' in patent['PATDOC']['SDOBI']['B600']
                    if 'B630' in patent['PATDOC']['SDOBI']['B600'] and not_new_invention_flag != True:
                        not_new_invention_flag = \
                        'B631' in patent['PATDOC']['SDOBI']['B600']['B630'] or \
                        'B632' in patent['PATDOC']['SDOBI']['B600']['B630'] or \
                        'B633' in patent['PATDOC']['SDOBI']['B600']['B630']
                if type(title_of_invention) is not str:
                    title_of_invention = 'null'
                db_cursor.execute("INSERT INTO patents VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (document_number, SIR_flag, document_kind, document_date, application_filing_date, national_main_classification, title_of_invention, not_new_invention_flag))

                # inventors (every patent must have at least one inventor)
                inventors = patent['PATDOC']['SDOBI']['B700']['B720']['B721']
                if type(inventors) is list:
                    for inventor in inventors:
                        first_name = 'null'
                        last_name = 'null'
                        city = 'null'
                        state = 'null'
                        country = 'null'
                        if 'FNM' in inventor['PARTY-US']['NAM']:
                            first_name = inventor['PARTY-US']['NAM']['FNM']['PDAT']
                        if 'SNM' in inventor['PARTY-US']['NAM']:
                            last_name = inventor['PARTY-US']['NAM']['SNM']['STEXT']['PDAT']
                        if 'ADR' in inventor['PARTY-US']:
                            if 'CITY' in inventor['PARTY-US']['ADR']:
                                city = inventor['PARTY-US']['ADR']['CITY']['PDAT']
                            if 'STATE' in inventor['PARTY-US']['ADR']:
                                state = inventor['PARTY-US']['ADR']['STATE']['PDAT']
                            if 'CTRY' in inventor['PARTY-US']['ADR']:
                                country = inventor['PARTY-US']['ADR']['CTRY']['PDAT']
                            else:
                                country = 'US'
                        if type(first_name) is not str:
                            first_name = 'null'
                        if type(city) is not str:
                            city = 'null'
                        db_cursor.execute("INSERT INTO inventors VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, first_name, last_name, city, state, country))
                else:
                    first_name = 'null'
                    last_name = 'null'
                    city = 'null'
                    state = 'null'
                    country = 'null'
                    if 'FNM' in inventors['PARTY-US']['NAM']:
                        first_name = inventors['PARTY-US']['NAM']['FNM']['PDAT']
                    if 'SNM' in inventors['PARTY-US']['NAM']:
                        last_name = inventors['PARTY-US']['NAM']['SNM']['STEXT']['PDAT']
                    if 'CITY' in inventors['PARTY-US']['ADR']:
                        city = inventors['PARTY-US']['ADR']['CITY']['PDAT']
                    if 'STATE' in inventors['PARTY-US']['ADR']:
                        state = inventors['PARTY-US']['ADR']['STATE']['PDAT']
                    if 'CTRY' in inventors['PARTY-US']['ADR']:
                        country = inventors['PARTY-US']['ADR']['CTRY']['PDAT']
                    else:
                        country = 'US'
                    db_cursor.execute("INSERT INTO inventors VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, first_name, last_name, city, state, country))

                # assignees (not every patent has an assignee)
                if 'B730' in patent['PATDOC']['SDOBI']['B700']:
                    assignees = patent['PATDOC']['SDOBI']['B700']['B730']
                    if type(assignees) is list:
                        for assignee in assignees:
                            name = 'null'
                            city = 'null'
                            state = 'null'
                            country = 'null'

                            # company's name or individual's name
                            if 'ONM' in assignee['B731']['PARTY-US']['NAM']:
                                name = assignee['B731']['PARTY-US']['NAM']['ONM']['STEXT']['PDAT']
                            elif 'FNM' in assignee['B731']['PARTY-US']['NAM'] and 'SNM' in assignee['B731']['PARTY-US']['NAM']:
                                name = assignee['B731']['PARTY-US']['NAM']['FNM']['PDAT'] + ' ' + assignee['B731']['PARTY-US']['NAM']['SNM']['STEXT']['PDAT']
                            elif 'SNM' in assignee['B731']['PARTY-US']['NAM']:
                                name = assignee['B731']['PARTY-US']['NAM']['SNM']['STEXT']['PDAT']
                            elif 'FNM' in assignee['B731']['PARTY-US']['NAM']:
                                name = assignee['B731']['PARTY-US']['NAM']['FNM']['PDAT']

                            if 'ADR' in assignee['B731']['PARTY-US']:
                                if 'CITY' in assignee['B731']['PARTY-US']['ADR']:
                                    city = assignee['B731']['PARTY-US']['ADR']['CITY']['PDAT']
                                if 'STATE' in assignee['B731']['PARTY-US']['ADR']:
                                    state = assignee['B731']['PARTY-US']['ADR']['STATE']['PDAT']
                                if 'CTRY' in assignee['B731']['PARTY-US']['ADR']:
                                    country = assignee['B731']['PARTY-US']['ADR']['CTRY']['PDAT']
                                else:
                                    country = 'US'
                            grantee_type = assignee['B732US']['PDAT']
                            db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, name, city, state, country, grantee_type))
                    else:
                        name = 'null'
                        city = 'null'
                        state = 'null'
                        country = 'null'

                        # company's name or individual's name
                        if 'ONM' in assignees['B731']['PARTY-US']['NAM']:
                            name = assignees['B731']['PARTY-US']['NAM']['ONM']['STEXT']['PDAT']
                        elif 'FNM' in assignees['B731']['PARTY-US']['NAM'] and 'SNM' in assignees['B731']['PARTY-US']['NAM']:
                            name = assignees['B731']['PARTY-US']['NAM']['FNM']['PDAT'] + ' ' + assignees['B731']['PARTY-US']['NAM']['SNM']['STEXT']['PDAT']
                        elif 'SNM' in assignees['B731']['PARTY-US']['NAM']:
                            name = assignees['B731']['PARTY-US']['NAM']['SNM']['STEXT']['PDAT']
                        elif 'FNM' in assignees['B731']['PARTY-US']['NAM']:
                            name = assignees['B731']['PARTY-US']['NAM']['FNM']['PDAT']
                        if type(name) is list:
                            name = " ".join(name)

                        if 'ADR' in assignees['B731']['PARTY-US']:
                            if 'CITY' in assignees['B731']['PARTY-US']['ADR']:
                                city = assignees['B731']['PARTY-US']['ADR']['CITY']['PDAT']
                            if 'STATE' in assignees['B731']['PARTY-US']['ADR']:
                                state = assignees['B731']['PARTY-US']['ADR']['STATE']['PDAT']
                            if 'CTRY' in assignees['B731']['PARTY-US']['ADR']:
                                country = assignees['B731']['PARTY-US']['ADR']['CTRY']['PDAT']
                            else:
                                country = 'US'
                        grantee_type = assignees['B732US']['PDAT']
                        db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, name, city, state, country, grantee_type))
        print("Patent records in year " + year + " imported into database successfully...")

    connection.commit()
    connection.close()

# populate the database with patent records from year 2005 through 2012
# did not use special encoding (e.g. B110, B220) in the xml file anymore, but replaced by more straightforward terms 
# to learn more about the new encoding, refer to Patent Grant Full Text Data/XML Version 4.2 ICE  (JAN 2007 – DEC 2012)  
# https://bulkdata.uspto.gov/data/patent/grant/redbook/2007/PatentGrantXMLv4.2Documentation.doc
# Note: the data in ipgb20050920.json was not populated into the database due to format error
def populate2005Through2012():
    connection = get_database("patents.db")
    db_cursor = connection.cursor()
    for i in range(2005, 2013):
        year = str(i)
        for filename in os.listdir('json/' + year):
            if filename == '.DS_Store' or filename == 'ipgb20050920.json':
                continue
            filename = 'json/' + year + '/' + filename
            with open(filename, 'r') as f:
                data = json.load(f)
            for i in range(len(data)):

                # patents
                patent = data[i]
                document_number = patent['us-patent-grant']['us-bibliographic-data-grant']['publication-reference']['document-id']['doc-number']
                SIR_flag = 'us-sir-flag' in patent['us-patent-grant']['us-bibliographic-data-grant']
                document_kind = patent['us-patent-grant']['us-bibliographic-data-grant']['publication-reference']['document-id']['kind']
                document_date = patent['us-patent-grant']['us-bibliographic-data-grant']['publication-reference']['document-id']['date']
                application_filing_date = patent['us-patent-grant']['us-bibliographic-data-grant']['application-reference']['document-id']['date']
                national_main_classification = patent['us-patent-grant']['us-bibliographic-data-grant']['classification-national']['main-classification']
                if '#text' in patent['us-patent-grant']['us-bibliographic-data-grant']['invention-title']:
                    title_of_invention = patent['us-patent-grant']['us-bibliographic-data-grant']['invention-title']['#text']
                else:
                    title_of_invention = 'null'
                if 'us-related-documents' not in patent['us-patent-grant']['us-bibliographic-data-grant']:
                    not_new_invention_flag = False
                else:
                    not_new_invention_flag = \
                    'reissue' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'us-divisional-reissue' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'reexamination' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'us-reexamination-reissue-merger' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'substitution' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'continuation' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'continuation-in-part' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'continuing-reissue' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents']
                if type(title_of_invention) is not str:
                    title_of_invention = 'null'
                db_cursor.execute("INSERT INTO patents VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (document_number, SIR_flag, document_kind, document_date, application_filing_date, national_main_classification, title_of_invention, not_new_invention_flag))

                # inventors (every patent must have at least one inventor)
                inventors = patent['us-patent-grant']['us-bibliographic-data-grant']['parties']['applicants']['applicant']
                if type(inventors) is list:
                    for inventor in inventors:
                        first_name = 'null'
                        last_name = 'null'
                        city = 'null'
                        state = 'null'
                        country = 'null'
                        if 'addressbook' in inventor:
                            if 'first-name' in inventor['addressbook']:
                                first_name = inventor['addressbook']['first-name']
                            if 'last-name' in inventor['addressbook']:
                                last_name = inventor['addressbook']['last-name']
                            if 'address' in inventor['addressbook']:
                                if 'city' in inventor['addressbook']['address']:
                                    city = inventor['addressbook']['address']['city']
                                if 'state' in inventor['addressbook']['address']:
                                    state = inventor['addressbook']['address']['state']
                                if 'country' in inventor['addressbook']['address']:
                                    country = inventor['addressbook']['address']['country']
                                else:
                                    country = 'US'
                            if type(first_name) is not str:
                                first_name = 'null'
                            if type(city) is not str:
                                city = 'null'
                        db_cursor.execute("INSERT INTO inventors VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, first_name, last_name, city, state, country))
                else:
                    first_name = 'null'
                    last_name = 'null'
                    city = 'null'
                    state = 'null'
                    country = 'null'
                    if 'addressbook' in inventors:
                        if 'first-name' in inventors['addressbook']:
                            first_name = inventors['addressbook']['first-name']
                        if 'last-name' in inventors['addressbook']:
                            last_name = inventors['addressbook']['last-name']
                        if 'address' in inventors['addressbook']:
                                if 'city' in inventors['addressbook']['address']:
                                    city = inventors['addressbook']['address']['city']
                                if 'state' in inventors['addressbook']['address']:
                                    state = inventors['addressbook']['address']['state']
                                if 'country' in inventors['addressbook']['address']:
                                    country = inventors['addressbook']['address']['country']
                                else:
                                    country = 'US'
                    db_cursor.execute("INSERT INTO inventors VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, first_name, last_name, city, state, country))

                # assignees (every patent has an assignee)
                if 'assignees' in patent['us-patent-grant']['us-bibliographic-data-grant']:
                    assignees = patent['us-patent-grant']['us-bibliographic-data-grant']['assignees']['assignee']
                    if type(assignees) is list:
                        for assignee in assignees:
                            name = 'null'
                            city = 'null'
                            state = 'null'
                            country = 'null'
                            grantee_type = 'null'

                            # company's name or individual's name
                            if 'addressbook' in assignee:
                                if 'orgname' in assignee['addressbook']:
                                    name = assignee['addressbook']['orgname']

                                if 'address' in assignee['addressbook']:
                                    if 'city' in assignee['addressbook']['address']:
                                        city = assignee['addressbook']['address']['city']
                                    if 'state' in assignee['addressbook']['address']:
                                        state = assignee['addressbook']['address']['state']
                                    if 'country' in assignee['addressbook']['address']:
                                        country = assignee['addressbook']['address']['country']
                                    else:
                                        country = 'US'
                                grantee_type = assignee['addressbook']['role']
                            db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, name, city, state, country, grantee_type))
                    else:
                        name = 'null'
                        city = 'null'
                        state = 'null'
                        country = 'null'
                        grantee_type = 'null'

                        # company's name or individual's name
                        if 'addressbook' in assignees:
                            if 'orgname' in assignees['addressbook']:
                                    name = assignees['addressbook']['orgname']

                            if 'address' in assignees['addressbook']:
                                if 'city' in assignees['addressbook']['address']:
                                    city = assignees['addressbook']['address']['city']
                                if 'state' in assignees['addressbook']['address']:
                                    state = assignees['addressbook']['address']['state']
                                if 'country' in assignees['addressbook']['address']:
                                    country = assignees['addressbook']['address']['country']
                                else:
                                    country = 'US'
                            grantee_type = assignees['addressbook']['role']
                        db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, name, city, state, country, grantee_type))

                else:
                    db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, 'null', 'null', 'null', 'null', 'null'))
        print("Patent records in year " + year + " imported into database successfully...")
    connection.commit()
    connection.close()

# populate the database with patent records from year 2013 through 2022
# slight changes to encoding structure compared to year 2005-2012
# e.g. a patent might not have an assignee
def populate2013Through2022():
    connection = get_database("patents.db")
    db_cursor = connection.cursor() 
    for i in range(2013, 2023):
        year = str(i)
        for filename in os.listdir('json/' + year):
            if filename == '.DS_Store':
                continue
            filename = 'json/' + year + '/' + filename
            with open(filename, 'r') as f:
                data = json.load(f)
            for i in range(len(data)):

                # patents
                patent = data[i]
                document_number = patent['us-patent-grant']['us-bibliographic-data-grant']['publication-reference']['document-id']['doc-number']
                SIR_flag = 'us-sir-flag' in patent['us-patent-grant']['us-bibliographic-data-grant']
                document_kind = patent['us-patent-grant']['us-bibliographic-data-grant']['publication-reference']['document-id']['kind']
                document_date = patent['us-patent-grant']['us-bibliographic-data-grant']['publication-reference']['document-id']['date']
                application_filing_date = patent['us-patent-grant']['us-bibliographic-data-grant']['application-reference']['document-id']['date']
                if 'classification-national' in patent['us-patent-grant']['us-bibliographic-data-grant']:
                    national_main_classification = patent['us-patent-grant']['us-bibliographic-data-grant']['classification-national']['main-classification']
                else:
                    national_main_classification = 'null'
                if '#text' in patent['us-patent-grant']['us-bibliographic-data-grant']['invention-title']:
                    title_of_invention = patent['us-patent-grant']['us-bibliographic-data-grant']['invention-title']['#text']
                else:
                    title_of_invention = 'null'
                if 'us-related-documents' not in patent['us-patent-grant']['us-bibliographic-data-grant']:
                    not_new_invention_flag = False
                else:
                    not_new_invention_flag = \
                    'reissue' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'us-divisional-reissue' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'reexamination' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'us-reexamination-reissue-merger' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'substitution' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'continuation' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'continuation-in-part' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents'] or \
                    'continuing-reissue' in patent['us-patent-grant']['us-bibliographic-data-grant']['us-related-documents']
                if type(title_of_invention) is not str:
                    title_of_invention = 'null'
                db_cursor.execute("INSERT INTO patents VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (document_number, SIR_flag, document_kind, document_date, application_filing_date, national_main_classification, title_of_invention, not_new_invention_flag))

                # inventors (every patent must have at least one inventor)
                if 'us-parties' in patent['us-patent-grant']['us-bibliographic-data-grant']:
                    inventors = patent['us-patent-grant']['us-bibliographic-data-grant']['us-parties']['us-applicants']['us-applicant']
                elif 'parties' in patent['us-patent-grant']['us-bibliographic-data-grant']:
                    inventors = patent['us-patent-grant']['us-bibliographic-data-grant']['parties']['applicants']['applicant']
                if type(inventors) is list:
                    for inventor in inventors:
                        first_name = 'null'
                        last_name = 'null'
                        city = 'null'
                        state = 'null'
                        country = 'null'
                        if 'addressbook' in inventor:
                            if 'first-name' in inventor['addressbook']:
                                first_name = inventor['addressbook']['first-name']
                            if 'last-name' in inventor['addressbook']:
                                last_name = inventor['addressbook']['last-name']
                            if 'address' in inventor['addressbook']:
                                if 'city' in inventor['addressbook']['address']:
                                    city = inventor['addressbook']['address']['city']
                                if 'state' in inventor['addressbook']['address']:
                                    state = inventor['addressbook']['address']['state']
                                if 'country' in inventor['addressbook']['address']:
                                    country = inventor['addressbook']['address']['country']
                                else:
                                    country = 'US'
                            # print(document_number, first_name, last_name, city, state, country)
                            if type(first_name) is not str:
                                first_name = 'null'
                            if type(city) is not str:
                                city = 'null'
                        db_cursor.execute("INSERT INTO inventors VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, first_name, last_name, city, state, country))
                else:
                    first_name = 'null'
                    last_name = 'null'
                    city = 'null'
                    state = 'null'
                    country = 'null'
                    if 'addressbook' in inventors:
                        if 'first-name' in inventors['addressbook']:
                            first_name = inventors['addressbook']['first-name']
                        if 'last-name' in inventors['addressbook']:
                            last_name = inventors['addressbook']['last-name']
                        if 'address' in inventors['addressbook']:
                                if 'city' in inventors['addressbook']['address']:
                                    city = inventors['addressbook']['address']['city']
                                if 'state' in inventors['addressbook']['address']:
                                    state = inventors['addressbook']['address']['state']
                                if 'country' in inventors['addressbook']['address']:
                                    country = inventors['addressbook']['address']['country']
                                else:
                                    country = 'US'
                    db_cursor.execute("INSERT INTO inventors VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, first_name, last_name, city, state, country))

                # assignees (a patent might not have an assignee)
                if 'assignees' in patent['us-patent-grant']['us-bibliographic-data-grant']:
                    assignees = patent['us-patent-grant']['us-bibliographic-data-grant']['assignees']['assignee']
                    if type(assignees) is list:
                        for assignee in assignees:
                            name = 'null'
                            city = 'null'
                            state = 'null'
                            country = 'null'
                            grantee_type = 'null'

                            # company's name or individual's name
                            if 'addressbook' in assignee:
                                if 'orgname' in assignee['addressbook']:
                                    name = assignee['addressbook']['orgname']

                                if 'address' in assignee['addressbook']:
                                    if 'city' in assignee['addressbook']['address']:
                                        city = assignee['addressbook']['address']['city']
                                    if 'state' in assignee['addressbook']['address']:
                                        state = assignee['addressbook']['address']['state']
                                    if 'country' in assignee['addressbook']['address']:
                                        country = assignee['addressbook']['address']['country']
                                    else:
                                        country = 'US'
                                grantee_type = assignee['addressbook']['role']
                            db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, name, city, state, country, grantee_type))
                    else:
                        name = 'null'
                        city = 'null'
                        state = 'null'
                        country = 'null'
                        grantee_type = 'null'

                        # company's name or individual's name
                        if 'addressbook' in assignees:
                            if 'orgname' in assignees['addressbook']:
                                    name = assignees['addressbook']['orgname']

                            if 'address' in assignees['addressbook']:
                                if 'city' in assignees['addressbook']['address']:
                                    city = assignees['addressbook']['address']['city']
                                if 'state' in assignees['addressbook']['address']:
                                    state = assignees['addressbook']['address']['state']
                                if 'country' in assignees['addressbook']['address']:
                                    country = assignees['addressbook']['address']['country']
                                else:
                                    country = 'US'
                            grantee_type = assignees['addressbook']['role']
                        db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, name, city, state, country, grantee_type))

                else:
                    db_cursor.execute("INSERT INTO grantees VALUES (NULL, ?, ?, ?, ?, ?, ?)", (document_number, 'null', 'null', 'null', 'null', 'null'))
        print("Patent records in year " + year + " imported into database successfully...")
    connection.commit()
    connection.close()

create_table_patents()
create_table_inventors()
create_table_grantees()

populate2002Through2004()
populate2005Through2012()
populate2013Through2022()

print("Database import is complete.")