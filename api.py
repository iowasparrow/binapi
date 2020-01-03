#!flask/bin/python3
from flask import Flask, jsonify, render_template
from flask import make_response
from flask import abort
from flask import request
from flask import flash, redirect
import sqlite3
from datetime import datetime, timezone, timedelta

database = '/var/www/html/binweb/binapi/customer.db'
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


@app.route('/api/v1.0/tasks', methods=['GET'])
def get_all(siteid):  # This returns all entries in the database into a dict and then converts to json.
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    sql = "SELECT * FROM tbl_data WHERE siteid  = ? ORDER BY timestamp DESC"
    # we have to change site id to a list because when we get to double digits it thinks we are passing in a list of characters.
    curs.execute(sql, [siteid])
    
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

        if row[5] == None or row[5] == 0 or row[5] == 185:
            #convert None to null so the chart is happy
            sensor2.append('null')
        else:
            sensor2.append(row[5])

        # sensor3append(row[6])
        # sensor4.append(row[7])
        # sensor5.append(row[8])
        # sensor6.append(row[9])

        dict[row[0]] = {'date': row[0], 'temp': row[1], 'soiltemps':row[3] ,'sensor1': row[4], 'sensor2': row[5]}

    conn.close()
    #print(dict)
    return dates, temps, soiltemps, sensor1, sensor2
    #return jsonify({'data': dict})


def get_average():
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    sql = "select avg(sensor1) from(select sensor1 from tbl_data WHERE sensor1 <> 'None' AND sensor1 <> '0' Order By timestamp desc limit 7)"
    # we have to change site id in the execute function to a list because when we get to double digits it thinks we are passing in a list of characters.
    curs.execute(sql)
    data = curs.fetchall()
    x = data[0]
    y= round(x[0],2)
    return y


def check_rapid_rise(current_temp):
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    temp_week_ago = 0
    for row in curs.execute(
            "SELECT * FROM tbl_data WHERE timestamp BETWEEN datetime('now', '-8 days') AND datetime('now', '-6 days') LIMIT 1;"):
        temp_week_ago = row[1]
    conn.close()
    temp_difference = current_temp - temp_week_ago
    print('temp difference=', temp_difference)
    if temp_difference >= 3 and current_temp > 32:
        print("DANGER RAPID RISE DETECTED 3 degrees in one week at 32.")
        # set_temp_alarm('true')
        formatted_temp_difference = round(temp_difference, 1)
        return formatted_temp_difference, temp_week_ago
    else:
        formatted_temp_difference = round(temp_difference, 1)
        return formatted_temp_difference, temp_week_ago


def get_current_data():  # get current values for display on dashboard
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    current_time = []
    current_temp = []
    current_soiltemp = []
    current_sensor1 = []
    current_sensor2 = []
    for row in curs.execute("SELECT * FROM tbl_data ORDER BY timestamp DESC LIMIT 1"):
        current_time = str(row[0])
        current_temp = row[1]
        current_soiltemp = row[3]
        current_sensor1 = row[4]
        current_sensor2 = row[5]
    conn.close()
    temp_difference, temp_week_ago = check_rapid_rise(current_temp)
    print("Current Sensor 2= " + str(current_sensor2))
    return current_time, current_temp, temp_difference, temp_week_ago, current_soiltemp, current_sensor1, current_sensor2


@app.route('/linechart')
def linechart():
    if not request.cookies.get('siteid'):
        res = make_response(redirect('/binapi/login'))
        return res
    mycookie = request.cookies.get('siteid')
    siteid=mycookie   
    #  print(dict)
    # return jsonify({'data': dict})
    current_time, current_temp, temp_difference, current_soiltemp, temp_week_ago, current_sensor1, current_sensor2 = get_current_data()
    dates, temps, soiltemps, sensor1, sensor2 = get_all(siteid)
    return render_template('index.html', siteid=siteid, temp_week_ago=temp_week_ago, temp_difference=temp_difference,temps=temps, dates=dates, soiltemps=soiltemps, current_soiltemp=current_soiltemp ,sensor1=sensor1,sensor2=sensor2, current_time=current_time, current_temp=current_temp)


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
    avg = get_average()
    current_time, current_temp, temp_difference, temp_week_ago, current_soiltemp, current_sensor1, current_sensor2 = get_current_data()
    #check_rapid_rise(current_temp)
    dates, temps, soiltemps, sensor1, sensor2 = get_all(siteid)
    return render_template('dashboard.html', siteid=siteid, avg=avg, temp_week_ago=temp_week_ago, mycookie=mycookie, temp_difference=temp_difference,temps=temps, dates=dates, soiltemps=soiltemps ,sensor1=sensor1, current_sensor1=current_sensor1, current_sensor2=current_sensor2, sensor2=sensor2, current_time=current_time, current_temp=current_temp, current_soiltemp=current_soiltemp)


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
    print(database)
    conn = sqlite3.connect(database)
    curs = conn.cursor()
    timestamp = datetime.now()
    # print(timestamp)
    #print("SENSOR1=:")
    #print(sensor1)
    curs.execute("INSERT INTO tbl_data values((?),(?),(?),(?),(?),(?),(?),(?),(?),(?))",
                 (timestamp, temp, siteid, soiltemp, sensor1, sensor2, None, None, None, None))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
