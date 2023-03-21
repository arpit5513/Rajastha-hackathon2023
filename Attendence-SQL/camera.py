from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import face_recognition
import cv2
import numpy as np
import csv
import os
from datetime import datetime
from datetime import date
import mysql.connector
from mysql.connector import Error
import pandas as pd

video_capture = cv2.VideoCapture(0)

def create_server_connection(host_name,user_name,user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host= host_name,
            user  =user_name,
            passwd = user_password)
        print("MySql Database connection sucessfull")
    
    except Error as err:
        print(f'Error: '+ str(err))
    
    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created sucessfully")
    except Error as err:
        print("Error: " + str(err))

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print("Mysql database connection sucessfull")
    except Error as e:
        print("Error: " + str(e))    
    return connection

def execute_query(connection, qurey):
    cursor = connection.cursor()
    try:
        cursor.execute(qurey)
        connection.commit()
        print("Query was sucessfull")
    except Error as e:
        print("Error: " + str(e))    

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print("Error: " + str(e))    


pw = 'pratham@123'
db = 'Attendence_System'
connection = create_server_connection("127.0.0.1",'root',pw)

q1 = """
select Faculty_Name from Faculty_Record;
"""
connection = create_db_connection("127.0.0.1","root",pw,db)
results = read_query(connection, q1)
Faculty_Name = []
for result in results:
    result = str(result)
    result = result.replace("(\'","")
    result = result.replace("\',)","")
    Faculty_Name.append(result)
    print(result)
    print(type(result))

q2 = """
select Faculty_Image from Faculty_Record;
"""
connection = create_db_connection("127.0.0.1","root",pw,db)
results = read_query(connection, q2)
Faculty_Image = []
for result in results:
    result = str(result)
    result = result.replace("(\'","")
    result = result.replace("/","\\")
    result = result.replace("\',)","")
    Faculty_Image.append(result)
    print(result)
    
Teachers_encoding = []
for i in range (len(Faculty_Name)):
    face_image =  face_recognition.load_image_file(Faculty_Image[i])
    face_encode = face_recognition.face_encodings(face_image)[0]
    Teachers_encoding.append(face_encode)

print(Teachers_encoding)

teachers = Faculty_Name.copy()
print(teachers)

known_face_names =  Faculty_Name
known_face_encoding = Teachers_encoding


face_locations = []
face_encodings = []
face_names = []
s = True

now = datetime.now()
current_date = str(date.today())#now.strftime("%Y-%M-%D")
print(current_date)

connection = create_db_connection("127.0.0.1","root",pw,"Attendence_System")

class KivyCamera(Image):
    def __init__(self, capture, fps, **kwargs):
        super(KivyCamera, self).__init__(**kwargs)
        self.capture = capture
        Clock.schedule_interval(self.update, 1.0 / fps)

    def face_reco(self,rgb_small_frame):
        if s:
            face_locations= face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame,face_locations)
            face_names= []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encoding,face_encoding)
                name = ""
                face_distance = face_recognition.face_distance(known_face_encoding,face_encoding)
                best_match_index = np.argmin(face_distance)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                face_names.append(name)
                if name in known_face_names:
                    if name in teachers:
                        teachers.remove(name)
                        print(teachers)
                        current_time = now.strftime("%H:%M")
                        print(current_time)
                        name = name.replace("\n","")
                        data_orders =  """
                        insert into Attendence values
                        ('{}','{}','{}')
                        """
                        data_orders = data_orders.format(current_date,name,current_time)
                        execute_query(connection, data_orders)
                        return
        return
    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # convert it to texture
            self.face_reco(frame)
            buf1 = cv2.flip(frame, 0)
            buf = buf1.tobytes()
            image_texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.texture = image_texture

class CamApp(App):
    def build(self):
        self.capture = cv2.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture, fps=30)
        return self.my_camera

    def on_stop(self):
        #without this, app will not exit even if the window is closed
        self.capture.release()

if __name__ == '__main__':
    CamApp().run()