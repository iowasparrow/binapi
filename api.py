#!flask/bin/python3
from flask import Flask, jsonify, render_template
from flask import make_response
from flask import abort
from flask import request
import sqlite3
from datetime import datetime, timezone, timedelta

database = '/var/www/html/binweb/binapi/customer.db'
#database = 'customer.db'
app = Flask(__name__)

tasks = []
dict = {}
test = {}


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
        sensor1.append(row[4])
        sensor2.append(row[5])
        # sensor3append(row[6])
        # sensor4.append(row[7])
        # sensor5.append(row[8])
        # sensor6.append(row[9])

        dict[row[0]] = {'date': row[0], 'temp': row[1], 'soiltemps':row[3] ,'sensor1': row[4], 'sensor2': row[5]}

    conn.close()
    # print(dict)
    return dates, temps, soiltemps, sensor1, sensor2
    #return jsonify({'data': dict})



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


def get_current_data():  # get current values for display on web page
    conn = sqlite3.connect(database, check_same_thread=False)
    curs = conn.cursor()
    current_time = []
    current_temp = []
    current_soiltemp = []
    for row in curs.execute("SELECT * FROM tbl_data ORDER BY timestamp DESC LIMIT 1"):
        current_time = str(row[0])
        current_temp = row[1]
        current_soiltemp = row[3]
    conn.close()
    temp_difference, temp_week_ago = check_rapid_rise(current_temp)
    return current_time, current_temp, temp_difference, temp_week_ago, current_soiltemp


@app.route('/linechart')
def linechart():
    # here we want to get the value of user (i.e. ?user=some-value)
    siteid = request.args.get('siteid')
    #  print(dict)
    # return jsonify({'data': dict})
    current_time, current_temp, temp_difference, current_soiltemp, temp_week_ago = get_current_data()
    dates, temps, soiltemps, sensor1, sensor2 = get_all(siteid)
    return render_template('index.html', temp_week_ago=temp_week_ago, temp_difference=temp_difference,temps=temps, dates=dates, soiltemps=soiltemps, current_soiltemp=current_soiltemp ,sensor1=sensor1,sensor2=sensor2, current_time=current_time, current_temp=current_temp)


@app.route('/dashboard')
def dashboard():
    # here we want to get the value of user (i.e. ?user=some-value)
    siteid = request.args.get('siteid')
    #  print(dict)
    # return jsonify({'data': dict})
    current_time, current_temp, temp_difference, temp_week_ago, current_soiltemp = get_current_data()
    dates, temps, soiltemps, sensor1, sensor2 = get_all(siteid)
    return render_template('dashboard.html', temp_week_ago=temp_week_ago, temp_difference=temp_difference,temps=temps, dates=dates, soiltemps=soiltemps ,sensor1=sensor1,sensor2=sensor2, current_time=current_time, current_temp=current_temp, current_soiltemp=current_soiltemp)



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
    return jsonify({'task': task}), 201

    # return temp, siteid


def insert_data(temp, siteid, soiltemp, sensor1,sensor2):
    print("we made it to the function")
    print(database)
    conn = sqlite3.connect(database)
    curs = conn.cursor()
    timestamp = datetime.now()
    # print(timestamp)
    print("SENSOR1=:")
    print(sensor1)
    curs.execute("INSERT INTO tbl_data values((?),(?),(?),(?),(?),(?),(?),(?),(?),(?))",
                 (timestamp, temp, siteid, soiltemp, sensor1, sensor2, 0, 0, 0, 0))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
