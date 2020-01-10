#!flask/bin/python3
from flask import Flask, jsonify, render_template
from flask import make_response
from flask import abort
from flask import request
from flask import flash, redirect
import sqlite3
from datetime import datetime, timezone, timedelta
import json

database = '/var/www/html/binweb/bin_temperature/sensorsData.db'
#database = 'customer.db'
app = Flask(__name__)

tasks = []
dict = {}
test = {}


##############
@app.route('/api/download', methods=['GET'])
def download():  # This returns all entries in the database into a dict and then converts to json.
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    sql = "SELECT * FROM tbl_data WHERE siteid  = 1 ORDER BY timestamp DESC"
    # we have to change site id to a list because when we get to double digits it thinks we are passing in a list of characters.
    #curs.execute(sql, [siteid])
    curs.execute(sql)
    data = curs.fetchall()
    dates = []
    temps = []
    # siteids = []
    soiltemps = []
    sensor1 = []
    sensor2 = []
    # sensor3 = []
    # sensor4 = []
    # sensor5 = []
    # sensor6 = []
    for row in reversed(data):
        dates.append(row[0])
        temps.append(row[1])
        #siteids.append(row[2])
        soiltemps.append(row[3])
         #sensor1.append(row[4])
        if row[4] == None:
            #convert None to null so the chart is happy
            sensor1.append('null')
        elif row[4] == 0:
            sensor1.append('null')
        else:
            sensor1.append(row[4])
        sensor2.append(row[5])
        # sensor3append(row[6])
        # sensor4.append(row[7])
        # sensor5.append(row[8])
        # sensor6.append(row[9])

        dict[row[0]] = {'date': row[0], 'temp': row[1], 'soiltemps':row[3] ,'sensor1': row[4], 'sensor2': row[5]}
    conn.close()
    #print(dict)
    #return dates, temps, soiltemps, sensor1, sensor2
    return jsonify({'data': dict})
    


#############


@app.route('/api/getall', methods=['GET'])
def get_all(start_date='1900-01-01', end_date='2050-01-01'):  # this is for the chart
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    print("start date in getall function: " + start_date)
    print("end date in getall function: " + end_date)
    sql = "SELECT * FROM pidata WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp DESC"
    curs.execute(sql, [start_date, end_date])
    data = curs.fetchall()
    dates = []
    airtemps = []
    soiltemps = []
    cputemps= []
    sensor1 = []
    sensor2 = []

    for row in reversed(data):
        dates.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M'))
        #topic
        airtemps.append(row[2])
        # siteids.append(row[3])
        soiltemps.append(row[4])
        #humidity5
        if row[6] is None or row[6] == 0:
            # convert None to null so the chart is happy 
            cputemps.append('null')
        else:
            cputemps.append(row[6])

        if row[7] is None or row[7] == 0:
            # convert None to null so the chart is happy
            sensor1.append('null')
        else:
            sensor1.append(row[7])

        if row[8] is None or row[8] == 0 or row[8] == 185:
            # convert None to null so the chart is happy
            sensor2.append('null')
        else:
            sensor2.append(row[8])

        # sensor3.append(row[6])
        # sensor4.append(row[7])
        # sensor5.append(row[8])
        # sensor6.append(row[9])


#dict[row[0]] = {'date': row[0], 'temp': row[1], 'soiltemps':row[3] ,'sensor1': row[4], 'sensor2': row[5]}
#return jsonify({'data': dict})

    conn.close()
    return dates ,airtemps, soiltemps, cputemps, sensor1, sensor2

