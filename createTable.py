import sqlite3 as lite


#database = '/home/gsiebrecht/PycharmProjects/bin_temperature/customer.db'
database = 'customer.db'

def reset():
    con = lite.connect(database)
    with con:
        cur = con.cursor()
        print("dropping table")
        cur.execute("DROP TABLE IF EXISTS tbl_data")
        #cur.execute("CREATE TABLE tbl_data(timestamp DATETIME, temp NUMERIC)")
        cur.execute("CREATE TABLE tbl_data(timestamp DATETIME, temp NUMERIC, siteid NUMERIC, soiltemp NUMERIC, sensor1 NUMERIC, sensor2 NUMERIC, sensor3 NUMERIC, sensor4 NUMERIC, sensor5 NUMERIC, sensor6 NUMERIC)")
        #cur.execute("CREATE TABLE tbl_timer(timestamp DATETIME)")
        print("function reset table")
reset()
