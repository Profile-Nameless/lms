import customtkinter as ctk
import mysql.connector
from tkinter import messagebox, TclError
from ctypes import windll 
from admin_dashboard import open_admin_dashboard
import re
from signup import signup_widgets
from dbconnection import create_db_connection
import os
from userdashboard import *
global invalidpopup

def setup_window():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    return root

def validate_login(root,username_or_email_entry, password_entry, remember_me_var, cursor):
    global invalidpopup ,frame
    username_or_email = username_or_email_entry.get()
    user_password = password_entry.get()

    cursor.execute("SELECT user_role,first_name  FROM users WHERE (user_name = %s or email = %s) AND password = %s", (username_or_email,username_or_email, user_password))
    
    result = cursor.fetchone()
    if result:
        name=result['first_name']
        id=['user_id']
        if remember_me_var.get():
            with open("login_info.txt", "w") as file:
                file.write(f"{username_or_email},{user_password}")
        else:
            if os.path.exists("login_info.txt"):
                os.remove("login_info.txt")
        if result['user_role'] == 'admin':
            for widget in root.winfo_children():
                widget.destroy()
            try:
                    invalidpopup.configure(text="")
            except TclError:
                    pass
            frame.destroy()
            
            root.destroy()
            open_admin_dashboard(name)
        else:
            for widget in root.winfo_children():
                widget.destroy()
            try:
                    invalidpopup.configure(text="")
            except TclError:
                    pass
            frame.destroy()
            
            root.destroy()
            
            open_user_dashboard(name,id)
            
    else:
        invalidpopup.configure(text="Incorrect Username/Email or Password",text_color="#cc0000")
        invalidpopup.pack(anchor="w",padx=(25,0),pady=(10,0))
        username_or_email_entry.delete(0,"end")
        password_entry.delete(0,'end')





def create_widgets(root,cursor):
    global frame,invalidpopup,side_img_data
    side_img_data=Image.open(r"E:\coding-programs\project\photos\img_gen_1019708_v5KBjL_2 (1).png")

    side_img = ctk.CTkImage(dark_image=side_img_data, light_image=side_img_data, size=(300, 480))
    frame2=ctk.CTkFrame(master=root,width=300,height=480)
    frame2.pack_propagate(0)
    frame2.place(anchor='nw')
    frame = ctk.CTkFrame(master=root, width=300, height=480, fg_color="#ffffff")
    frame.pack_propagate(0)
    frame.place(relx=1.0, rely=0.0, anchor='ne')
    name=ctk.CTkLabel(frame, text="Welcome to StudySpark", font=("ROBOTO",24,"bold"),text_color="#123C69")
    name.pack(anchor="w", pady=(50, 0), padx=(25, 0))
    ctk.CTkLabel(master=frame2, text="", image=side_img).pack(expand=True, side="right")
    ctk.CTkLabel(master=frame, text="Sign in to your account", text_color="#7E7E7E", anchor="w", justify="left", font=("Arial Bold", 12)).pack(anchor="w", padx=(25, 0))
   

    invalidpopup = ctk.CTkLabel(frame,text="",text_color="#cc0000",anchor="w",justify="left",font=("Arial",12))
    invalidpopup.pack(anchor="w",padx=(25,0),pady=(1,0))
    username_or_email_label = ctk.CTkLabel(frame, text="Username or Email:",text_color="#000080", anchor="w", justify="left", font=("Arial Bold", 14), compound="left")
    username_or_email_label.pack(anchor="w", pady=(5, 0), padx=(25, 0))
    
    username_or_email_entry = ctk.CTkEntry(master=frame,fg_color="#EEEEEE",border_color="#000080",border_width=1,placeholder_text="Enter Username",text_color="#000000",width=255)
    username_or_email_entry.pack(anchor="w", padx=(25, 0))
    
    
    password_label = ctk.CTkLabel(frame, text="Password:", text_color="#000080",anchor="w", justify="left", font=("Arial Bold", 14), compound="left")
    password_label.pack(anchor="w", pady=(21, 0), padx=(25, 0))

    password_entry = ctk.CTkEntry(frame,placeholder_text="Enter Password",  fg_color="#EEEEEE", border_color="#000080", border_width=1, text_color="#000000", show="*",width=255)
    password_entry.pack(anchor="w", padx=(25, 0))

    remember_me_var = ctk.IntVar()
    remember_me_checkbutton = ctk.CTkCheckBox(frame, text="Remember Me", variable=remember_me_var,border_color="#000080",bg_color="transparent")
    remember_me_checkbutton.pack(anchor="w",pady=(26,0),padx=(25,0))

    
    login_button = ctk.CTkButton(frame, text="Login",width=255 ,command=lambda: validate_login(root,username_or_email_entry, password_entry, remember_me_var, cursor),fg_color="#BAB2B5")
    login_button.pack(anchor="w",pady=(40, 0), padx=(25, 0),)

    
 
    
    sign_up_button = ctk.CTkButton(frame, text="Sign Up",width=255 ,command=lambda: signup_widgets(root,frame))
    sign_up_button.pack(anchor="w",pady=(20, 0), padx=(25, 0), )

    return username_or_email_entry, password_entry, remember_me_var

def load_credentials(username_or_email_entry, password_entry, remember_me_var):
    try:
        with open("login_info.txt", "r") as file:
            username, password = file.read().split(",")
            username_or_email_entry.insert(0, username)
            password_entry.insert(0, password)
            remember_me_var.set(1)
    except FileNotFoundError:
        pass

def center_window(root, app_width, app_height):
    screen_width = root.winfo_screenwidth()
    screen_height=root.winfo_screenheight()
    app_center_coordinate_x=(screen_width / 3) - (app_width/3)
    app_center_coordinate_y=(screen_height/ 3) - (app_height/3)
    root.geometry(f"{app_width}x{app_height}+{int(app_center_coordinate_x)}+{int(app_center_coordinate_y)}")

def main():
    app_width=600
    app_height=480
    root = setup_window()
    conn, cursor = create_db_connection()
    username_or_email_entry, password_entry, remember_me_var = create_widgets(root,cursor)
    load_credentials(username_or_email_entry, password_entry, remember_me_var)
    center_window(root, app_width, app_height)
    root.resizable(0,0)
    root.mainloop()
    
if __name__ == "__main__":
    main()
