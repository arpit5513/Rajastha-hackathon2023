from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen,ScreenManager, WipeTransition
from plyer import filechooser,storagepath
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDFlatButton
from kivy.uix.popup import Popup
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivy.uix.spinner import Spinner
import csv
import cv2
import os
import cv2
import face_recognition
import numpy as np
from datetime import datetime
from datetime import date
import pyttsx3
import mysql.connector
from mysql.connector import Error
import pandas as pd

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
#print(voices[1].id)
engine.setProperty('voice', voices[1].id)

class Screen_Manager(ScreenManager):
    pass
class Screen_Function(Screen):
    pass
class Screen_Admin_Login(Screen):
    pass
class Screen_Admin_Panel(Screen):
    pass
class Screen_Faculty_Login(Screen):
    pass
class Screen_Faculty_Panel(Screen):
    pass
class Screen_Add_Faculty(Screen):
    pass
class Screen_Update_Faculty(Screen):
    pass
class Screen_Remove_Faculty(Screen):
    pass
class Screen_Faculty_Record(Screen):
    pass
class Screen_Attendence_Record(Screen):
    pass
class Screen_Camera_Panel(Screen):
    pass
class Screen_Master_Panel(Screen):
    pass

class DatabaseClass:
    def create_server_connection(self,host_name,user_name,user_password):
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

    def create_database(self,connection, query):
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            print("Database created sucessfully")
        except Error as err:
            print("Error: " + str(err))

    def create_db_connection(self,host_name, user_name, user_password, db_name):
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

    def execute_query(self,connection, qurey):
        cursor = connection.cursor()
        try:
            cursor.execute(qurey)
            connection.commit()
            print("Query was sucessfull")
        except Error as e:
            print("Error: " + str(e))    

    def read_query(self,connection, query):
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
Database = DatabaseClass()
Database.create_server_connection("127.0.0.1",'root',"pratham@123")
connection = Database.create_db_connection("127.0.0.1","root",pw,db)

q1 = """
select Faculty_Name from Faculty_Record;
"""
results = Database.read_query(connection, q1)
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
results = Database.read_query(connection, q2)
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
teachers_out = Faculty_Name.copy()
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
                        now = datetime.now()
                        current_time = now.strftime("%H:%M")
                        print(current_time)
                        name = name.replace("\n","")
                        data_orders =  """
                        insert into Attendence values
                        ('{}','{}','{}','')
                        """
                        data_orders = data_orders.format(current_date,name,current_time)
                        Database.execute_query(connection, data_orders)
                        self.speak(name + "Is added")
                        return
                    elif name in teachers_out:
                        now = datetime.now()
                        current_time = str(now.strftime("%H"))
                        if current_time >= '12':
                            teachers_out.remove(name)
                            print(teachers_out)
                            now = datetime.now()
                            current_time = now.strftime("%H:%M")
                            print(current_time)
                            name = name.replace("\n","")
                            data_orders =  """
                            update Attendence
                            set Time_Out = '{}'        
                            where Faculty_Name = '{}', Date = {}
                            """
                            data_orders = data_orders.format(current_time, name,current_date)
                            Database.execute_query(connection, data_orders)
                            self.speak(name + "Is added")
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
    
    def speak(self,audio):
        engine.say(audio)
        engine.runAndWait()
        return

class mainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Purple'
        q1 = """
        select * from Master_Department;
        """
        connection = Database.create_db_connection("127.0.0.1","root",pw,db)
        results = Database.read_query(connection, q1)
        departments = []
        for result in results:
            result = str(result).replace("(\'","")
            result = str(result).replace("\',)","")
            
            departments.append(str(result))
        print(departments)
        self.root.get_screen("Add_Faculty").ids.faculty_department.values = departments
        self.root.get_screen("Update_Faculty").ids.faculty_department.values = departments
        return 
    
    def Admin_Login(self):

        q1 = """
        select * from Admin_Password;
        """
        connection = Database.create_db_connection("127.0.0.1","root",pw,db)
        results = Database.read_query(connection, q1)
        Admin_list = []
        for result in results:
            Admin_list.append(result)
        print(Admin_list)
        print(type(Admin_list))
        user_name = self.root.get_screen('Admin_Login').ids.user_name.text 
        user_password = self.root.get_screen('Admin_Login').ids.user_password.text 

        user_data = [(user_name,user_password)]
        print(user_data)

        print(user_data)
        if user_data[0] in Admin_list:
            print("Access granted")
            self.root.current = 'Admin_Panel'
            self.root.get_screen('Admin_Login').ids.user_name.text = ''
            self.root.get_screen('Admin_Login').ids.user_password.text = ''

        else:
            self.root.get_screen('Admin_Login').ids.label.text = "Access Denied"
            self.root.get_screen('Admin_Login').ids.user_name.text = ''
            self.root.get_screen('Admin_Login').ids.user_password.text = ''

    def File_Chooser(self):
        filechooser.open_file(on_selection  = self.Add_Faculty)
    
    def File_Update_Chooser(self):
        filechooser.open_file(on_selection = self.Update_Faculty)

    def Add_Faculty(self,selection):
        Faculty_Name = self.root.get_screen("Add_Faculty").ids.faculty_name.text
        Faculty_DOB = self.root.get_screen("Add_Faculty").ids.faculty_dob.text
        Faculty_Department = self.root.get_screen("Add_Faculty").ids.faculty_department.text
        Faculty_Id = self.root.get_screen("Add_Faculty").ids.faculty_id.text
        Faculty_Password = self.root.get_screen("Add_Faculty").ids.faculty_password.text
        Faculty_Image = selection[0]
        Faculty_Image = Faculty_Image.replace("\\","/")
        print(Faculty_Image)

        Data_Entry =  """
        insert into Faculty_Record values
        ('{}','{}','{}','{}','{}','{}')
        """
        Data_Entry = Data_Entry.format(Faculty_Name,
                                       Faculty_DOB,
                                       Faculty_Department,
                                       Faculty_Id,
                                       Faculty_Password,
                                       Faculty_Image)
        print(Data_Entry)

        connection = Database.create_db_connection("127.0.0.1",'root', pw, db) 
        Database.execute_query(connection, Data_Entry)

        self.root.get_screen("Add_Faculty").ids.label.text = "Entry Added"
        self.root.get_screen("Add_Faculty").ids.faculty_name.text = ''
        self.root.get_screen("Add_Faculty").ids.faculty_dob.text = ''
        self.root.get_screen("Add_Faculty").ids.faculty_department.text = 'Department'
        self.root.get_screen("Add_Faculty").ids.faculty_id.text = ''
        self.root.get_screen("Add_Faculty").ids.faculty_password.text = ''
    
    def Update_Faculty(self,selection):
        Faculty_Name = self.root.get_screen("Update_Faculty").ids.faculty_name.text
        Faculty_DOB = self.root.get_screen("Update_Faculty").ids.faculty_dob.text
        Faculty_Department = self.root.get_screen("Update_Faculty").ids.faculty_department.text
        Faculty_Id = self.root.get_screen("Update_Faculty").ids.faculty_id.text
        Faculty_Password = self.root.get_screen("Update_Faculty").ids.faculty_password.text
        Faculty_Image = selection[0]
        Faculty_Image = Faculty_Image.replace("\\","/")
        print(Faculty_Image)

        Update_Entry = """
        update Faculty_Record
        set Faculty_DOB = '{}',
        Faculty_Department = '{}',
        Faculty_Id = '{}',
        Faculty_Password = '{}',
        Faculty_Image = '{}'
        where Faculty_Name = '{}'
        """
        Update_Entry = Update_Entry.format(
            Faculty_DOB,
            Faculty_Department,
            Faculty_Id,
            Faculty_Password,
            Faculty_Image,
            Faculty_Name)
        print(Update_Entry)

        connection = Database.create_db_connection("127.0.0.1",'root', pw, db) 
        Database.execute_query(connection, Update_Entry)

        self.root.get_screen("Update_Faculty").ids.label.text = "Entry Added"
        self.root.get_screen("Update_Faculty").ids.faculty_name.text = ''
        self.root.get_screen("Update_Faculty").ids.faculty_dob.text = ''
        self.root.get_screen("Update_Faculty").ids.faculty_department.text = 'Department'
        self.root.get_screen("Update_Faculty").ids.faculty_id.text = ''
        self.root.get_screen("Update_Faculty").ids.faculty_password.text = ''
    
    
    def Remove_Faculty(self):
        Faculty_Name = self.root.get_screen("Remove_Faculty").ids.faculty_name.text
        Delete_Entry = """
        delete Faculty_Record
        where Faculty_Name = '{}'
        """
        Delete_Entry = Delete_Entry.format(Faculty_Name)
        print(Delete_Entry)
        connection = Database.create_db_connection("127.0.0.1",'root', pw, db) 
        Database.execute_query(connection, Delete_Entry)


    def add_Datatable(self):
        import pandas as pd
        q1 = """
        select * from Faculty_Record;
        """
        connection = Database.create_db_connection("127.0.0.1","root",pw,db)
        results = Database.read_query(connection, q1)
        self.removable_data = []
        self.data_tables = MDDataTable(
            use_pagination = True,
            size_hint = (0.95, 0.9),
            check = True,
            column_data =  [
                ("Faculty_Name",dp(40)),
                ("Faculty_DOB",dp(30)),
                ("Faculty_Department",dp(40)),
                ("Faculty_ID",dp(45)),
                ("Faculty_Password",dp(30)),
                ("Faculty_Image",dp(60))
            ],
            row_data = results
        )
        self.data_tables.bind(on_check_press = self.checked)
        self.root.get_screen("Faculty_Record").ids.table.add_widget(self.data_tables)

    def checked(self, instance_table, current_row):
        if current_row[0] not in self.removable_data:
            self.removable_data.append(current_row[0])
        else:
            self.removable_data.remove(current_row[0])
        print(self.removable_data)

    def show_alert_dialog(self):
        
        self.dialog = MDDialog(
            text =  "Sure to Delete the Data?",
            buttons = [
                MDFlatButton(
                    text = "CANCEL",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.close_dialog
                    ),
                MDRectangleFlatButton(
                    text = "CONFIRM",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.bin
                ),
            ],
        )
        self.dialog.open()

    def close_dialog(self, obj):
		# Close alert box
        self.dialog.dismiss()
	
    def bin(self,obj):
        self.close_dialog(obj)
        print(self.removable_data)
        for i in range (len(self.removable_data)):
            delete_order = """
            delete from Faculty_Record
            where Faculty_Name = "{}"
            """
            delete_order = delete_order.format(self.removable_data[i])
            print(delete_order)
            connection = Database.create_db_connection("127.0.0.1", 'root', pw,db)
            Database.execute_query(connection , delete_order)

    def Add_Attendence_Table(self):
        Date = str(self.root.get_screen("Attendence_Record").ids.Attendence_Date.text)
        Date = Date.replace("/","-")
        print(Date)
        q1 = """
        select * from Attendence where Date = '{}'; 
        """
        if Date == 'ALL' :
            q1 = """select * from Attendence ;"""
        else:
            q1 = q1.format(Date)

        connection = Database.create_db_connection("127.0.0.1","root",pw,db)
        results = Database.read_query(connection, q1)
        self.Attendence_removable_data = []
        self.Attendence_data_tables = MDDataTable(
            use_pagination = True,
            size_hint = (0.95, 0.9),
            check = True,
            column_data =  [
                ("Date",dp(40)),
                ("Faculty_Name",dp(60)),
                ("Faculty_Timing",dp(70)),
                ("Out_Timing",dp(70)),
            ],
            row_data = results
        )
        self.Attendence_data_tables.bind(on_check_press = self.Attendence_checked)
        self.root.get_screen("Attendence_Record").ids.table.add_widget(self.Attendence_data_tables)

    def Attendence_checked(self, instance_table, current_row):
        if current_row[0] not in self.Attendence_removable_data:
            self.Attendence_removable_data.append(current_row[0])
            self.Attendence_removable_data.append(current_row[1])
        else:
            self.Attendence_removable_data.remove(current_row[0])
            self.Attendence_removable_data.remove(current_row[1])
        print(self.Attendence_removable_data)

    def Attendence_show_alert_dialog(self):
        
        self.Attendence_dialog = MDDialog(
            text =  "Sure to Delete the Data?",
            buttons = [
                MDFlatButton(
                    text = "CANCEL",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.Attendence_close_dialog
                    ),
                MDRectangleFlatButton(
                    text = "CONFIRM",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.Attendence_bin
                ),
            ],
        )
        self.Attendence_dialog.open()

    def Attendence_close_dialog(self, obj):
		# Close alert box
        self.Attendence_dialog.dismiss()
	
    def Attendence_bin(self,obj):
        self.Attendence_close_dialog(obj)
        print(self.Attendence_removable_data)
        for i in range (0,len(self.Attendence_removable_data),2):
            delete_order = """
            delete from Attendence
            where Date = "{}" and Faculty_Name = "{}"
            """
            delete_order = delete_order.format(self.Attendence_removable_data[i],self.Attendence_removable_data[i+1])
            print(delete_order)
            connection = Database.create_db_connection("127.0.0.1", 'root', pw,db)
            Database.execute_query(connection , delete_order)

    def Camera_Start(self):
        self.capture = cv2.VideoCapture(0)
        self.my_camera = KivyCamera(capture=self.capture,
                                    fps=30,
                                    pos_hint={'center_x': .5,'center_x': .5},
                                    size_hint= (.8,.8))
        return self.root.get_screen("Camera_Panel").ids.camera.add_widget(self.my_camera)

    def Camera_Stop(self):
        self.capture.release()
    
    def Master_Department(self):
        q1 = """
        select * from Master_Department;
        """
        connection = Database.create_db_connection("127.0.0.1","root",pw,db)
        results = Database.read_query(connection, q1)
        self.removable_master_data = []
        print(results)
        self.master_tables = MDDataTable(
            use_pagination = True,
            size_hint = (0.3, 0.9),
            check = True,
            column_data =[("Faculty_Department",dp(40))],
            row_data = results
        )
        self.master_tables.bind(on_check_press = self.master_check)
        self.root.get_screen("Master_Panel").ids.table.add_widget(self.master_tables)
    
    def master_check(self, instance_table, current_row):
        if current_row[0] not in self.removable_master_data:
            self.removable_master_data.append(current_row[0])
        else:
            self.removable_master_data.remove(current_row[0])
        print(self.removable_master_data)

    
    def master_show_alert_dialog(self):
        
        self.master_dialog = MDDialog(
            text =  "Sure to Delete the Data?",
            buttons = [
                MDFlatButton(
                    text = "CANCEL",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.master_close_dialog
                    ),
                MDRectangleFlatButton(
                    text = "CONFIRM",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.master_bin
                ),
            ],
        )
        self.master_dialog.open()

    def master_close_dialog(self, obj):
		# Close alert box
        self.master_dialog.dismiss()
	
    def master_bin(self,obj):
        self.master_close_dialog(obj)
        print(len(self.removable_master_data))
        print(self.removable_master_data)
        for i in range (len(self.removable_master_data)):
            delete_order = """
            delete from Master_Department
            where Faculty_Department = "{}"
            """
            delete_order = delete_order.format(self.removable_master_data[i])
            print(delete_order)
            connection = Database.create_db_connection("127.0.0.1", 'root', pw,db)
            Database.execute_query(connection , delete_order)
    
    
    def master_addon(self):
        self.master_dialog_addon = MDDialog(
            text =  "Confirm Department List?",
            buttons = [
                MDFlatButton(
                    text = "CANCEL",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.master_close
                    ),
                MDRectangleFlatButton(
                    text = "CONFIRM",
                    text_color = self.theme_cls.primary_color,
                    on_release = self.master_Daddon
                ),
            ],
        )
        self.master_dialog_addon.open()

    
    def master_close(self, obj):
		# Close alert box
        self.master_dialog_addon.dismiss()
	
    def master_Daddon(self,obj):
        Department_Name = self.root.get_screen("Master_Panel").ids.department_name.text
        self.master_close(obj)
        Add_order = """
        insert into Master_Department values
        ('{}')
        """
        Add_order = Add_order.format(Department_Name)
        print(Add_order)
        connection = Database.create_db_connection("127.0.0.1", 'root', pw,db)
        Database.execute_query(connection , Add_order)
    
mainApp().run()