@app.route('/api/getjson', methods=['GET'])
def get_json(start_date='1900-01-01', end_date='2050-01-01'):  # this is for the chart
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    print("start date in getall function: " + start_date)
    print("end date in getall function: " + end_date)
    sql = "SELECT * FROM pidata WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp DESC"
    curs.execute(sql, [start_date, end_date])
    data = curs.fetchall()
    dates = []
    airtemps = []
    soiltemps = []
    cputemps= []
    sensor1 = []
    sensor2 = []

    for row in reversed(data):
        dates.append(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M'))
        #topic
        airtemps.append(row[2])
        # siteids.append(row[3])
        soiltemps.append(row[4])
        #humidity5
        if row[6] is None or row[6] == 0:
            # convert None to null so the chart is happy 
            cputemps.append('null')
        else:
            cputemps.append(row[6])

        if row[7] is None or row[7] == 0:
            # convert None to null so the chart is happy
            sensor1.append('null')
        else:
            sensor1.append(row[7])

        if row[8] is None or row[8] == 0 or row[8] == 185:
            # convert None to null so the chart is happy
            sensor2.append('null')
        else:
            sensor2.append(row[8])

        # sensor3.append(row[6])
        # sensor4.append(row[7])
        # sensor5.append(row[8])
        # sensor6.append(row[9])


        dict[row[0]] = {'date': row[0], 'airtemp': row[2], 'soiltemps':row[4] ,'sensor1': row[7], 'sensor2': row[8]}
    
    x = json.dumps(dict)
    json_object = json.loads(x)
    json_formatted_str = json.dumps(json_object, indent=2)
    
    #print(json_formatted_str)
    #return json_formatted_str
    
    
    return jsonify({'data': dict})






def get_average():
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    sql = "select avg(sensor1) from(select sensor1 from pihq WHERE sensor1 <> 'None' AND sensor1 <> '0' Order By timestamp desc limit 20)"
    # we have to change site id in the execute function to a list because when we get to double digits it thinks we are passing in a list of characters.
    curs.execute(sql)
    data = curs.fetchall()
    x = data[0]
    y= round(x[0],2)
    return y


def check_rapid_rise(current_temp, x):
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    temp_week_ago = 0
    for row in curs.execute(
            "SELECT * FROM pihq WHERE timestamp BETWEEN datetime('now', '-8 days') AND datetime('now', '-6 days') LIMIT 1;"):
        temp_week_ago = row[x]
    conn.close()
    if temp_week_ago == None:
            temp_week_ago = 0
    temp_difference = current_temp - temp_week_ago
    #print('temp difference=', temp_difference)
    if temp_difference >= 3 and current_temp > 32:
        #print("DANGER RAPID RISE DETECTED 3 degrees in one week at 32.")
        # set_temp_alarm('true')
        formatted_temp_difference = round(temp_difference, 1)
        return formatted_temp_difference, temp_week_ago
    else:
        formatted_temp_difference = round(temp_difference, 1)
        return formatted_temp_difference, temp_week_ago


def get_current_data():  # get current values for display on web page
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    current_time = []
    current_temp = []
    current_soiltemp = []
    sensor1 = []
    sensor2 = []
    for row in curs.execute("SELECT * FROM pidata ORDER BY timestamp DESC LIMIT 1"):
        current_time = str(row[0])
        current_temp = row[2]
        current_soiltemp = row[4]
        current_sensor1 = row[7]
        current_sensor2 = row[8]
    conn.close()

    # send current temp and databse row to check for rapid rise
    temp_difference, temp_week_ago = check_rapid_rise(current_temp, 2)
    temp_difference1, temp_week_ago1 = check_rapid_rise(current_sensor1, 7)
    temp_difference2, temp_week_ago2 = check_rapid_rise(current_sensor2, 8)

    return current_time, current_temp, temp_difference, temp_week_ago, current_soiltemp, current_sensor1, current_sensor2, temp_week_ago1, temp_week_ago2, temp_difference1, temp_difference2


@app.route('/linechart', methods=['get','post'])
def linechart():
    if not request.cookies.get('siteid'):
        res = make_response(redirect('/binapi/login'))
        return res
    mycookie = request.cookies.get('siteid')
    siteid=mycookie
    x = "0"
    if not request.values.get("aStartDate") and not request.values.get("aEndDate"): 
        dates, airtemps, soiltemps, cputemps, sensor1, sensor2 = get_all(siteid)    
    if request.values.get("aStartDate") and request.values.get("aEndDate"):
        start_date = request.values.get("aStartDate")
        end_date = request.values.get("aEndDate")
        dates, airtemps, soiltemps, cputemps, sensor1, sensor2 = get_all(siteid, start_date, end_date)
    if request.values.get("aStartDate") and not request.values.get("aEndDate"):
        start_date = request.values.get("aStartDate")
        dates, airtemps, soiltemps, cputemps, sensor1, sensor2 = get_all(siteid, start_date)
    if request.values.get("aEndDate") and not request.values.get("aStartDate"):
        end_date = request.values.get("aEndDate")
        dates, airtemps, soiltemps, cputemps, sensor1, sensor2 = get_all(siteid, x, end_date)
    
    #  print(dict)
    # return jsonify({'data': dict})
    current_time, current_temp, temp_difference, current_soiltemp, temp_week_ago, current_sensor1, current_sensor2, temp_week_ago1, temp_week_ago2, temp_difference1, temp_difference2 = get_current_data()
   
    shortdate = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M')
    
    return render_template('index.html', siteid=siteid, temp_week_ago=temp_week_ago, temp_difference=temp_difference, temp_difference1=temp_difference1, temp_difference2=temp_difference2, temps=airtemps, dates=dates, soiltemps=soiltemps, current_soiltemp=current_soiltemp ,sensor1=sensor1,sensor2=sensor2, current_sensor1=current_sensor1, current_sensor2=current_sensor2, shortdate=shortdate, current_temp=current_temp, temp_week_ago1=temp_week_ago1, temp_week_ago2=temp_week_ago2)


@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.cookies.get('siteid'):
        flash_text()
    error = ''
    siteid = request.values.get("asiteid")
    #print(siteid)
    if siteid:
        res = cookie(siteid)
        return res
    return render_template('login.html', error=error)


def flash_text():
    flash("You are logged in")
    print("you are logged in")

@app.route('/cookie/')
def cookie(siteid = '0'):
    if not request.cookies.get('siteid'):
        res = make_response(redirect('/binapi/dashboard'))
        res.set_cookie('siteid', siteid, max_age=60*60*24*365*2)
        return res
    else:
        dashboard()
        #res = make_response("Value of cookie siteid is {}".format(request.cookies.get('siteid')))
    return dashboard()



@app.route('/dashboard')
def dashboard():
    if not request.cookies.get('siteid'):
        res = make_response(redirect('/binapi/login'))
        return res
    mycookie = request.cookies.get('siteid')
    siteid = mycookie
    #  print(dict)
    # return jsonify({'data': dict})
    #avg = get_average()

    current_time, current_temp, temp_difference, temp_week_ago, current_soiltemp, current_sensor1, current_sensor2, temp_week_ago1, temp_week_ago2, temp_difference1, temp_difference2 = get_current_data()
    
    #print("current soiltemp- " + str(current_soiltemp))

    dates, airtemps, soiltemps, cputemps, sensor1, sensor2 = get_all(siteid)

    avg = 0

    return render_template('dashboard.html', siteid=siteid, avg=avg, temp_week_ago=temp_week_ago, mycookie=mycookie, temp_difference=temp_difference,temps=airtemps, dates=dates, soiltemps=soiltemps ,sensor1=sensor1, current_sensor1=current_sensor1, current_sensor2=current_sensor2, sensor2=sensor2, current_time=current_time, current_temp=current_temp, current_soiltemp=current_soiltemp, temp_week_ago1=temp_week_ago1, temp_week_ago2=temp_week_ago2 )


@app.route('/delete-cookie/')
def delete_cookie():
    res = make_response("Logged Out")
    res.set_cookie('siteid', max_age=0)
    return res

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'temp' in request.json:
        abort(400)
    task = {
        'temp': request.json['temp'],
        'siteid': request.json['siteid'],
        'soiltemp': request.json['soiltemp'],
        'sensor1' : request.json['sensor1'],
        'sensor2' : request.json['sensor2']
    }
    temp = request.json['temp']
    siteid = request.json.get('siteid')
    soiltemp = request.json.get('soiltemp')
    sensor1 = request.json.get('sensor1')
    sensor2 = request.json.get('sensor2')
    print("calling inserting data into database function")
    insert_data(temp, siteid, soiltemp, sensor1, sensor2)
    print(temp)
    print(siteid)
    print(soiltemp)
    print("sensor2= " + str(sensor2))
    return jsonify({'task': task}), 201

    # return temp, siteid


def insert_data(temp, siteid, soiltemp, sensor1, sensor2):
    print("insert date into database function")
    timestamp = datetime.now()
    print(database)
    conn = sqlite3.connect(database)
    curs = conn.cursor()
    #print("SENSOR1=:")
    #print(sensor1)
    curs.execute("INSERT INTO tbl_data values((?),(?),(?),(?),(?),(?),(?),(?),(?),(?))",
                 (timestamp, temp, siteid, soiltemp, sensor1, sensor2, None, None, None, None))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
