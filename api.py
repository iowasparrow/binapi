#!flask/bin/python3
from flask import Flask, jsonify, render_template
from flask import make_response
from flask import abort
from flask import request
from flask import flash, redirect
import sqlite3
from subprocess import check_output
from datetime import datetime, timezone, timedelta
import re
import json
from pytz import timezone

database = '/var/www/html/binweb/bin_temperature/sensorsData.db'
#database = 'customer.db'
app = Flask(__name__)

tasks = []
dict = {}
test = {}


def get_all(siteid, start_date='1900-01-01', end_date='2050-01-01'):  # this is for the chart
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    print("start date in getall function: " + start_date)
    print("end date in getall function: " + end_date)
    print("SiteID in getall function: " + siteid)
    sql = "SELECT * FROM pihq WHERE timestamp >= ? AND timestamp <= ? and siteid = ? ORDER BY timestamp DESC"
    # we have to change site id to a list because when we get to double digits it thinks we are passing in a list of characters.
    #curs.execute(sql, [siteid])
    curs.execute(sql, [start_date, end_date, siteid])
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
    #sql = "SELECT * FROM pidata WHERE timestamp >= ? AND timestamp <= ? ORDER BY timestamp DESC"
    sql = "SELECT * FROM pidata ORDER BY timestamp DESC LIMIT 1"
    #curs.execute(sql, [start_date, end_date])
    curs.execute(sql)
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
            "SELECT * FROM pidata WHERE timestamp BETWEEN datetime('now', '-8 days') AND datetime('now', '-6 days') LIMIT 1;"):
        temp_week_ago = row[x]
        if temp_week_ago == "":
            temp_week_ago = 0
    conn.close()
    if temp_week_ago is None:
        temp_week_ago = 0
    if current_temp == None:
        current_temp = 0
    print("temp week ago: " + str(temp_week_ago))
    print("current temp " + str(current_temp))

    temp_difference = current_temp - temp_week_ago
    if temp_difference >= 3 and current_temp > 32:
        # print("DANGER RAPID RISE DETECTED 3 degrees in one week at 32.")
        #set_temp_alarm('true')
        temp_difference_rounded = round(temp_difference, 2)
        return temp_difference_rounded, temp_week_ago
    else:
        temp_difference_rounded = round(temp_difference, 2)
        return temp_difference_rounded, temp_week_ago

def get_current_data(siteid):  # get current values for display on web page
    
    print("site id in get current data " + siteid)
    
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    current_time = []
    current_temp = []
    current_soiltemp = []
    sensor1 = []
    sensor2 = []
    sql = "SELECT * FROM pihq WHERE siteid = ? ORDER BY timestamp DESC LIMIT 1" 
    for row in curs.execute(sql, siteid):
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
    current_time, current_temp, temp_difference, current_soiltemp, temp_week_ago, current_sensor1, current_sensor2, temp_week_ago1, temp_week_ago2, temp_difference1, temp_difference2 = get_current_data(siteid)
   
    shortdate = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M')
    
    ipaddr = getipaddress()

    return render_template('index.html', ipaddr=ipaddr, siteid=siteid, temp_week_ago=temp_week_ago, temp_difference=temp_difference, temp_difference1=temp_difference1, temp_difference2=temp_difference2, temps=airtemps, dates=dates, soiltemps=soiltemps, current_soiltemp=current_soiltemp ,sensor1=sensor1,sensor2=sensor2, current_sensor1=current_sensor1, current_sensor2=current_sensor2, shortdate=shortdate, current_temp=current_temp, temp_week_ago1=temp_week_ago1, temp_week_ago2=temp_week_ago2)


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

def getipaddress():
    ipaddr_bytes = check_output(['hostname', '-I'])
    ipaddr = ipaddr_bytes.decode("utf-8")
    ipaddr = re.sub(r"[\n\t\s]*", "", ipaddr)
    return ipaddr

@app.route('/dashboard')
def dashboard():
    if not request.cookies.get('siteid'):
        res = make_response(redirect('/binapi/login'))
        return res
    mycookie = request.cookies.get('siteid')
    siteid = mycookie
    #  print(dict)
    # return jsonify({'data': dict})
    avg = get_average()
    
    ipaddr = getipaddress()

    current_time, current_temp, temp_difference, temp_week_ago, current_soiltemp, current_sensor1, current_sensor2, temp_week_ago1, temp_week_ago2, temp_difference1, temp_difference2 = get_current_data(siteid)
    
    #print("current soiltemp- " + str(current_soiltemp))

    dates, airtemps, soiltemps, cputemps, sensor1, sensor2 = get_all(siteid)

    if siteid == 1:
        return render_template('dashboard.html', ipaddr=ipaddr, siteid=siteid, avg=avg, temp_week_ago=temp_week_ago, mycookie=mycookie, temp_difference=temp_difference,temps=airtemps, dates=dates, soiltemps=soiltemps ,sensor1=sensor1, current_sensor1=current_sensor1, current_sensor2=current_sensor2, sensor2=sensor2, current_time=current_time, current_temp=current_temp, current_soiltemp=current_soiltemp, temp_week_ago1=temp_week_ago1, temp_week_ago2=temp_week_ago2 )
    else:
        return render_template('dashboard_customer.html', ipaddr=ipaddr, siteid=siteid, avg=avg, temp_week_ago=temp_week_ago, mycookie=mycookie, temp_difference=temp_difference,temps=airtemps, dates=dates, soiltemps=soiltemps ,sensor1=sensor1, current_sensor1=current_sensor1, current_sensor2=current_sensor2, sensor2=sensor2, current_time=current_time, current_temp=current_temp, current_soiltemp=current_soiltemp, temp_week_ago1=temp_week_ago1, temp_week_ago2=temp_week_ago2 )

@app.route('/logout')
def delete_cookie():
    res = make_response("<a href=""http://bintemp.com/binapi/login"">Log In</a>")
    res.set_cookie('siteid', max_age=0)
    return res


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/api/insert', methods=['POST'])
def get_json_data():
    if not request.json or not 'sensor1' in request.json:
        abort(400)
    data = {
        'airtemp' : request.json['airtemp'],
        'siteid'  : request.json['siteid'],
        'soiltemp': request.json['soiltemp'],
        'sensor1' : request.json['sensor1'],
        'sensor2' : request.json['sensor2'],
        'picpu'   : request.json['picpu']
    }
    
    airtemp = request.json.get('airtemp')
    siteid = request.json.get('siteid')
    soiltemp = request.json.get('soiltemp')
    sensor1 = request.json.get('sensor1')
    sensor2 = request.json.get('sensor2')
    picpu = request.json.get('picpu')
    log_to_database(airtemp, siteid, soiltemp, sensor1, sensor2, picpu)
    print("api data being logged")
    #print(data)
    return jsonify({'data': data}), 201


def log_to_database(airtemp, siteid, soiltemp, sensor1,sensor2, picpu):
    fmt = "%Y-%m-%d %H:%M:%S"
    now_utc = datetime.now(timezone('UTC'))
    now_central = now_utc.astimezone(timezone('US/Central'))
    formatted_date = now_central.strftime(fmt)
    #print("Formatted Date: " +formatted_date)
    conn = sqlite3.connect(database)
    curs = conn.cursor()
    curs.execute("INSERT INTO pihq VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (formatted_date, None, airtemp, siteid, soiltemp, None, picpu, sensor1, sensor2, None, None, None ,None ))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
