import plyer
import time
from datetime import datetime

import mysql.connector
from mysql.connector import Error

connection = ''
cursor = ''

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='iot',
                                         user='root',
                                         password='')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        curs = connection.cursor(buffered=True)

        while True:
            connection = mysql.connector.connect(host='localhost',
                                                 database='iot',
                                                 user='root',
                                                 password='')
            curs = connection.cursor(buffered=True)
            curs.execute('Select sum(m_move) from sensor_data where d_date=current_date and time_to_sec(timediff(current_time, t_time)) < 20')
            try:
                cnt = int(curs.fetchone()[0])
                if cnt > 3:
                    print(cnt, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    plyer.notification.notify(title='ALERT !!', message="Movement detected at"+datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            except TypeError as e:
                print('No movement')
            except Error as e:
                print("Error :", e)
            time.sleep(3)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    try:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    except Error as e:
        print("Failed to close : ",e)
