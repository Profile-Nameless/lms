import customtkinter as ctk
import mysql.connector
from tkinter import messagebox
from ctypes import windll 
from dbconnection import create_db_connection
import re


conn,cursor=create_db_connection()
def sign_up_details(root, username_entry, email_entry, password_entry,rname_entry):

    name=rname_entry.get()
    username = username_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    role="user""INSERT INTO users (user_name, user_email, user_password,user_role,user_rname"
    cursor.execute("INSERT INTO users (first_name, user_name,email, password,user_role) VALUES (%s, %s, %s,%s,%s)", (name, username,email, password,role))
    conn.commit()
    ctk.CTkLabel(root,text="Sign Up Successful, Account created successfully!").pack(side="right")
    open_user_dashboard()

def check_username(event,sign_up_button):
    global username_exists_label ,signup_username_entry
    
    username = signup_username_entry.get()
    cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
    result = cursor.fetchone()
    if result:
        username_exists_label.configure(text="Username already exists", text_color="red")
        sign_up_button.configure(state="disabled")
    else:
        username_exists_label.configure(text="")
        pass

def check_email(event,sign_up_button):
    global email_exists_label,signup_email_entry
    
    email = signup_email_entry.get()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        email_exists_label.configure(text="Email already exists", text_color="red")
        sign_up_button.configure(state="disabled")
    else:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if re.match(pattern, email):
            email_exists_label.configure(text="")
            pass
        else:
            email_exists_label.configure(text="Invalid Email,Please input a valid Email", text_color="red")
            sign_up_button.configure(state="disabled")





count_of_entries = 0

def check_password(event, sign_up_button):
    if password_entry.get() and check_password_entry.get() is not None:
        if password_entry.get() == check_password_entry.get():
            password_doesnt_match.configure(text="")
            entries = [rname_entry, signup_username_entry, signup_email_entry, password_entry]
            check_entries(event, entries, sign_up_button)  # Call check_entries here
        else:
            password_doesnt_match.configure(text="Password does not match", text_color="red")
            sign_up_button.configure(state="disabled")


def check_entries(event, entries, button):
    for entry in entries:
        if entry.get() == "" or entry.get() is None:
            button.configure(state="disabled")
            return
    if password_entry.get() == check_password_entry.get():
        button.configure(state="normal")
    else:
        button.configure(state="disabled")



def signup_widgets(root,frame):
    root=root
    global username_exists_label,signup_username_entry,signup_email_entry,email_exists_label,password_doesnt_match,password_entry,check_password_entry,rname_entry
    for widget in root.winfo_children():
                widget.destroy()
    frame.destroy()
    frame2 = ctk.CTkFrame(master=root, width=300, height=480, fg_color="#ffffff",border_color="#000080")
    frame2.pack_propagate(0)
    frame2.place(relx=0.5, rely=0.5,anchor='center')

    name_frame = ctk.CTkFrame(frame2, fg_color="#808080",corner_radius=0)
    name_frame.pack(fill='x', padx=(0, 0))


    name = ctk.CTkLabel(name_frame, text="Sign Up", font=("ROBOTO", 24, "bold"), text_color="#123C69")
    name.pack(anchor="w", padx=(12,0),pady=0)

    rname=ctk.CTkLabel(frame2, text="Name:",text_color="#000080", anchor="w", justify="left", font=("Arial Bold", 14), compound="left")
    rname.pack(anchor="w",pady=(2,0),padx=(25,0))

    rname_entry=ctk.CTkEntry(frame2,placeholder_text="Enter Name:",fg_color="#EEEEEE",border_color="#000080",border_width=1,text_color="#000000",width=255)
    rname_entry.pack(anchor="w",padx=(25,0))

    username_exists_label = ctk.CTkLabel(frame2, text="", text_color="red")
    username_exists_label.pack(anchor="w",pady=(2,0), padx=(25, 0))

    username = ctk.CTkLabel(frame2, text="Username:",text_color="#000080", anchor="w", justify="left", font=("Arial Bold", 14), compound="left")
    username.pack(anchor="w", pady=(2, 0), padx=(25, 0))
    signup_username_entry = ctk.CTkEntry(master=frame2,fg_color="#EEEEEE",border_color="#000080",border_width=1,placeholder_text="Enter Username",text_color="#000000",width=255)
    signup_username_entry.pack(anchor="w", padx=(25, 0))
     

    email_exists_label=ctk.CTkLabel(frame2,text="",text_color="red")
    email_exists_label.pack(anchor="w",pady=(2,0),padx=(25,0))
    email=ctk.CTkLabel(frame2,text="Email:",text_color="#000080",anchor="w",justify="left",font=("Arial Bold",14),compound="left")
    email.pack(anchor="w",pady=(2,0),padx=(25,0))

    signup_email_entry=ctk.CTkEntry(frame2,fg_color="#EEEEEE",placeholder_text="Enter Email:", border_color="#000080", border_width=1, text_color="#000000",width=255)
    signup_email_entry.pack(anchor="w",padx=(25,0))
    
    password_doesnt_match=ctk.CTkLabel(frame2,text="",text_color="red")
    password_doesnt_match.pack(anchor="w",pady=(2,0),padx=(25,0))


    password_label = ctk.CTkLabel(frame2, text="Password:", text_color="#000080",anchor="w", justify="left", font=("Arial Bold", 14), compound="left")
    password_label.pack(anchor="w", pady=(2, 0), padx=(25, 0))

    password_entry = ctk.CTkEntry(frame2,placeholder_text="Enter Password",  fg_color="#EEEEEE", border_color="#000080", border_width=1, text_color="#000000", show="*",width=255,)
    password_entry.pack(anchor="w", padx=(25, 0))

    check_password_label = ctk.CTkLabel(frame2, text="Re-enter Password:", text_color="#000080",anchor="w", justify="left", font=("Arial Bold", 14), compound="left")
    check_password_label.pack(anchor="w", padx=(25, 0))

    check_password_entry = ctk.CTkEntry(frame2,placeholder_text="Re-Enter Password",  fg_color="#EEEEEE", border_color="#000080", border_width=1, text_color="#000000", show="*",width=255,)
    check_password_entry.pack(anchor="w", padx=(25, 0))
    sign_up_button = ctk.CTkButton(frame2, text="Sign Up",width=255 ,command=lambda: sign_up_details(root,signup_username_entry,signup_email_entry,password_entry,rname_entry))
    sign_up_button.pack(anchor="w",pady=(2, 0), padx=(25, 0) )
    sign_up_button.configure(state="disabled")

    
    check_password_entry.bind("<Key>", lambda event: check_password(event, sign_up_button))
    check_password_entry.bind("<FocusOut>", lambda event: check_password(event, sign_up_button))
    signup_username_entry.bind("<FocusOut>", lambda event: check_username(event,sign_up_button))
    signup_email_entry.bind("<FocusOut>", lambda event: check_email(event,sign_up_button))


    
    entries = [rname_entry, signup_username_entry, signup_email_entry, password_entry]

    for entry in entries:
        entry.bind("<KeyRelease>", lambda event: check_entries(event, entries, sign_up_button))

