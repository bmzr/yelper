import json
import psycopg2

def cleanStr4SQL(s):
    return s.replace("'","`").replace("\n"," ")

def int2BoolStr (value):
    if value == 0:
        return 'False'
    else:
        return 'True'

def attributesToSQL(data_dict, business_id, cur, conn):
    for attribute, value in data_dict.items():
        if isinstance(value, bool) or isinstance(value, int):
            value = int2BoolStr(value)
        sql_str = "INSERT INTO Attributes(business_id, attr_name, value) " + \
        "VALUES ('" + cleanStr4SQL(business_id) + "','" + cleanStr4SQL(attribute) + "','" + cleanStr4SQL(value) + "');"
        try:
            print(sql_str)
            cur.execute(sql_str)
        except Exception as e:
            print("Insert to businessTABLE failed!", e)
        conn.commit()

def insert2AttributesTable():
    #reading the JSON file
    with open('./yelp_business.JSON','r') as f:    #TODO: update path for the input file
        #outfile =  open('./yelp_business.SQL', 'w')  #uncomment this line if you are writing the INSERT statements to an output file.
        line = f.readline()
        count_line = 0

        #connect to yelpdb database on postgres server using psycopg2
        #TODO: update the database name, username, and password
        try:
            # conn = psycopg2.connect("dbname='milestone1db' user='postgres' host='localhost' password='112358'")
            conn = psycopg2.connect(dbname='yelpdb', user='postgres', password='112358', host='localhost', port='5432')
        except Exception as e:
            print('Unable to connect to database:', str(e))
        cur = conn.cursor()

        while line:
            data = json.loads(line)
            # Generate the INSERT statement for the cussent business
            # TODO: The below INSERT statement is based on a simple (and incomplete) businesstable schema. Update the statement based on your own table schema and
            # include values for all businessTable attributes
            for attribute, value in data["attributes"].items():
                if isinstance(value, dict):
                    attributesToSQL(value, data['business_id'], cur, conn)
                else:
                    if isinstance(value, bool) or isinstance(value, int):
                        value = int2BoolStr(value)
                    sql_str = "INSERT INTO Attributes(business_id, attr_name, value) " \
                            "VALUES ('" + cleanStr4SQL(data['business_id']) + "','" + cleanStr4SQL(attribute) + "','" + cleanStr4SQL(value) + "');"
                try:
                    print(sql_str)
                    cur.execute(sql_str)
                except Exception as e:
                    print("Insert to Attributes table failed!", e)
                conn.commit()
            # optionally you might write the INSERT statement to a file.
            #outfile.write(sql_str)

            line = f.readline()
            count_line +=1

        cur.close()
        conn.close()

    print(count_line)
    #outfile.close()  #uncomment this line if you are writing the INSERT statements to an output file.
    f.close()

insert2AttributesTable()