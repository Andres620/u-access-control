import os
from tkinter import *
import tkinter as Tk
import imutils
from PIL import Image, ImageTk
import cv2
import threading

from process.assets.image_paths import ImagePaths
from process.database.config import DataBasePaths
from process.face_processing.facial_signup import FacialSignUp
from process.face_processing.facial_login import FacialLogIn
from process.com_interface.serial_com import SerialCommunication


class CustomFrame(Tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill=Tk.BOTH, expand=True)


class GraphicalUserInterface:
    def __init__(self, root):
        # config root
        self.main_window = root
        self.main_window.title('Uni Access Control System')
        self.main_window.geometry('1280x720')
        self.frame = CustomFrame(self.main_window)

        # config stream
        # self.stream_url = "http://192.168.1.200:4747/video"
        self.signup_video = None
        self.login_video = None
        # self.cap = cv2.VideoCapture(self.stream_url)
        # self.cap.set(3, 1280)
        # self.cap.set(4, 720)

        # windows
        self.signup_window = None
        self.face_signup_window = None
        self.face_login_window = None

        # paths
        self.images = ImagePaths()
        self.database = DataBasePaths()

        # data
        self.input_name: str = ''
        self.input_user_code: str = ''
        self.name: str = ''
        self.user_code: str = ''
        self.user_list = []
        self.user_codes = []
        self.data = []

        # process
        self.face_sign_up = FacialSignUp()
        self.face_login = FacialLogIn()
        self.com = SerialCommunication()
        
        # Serial Communication
        self.serial_thread = threading.Thread(target=self.listen_serial)
        self.serial_thread.start()

        # Boolean to control login
        self.login_active = False

        # Boolean to control signup
        self.signup_active = False   

        # Boolean to control serial access        
        self.access_granted = False 

        self.init()
    
    def listen_serial(self):
        while True:
            if self.com.com.in_waiting > 0:
                line = self.com.com.readline().decode('utf-8').rstrip()
                if line == "Movimiento detectado" and not self.login_active and not self.signup_active:
                    self.gui_login()
                    self.login_active = True

    def close_signup(self):
        self.face_signup_window.destroy()
        self.signup_video.destroy()
        self.face_sign_up.__init__()
        self.signup_active = False
        self.close_camera()

    def facial_sign_up(self):
        if self.cap:
            ret, frame_bgr = self.cap.read()

            if ret:
                frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                # process
                frame, save_image, info = self.face_sign_up.process(frame, self.user_code)

                # config video
                frame = imutils.resize(frame, width=1280)
                im = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=im)

                # show video
                self.signup_video.configure(image=img)
                self.signup_video.image = img
                self.signup_video.after(10, self.facial_sign_up)

                # close
                if save_image:
                    self.signup_video.after(3000, self.close_signup)

        else:
            self.cap.release()
        
    def data_sign_up(self):
        # extract data
        self.name, self.user_code = self.input_name.get(), self.input_user_code.get()
        # Check data
        if len(self.name) == 0 or len(self.user_code) == 0:
            print('Form incomplete')
        else:
            # Check user
            self.user_list = os.listdir(self.database.check_users)
            for u_list in self.user_list:
                user = u_list
                user = user.split('.')
                self.user_codes.append(user[0])
            if self.user_code in self.user_codes:
                print('User already registered')
            else:
                # save data
                self.data.append(self.name)
                self.data.append(self.user_code)

                file = open(f"{self.database.users}/{self.user_code}.txt", 'w')
                file.writelines(self.name + ',')
                file.writelines(self.user_code + ',')
                file.close()

                # clean
                self.input_name.delete(0, END)
                self.input_user_code.delete(0, END)

                # new window
                self.face_signup_window = Toplevel(self.main_window)
                self.face_signup_window.title('face capture')
                self.face_signup_window.geometry("1280x720")

                self.signup_video = Label(self.face_signup_window)
                self.signup_video.place(x=0, y=0)
                self.signup_window.destroy()
                self.open_camera()
                self.facial_sign_up()
                # Vincula el evento de cierre de la ventana a la función on_signup_close
                self.face_signup_window.protocol("WM_DELETE_WINDOW", self.on_face_signup_close)
    
    def on_face_signup_close(self):
        self.signup_active = False
        self.close_camera()
        self.face_signup_window.destroy()


    def gui_signup(self):
        self.signup_window = Toplevel(self.main_window)
        self.signup_window.title("Sign up")
        self.signup_window.geometry("1280x720")

        # background
        background_signup_img = PhotoImage(file=self.images.gui_signup_img)
        background_signup = Label(self.signup_window, image=background_signup_img, text='back')
        background_signup.image = background_signup_img
        background_signup.place(x=0, y=0, relwidth=1, relheight=1)

        # input data
        self.input_name = Entry(self.signup_window)
        self.input_name.place(x=585, y=320)
        self.input_user_code = Entry(self.signup_window)
        self.input_user_code.place(x=585, y=475)

        # button
        face_register_button_img = PhotoImage(file=self.images.face_capture_img)
        face_register_button = Button(self.signup_window, text='register', image=face_register_button_img,
                                      height="40", width="200", command=self.data_sign_up)
        face_register_button.image = face_register_button_img
        face_register_button.place(x=1005, y=565)

        self.signup_active = True
        # Vincula el evento de cierre de la ventana a la función on_signup_close
        self.signup_window.protocol("WM_DELETE_WINDOW", self.on_signup_close)


    def on_signup_close(self):
        self.signup_active = False
        self.close_camera()
        self.signup_window.destroy()
    

    def close_login(self):
        self.face_login.__init__()
        self.face_login_window.destroy()
        self.login_video.destroy()
        self.com.sending_data('C')
        print('¡Close Login! - C')
        # Restablecer la bandera después de que se complete el inicio de sesión
        self.login_active = False
        self.access_granted = False
        self.close_camera()

    def facial_login(self):
        if self.cap:
            ret, frame_bgr = self.cap.read()

            if ret:
                frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                # process
                frame, user_access, info = self.face_login.process(frame)

                # config video
                frame = imutils.resize(frame, width=1280)
                im = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=im)

                # show video
                self.login_video.configure(image=img)
                self.login_video.image = img
                self.login_video.after(10, self.facial_login)

                # close
                if user_access and not self.access_granted:
                    # serial communication
                    self.com.sending_data('A')
                    print('¡Access granted! - A')
                    self.access_granted = True
                    self.login_video.after(3000, self.close_login)

                elif user_access is False:
                    self.login_video.after(3000, self.close_login)

        else:
            self.cap.release()

    def gui_login(self):
        # new window
        self.face_login_window = Toplevel(self.main_window)
        self.face_login_window.title('Login')
        self.face_login_window.geometry("1280x720")

        self.login_video = Label(self.face_login_window)
        self.login_video.place(x=0, y=0)
        self.open_camera()
        self.facial_login()
        # Vincula el evento de cierre de la ventana a la función on_login_close
        self.face_login_window.protocol("WM_DELETE_WINDOW", self.on_login_close)
    
    def on_login_close(self):
        self.login_active = False
        self.close_camera()
        self.face_login_window.destroy()
    
    def open_camera(self):
        self.stream_url = "http://192.168.1.200:4747/video"
        self.cap = cv2.VideoCapture(self.stream_url)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        
    def close_camera(self):
        if self.cap:
            self.cap.release()

    def init(self):
        # background
        background_img = PhotoImage(file=self.images.init_img)
        background = Label(self.frame, image=background_img, text='back')
        background.image = background_img
        background.place(x=0, y=0, relwidth=1, relheight=1)

        # buttons
        # login_button_img = PhotoImage(file=self.images.login_img)
        # login_button = Button(self.frame, text='login', image=login_button_img, height="40", width="200",
        #                       command=self.gui_login)
        # login_button.image = login_button_img
        # login_button.place(x=980, y=325)

        signup_button_img = PhotoImage(file=self.images.signup_img)
        signup_button = Button(self.frame, text='signup', image=signup_button_img, height="40", width="200",
                               command=self.gui_signup)
        signup_button.image = signup_button_img
        signup_button.place(x=988, y=578)
