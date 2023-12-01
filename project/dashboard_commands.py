import customtkinter as ctk
from dbconnection import create_db_connection
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from tkinter import *
import tkinter as tk

import customtkinter as ctk
from tkinter import  PhotoImage
from PIL import Image, ImageTk
import PIL.Image
import tkinter
from dbconnection import create_db_connection
import tkinter as tk
from dashboard_commands import *
from ttkthemes import ThemedTk
from tkinter import ttk

conn,cursor=create_db_connection()


#missing book, returned book,overdue book , borrowed book


from datetime import datetime

def get_outdated_books(outdated_books_table):
    if outdated_books_table is not None:
        for widgets in outdated_books_table.winfo_children():
            widgets.destroy()

    conn, cursor = create_db_connection()

    query = """
    SELECT borrowedreturned.borrowdate, borrowedreturned.returndate, users.user_id, users.email, book.book_id, book.title,
    CASE WHEN CURRENT_DATE > borrowedreturned.returndate THEN CURRENT_DATE - borrowedreturned.returndate ELSE 0 END AS days_overdue,
    CASE WHEN CURRENT_DATE > borrowedreturned.returndate THEN (CURRENT_DATE - borrowedreturned.returndate) * 50 ELSE 0 END AS fine
    FROM borrowedreturned
    INNER JOIN users ON borrowedreturned.user_id = users.user_id
    INNER JOIN book ON borrowedreturned.book_id = book.book_id
    WHERE borrowedreturned.returndate < CURRENT_DATE AND borrowedreturned.status_id = 1
    """
    cursor.execute(query)
    results = cursor.fetchall()

    
    for i in range(min(len(results), 1000) + 1):  #
        outdated_books_table.grid_rowconfigure(i, weight=1)
    for j in range(7):
        outdated_books_table.grid_columnconfigure(j, weight=1)
    outdatedframe=ctk.CTkFrame(outdated_books_table,fg_color="#FFFFFF")
    outdatedframe.grid(row=0,rowspan=20,column=0,columnspan=8,sticky='nsew',padx=(10,10),pady=(0,0))
    
    style = ttk.Style()
    style.layout('Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'ns'})], 'sticky': 'ns'})])
    style.configure('Vertical.TScrollbar', troughcolor ='#FFFFFF', background='#000000') 
    
    canvas = tk.Canvas(outdatedframe,bg="#FFFFFF",background="#FFFFFF")
    scrollbar = ttk.Scrollbar(outdatedframe, orient="vertical", command=canvas.yview,style="Vertical.TScrollbar")  
    scrollable_frame = tk.Frame(canvas,bg="#FFFFFF")
        
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))

    
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    header = ["BorrowDate", "ReturnDate", "User_ID", "Email", "Book_ID", "Title", "Days_Overdue", "Fine"]
    for d in range(len(header)):
        scrollable_frame.grid_columnconfigure(d,weight=1)
        scrollable_frame.grid_rowconfigure(d,weight=1)
    for j ,field in enumerate(header):
        cell_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", bg='black')
        cell_frame.grid(row=0, column=j, sticky='nsew', padx=10, pady=10)
        header_label = tk.Label(cell_frame, text=str(field), bg='black', fg='white', font=('Arial', 12))
        header_label.pack(fill='both', expand=True)

    
    if results:

    
        for i, book in enumerate(results, start=1):  
            for j, field in enumerate(book.values()):  
                cell_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", bg='white')
                cell_frame.grid(row=i, column=j, sticky='nsew', padx=5, pady=5)
                book_label = tk.Label(cell_frame, text=str(field), bg='white', fg='black', font=('Arial', 12))
                book_label.pack(fill='both', expand=True)
    else:
         label=ctk.CTkLabel(scrollable_frame,text="No overdue books")
         label.grid()


def update_status(event, reserve_id, cell_frame,stats_button,book_id):
    print("update status")
    
    status_options = ['Reserved', 'Cancelled', 'Picked Up', 'Returned']
    status_ids={'Picked up':1,'Returned':2,'Missing':4,'Cancelled':2,'Reserved':3}
    
    options_frame = tk.Frame(cell_frame)
    options_frame.pack()
    
    for option in status_options:
        button = tk.Button(options_frame, text=option, command=lambda option=option: update_book_status(book_id, status_ids[option], options_frame, status_button, status_ids))
        button.pack(side='left')

def update_book_status(book_id, new_status_id, options_frame, status_button, status_ids):
    
    conn,cursor=create_db_connection()
    query = f"""
    UPDATE borrowedreturned
    JOIN book ON borrowedreturned.book_id = book.book_id
    SET borrowedreturned.status_id = '{new_status_id}'
    WHERE book.book_id = {book_id}
    """
    cursor.execute(query)
    conn.commit()
    
    options_frame.destroy()
    
    status_button.configure(text=list(status_ids.keys())[list(status_ids.values()).index(new_status_id)])       

def totalbooks_get(totalbooks):
    conn,curser=create_db_connection()
    query=f"SELECT COUNT(*) FROM book"
    curser.execute(query)
    rows=curser.fetchone()
    conn.close()
    totalbooks.grid_rowconfigure(0,weight=1)
    totalbooks.grid_rowconfigure(1,weight=1)
    tlabel=ctk.CTkLabel(totalbooks,text="Total Books")
    tlabel.grid(row=0,sticky="nsew",padx=(10,0))
    label=ctk.CTkLabel(totalbooks,text=f"{rows['COUNT(*)']}",font=("Arial Bold",24),text_color="#000000",anchor="w")
    label.grid(row=1,sticky="nsew",padx=(10,0))


def totalusers_get(totalusers):
    conn,curser=create_db_connection()
    query=f"SELECT COUNT(*) FROM users WHERE user_role='user'"
    curser.execute(query)
    rows=curser.fetchone()
    conn.close()
    totalusers.grid_rowconfigure(0,weight=1)
    totalusers.grid_rowconfigure(1,weight=1)
    tlabel=ctk.CTkLabel(totalusers,text="Total Users")
    tlabel.grid(row=0,sticky="nsew",padx=(10,0))
    label=ctk.CTkLabel(totalusers,text=f"{rows['COUNT(*)']}",font=("Arial Bold",24),text_color="#000000",anchor="w")
    label.grid(row=1,sticky="nsew",padx=(10,0))

def borrowedbooks_get(borrowedbooks):
    conn,curser=create_db_connection()
    query=f"SELECT COUNT(*) FROM borrowedreturned WHERE borrowedreturned.status_id=3"
    curser.execute(query)
    rows=curser.fetchone()
    conn.close()
    borrowedbooks.grid_rowconfigure(0,weight=1)
    borrowedbooks.grid_rowconfigure(1,weight=1)
    tlabel=ctk.CTkLabel(borrowedbooks,text="Borrowed Books")
    tlabel.grid(row=0,sticky="nsew",padx=(10,0))
    label=ctk.CTkLabel(borrowedbooks,text=f"{rows['COUNT(*)']}",font=("Arial Bold",24),text_color="#000000",anchor="w")
    label.grid(row=1,sticky="nsew",padx=(10,0))

def returnedbooks_get(returnedbooks):
        conn,curser=create_db_connection()
        query=f"SELECT COUNT(*) FROM borrowedreturned WHERE borrowedreturned.status_id=2"
        curser.execute(query)
        rows=curser.fetchone()
        conn.close()
        returnedbooks.grid_rowconfigure(0,weight=1)
        returnedbooks.grid_rowconfigure(1,weight=1)
        tlabel=ctk.CTkLabel(returnedbooks,text="Returned Books")
        tlabel.grid(row=0,sticky="nsew",padx=(10,0))
        label=ctk.CTkLabel(returnedbooks,text=f"{rows['COUNT(*)']}",font=("Arial Bold",24),text_color="#000000",anchor="w")
        label.grid(row=1,sticky="nsew",padx=(10,0))
def overduebooks_get(overduebooks):
        conn,curser=create_db_connection()
        query=f"SELECT COUNT(*) FROM borrowedreturned WHERE ReturnDate < CURRENT_DATE AND status_id=3"
        curser.execute(query)
        rows=curser.fetchone()
        conn.close()
        overduebooks.grid_rowconfigure(0,weight=1)
        overduebooks.grid_rowconfigure(1,weight=1)
        tlabel=ctk.CTkLabel(overduebooks,text="Overdue Books")
        tlabel.grid(row=0,sticky="nsew",padx=(10,0))
        label=ctk.CTkLabel(overduebooks,text=f"{rows['COUNT(*)']}",font=("Arial Bold",24),text_color="#000000",anchor="w")
        label.grid(row=1,sticky="nsew",padx=(10,0))

def missingbooks_get(missingbooks):
        conn,curser=create_db_connection()
        query=f"SELECT COUNT(*) FROM book,borrowedreturned WHERE borrowedreturned.status_id=3"
        curser.execute(query)
        rows=curser.fetchone()
        conn.close()
        missingbooks.grid_rowconfigure(0,weight=1)
        missingbooks.grid_rowconfigure(1,weight=1)
        tlabel=ctk.CTkLabel(missingbooks,text="Missing Books")
        tlabel.grid(row=0,sticky="nsew",padx=(10,0))
        label=ctk.CTkLabel(missingbooks,text=f"{rows['COUNT(*)']}",font=("Arial Bold",24),text_color="#000000",anchor="w")
        label.grid(row=1,sticky="nsew",padx=(10,0))


def graph(graph):
        fig, ax = plt.subplots()

        conn, cursor = create_db_connection()
        query = """SELECT DAYOFWEEK(BorrowDate) AS Weekday, COUNT(*) AS noofbooks FROM borrowedreturned GROUP BY DAYOFWEEK(BorrowDate)"""
        cursor.execute(query)
        borrowed_data = pd.DataFrame(cursor.fetchall(), columns=["Weekday", "noofbooks"])
        cursor.execute("""SELECT DAYOFWEEK(ReturnDate) AS Weekday, COUNT(*) AS noofbooks FROM borrowedreturned GROUP BY DAYOFWEEK(ReturnDate)""")
        returned_data = pd.DataFrame(cursor.fetchall(), columns=['Weekday', 'noofbooks'])
        
        
        all_days = pd.DataFrame({'Weekday': np.arange(1, 8), 'noofbooks': np.zeros(7)})

        
        borrowed_data = pd.merge(all_days, borrowed_data, on='Weekday', how='left').fillna(0)
        returned_data = pd.merge(all_days, returned_data, on='Weekday', how='left').fillna(0)

        

        
        days = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
        borrowed_data['Weekday'] = borrowed_data['Weekday'].replace(days)
        returned_data['Weekday'] = returned_data['Weekday'].replace(days)

        
        ax.plot(borrowed_data['Weekday'], borrowed_data['noofbooks_x'], label='Borrowed Books')
        ax.plot(returned_data['Weekday'], returned_data['noofbooks_y'], label='Returned Books')
        ax.set_xlabel('Weekday')
        ax.set_ylabel('Number of Books')
        ax.set_title('Number of Books Borrowed and Returned on Each Weekday')
        ax.legend()

        
        canvas = FigureCanvasTkAgg(fig, master=graph)
        canvas.draw()
        canvas.get_tk_widget().pack()

def reservedtable(reservetables):
    global reservetable,status_button
    if reservetables is not None:
        for widgets in reservetables.winfo_children():
                widgets.destroy()
         
    reservetable=reservetables
    conn,cursor=create_db_connection()

    query = "SELECT * FROM book,borrowedreturned WHERE borrowedreturned.status_id=3"
    cursor.execute(query)
    results=cursor.fetchall()

    
    for i in range(min(len(results), 1000) + 1):  
        reservetable.grid_rowconfigure(i, weight=1)
    for j in range(7):
        reservetable.grid_columnconfigure(j,weight=1)

    reserveframe=ctk.CTkFrame(reservetable,fg_color="#FFFFFF")
    reserveframe.grid(row=0,rowspan=20,column=0,columnspan=7,sticky="nsew",padx=(10,10),pady=(0,0))

    style = ttk.Style()
    style.layout('Vertical.TScrollbar', [('Vertical.Scrollbar.trough', {'children': [('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'ns'})], 'sticky': 'ns'})])
    style.configure('Vertical.TScrollbar', troughcolor ='#FFFFFF', background='#000000') 
    
    canvas = tk.Canvas(reserveframe,bg="#FFFFFF",background="#FFFFFF")
    scrollbar = ttk.Scrollbar(reserveframe, orient="vertical", command=canvas.yview,style="Vertical.TScrollbar")  
    scrollable_frame = tk.Frame(canvas,bg="#FFFFFF")

    
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))

    
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    
    header = ["ID", "Book_ID", "User_ID", "PickupDate", "ReturnDate", "Status"]
    for d in range(len(header)):
        scrollable_frame.grid_columnconfigure(d,weight=1,minsize=20)
        scrollable_frame.grid_rowconfigure(d,weight=1,minsize=20)
    for j, field in enumerate(header):
        cell_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", bg='black')
        cell_frame.grid(row=0, column=j, sticky='nsew',padx=10,pady=10)
        header_label = tk.Label(cell_frame, text=str(field), bg='black', fg='white', font=('Arial', 12))
        header_label.pack(fill='both', expand=True)

    if results:
        print(results)
        
        for i, reserve in enumerate(results, start=1):  
            for j, field in enumerate(reserve.values()):  
                cell_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", bg='white')
                cell_frame.grid(row=i, column=j, sticky='nsew',padx=5,pady=5)
                if j == 6:  
                    status_button = tk.Button(cell_frame, text=str(field), bg='#FFFFFF', fg='black', font=('Arial', 12))
                    status_button.bind('<Button-1>', lambda e, item=reserve['borrowid'], cell_frame=cell_frame: update_status(e, item, cell_frame))  
                    status_button.pack(fill='both', expand=True)

                else:
                    reserve_label = tk.Label(cell_frame, text=str(field), bg='white', fg='black', font=('Arial', 12))
                    reserve_label.pack(fill='both', expand=True)
    else:
         label=ctk.CTkLabel(scrollable_frame,text="No Reservations For today")
         label.grid()



def addnewcat(frame_forframe):
    languages=None
    frame_forframe=frame_forframe
    for i in range(18):
            frame_forframe.grid_rowconfigure(i,weight=1)
    for j in range(8):
            frame_forframe.grid_columnconfigure(j,weight=1)

    def updating(event,table_name,column_name,new_entry):
            result = cursor.execute(f"SELECT * FROM {table_name} WHERE {column_name}='{new_entry}'")
            rows = cursor.fetchall()  
            if rows:
                label.configure(text=f"{category_type_entry.get().capitalize()} already exists in table")
                category_type_entry.delete(0, "end")
                return

            if category_type_entry.get()=='language':
                cursor.execute(f"INSERT INTO {table_name} ({column_name}, language_code) VALUES ('{new_entry}', '{languages}')")
            else:
                cursor.execute(f"INSERT INTO {table_name} ({column_name}) VALUES ('{new_entry}')")
            conn.commit()
            label.configure(text=f'Succesfully Added')

    def remove_category(event,table_name,column_name,new_entry):
        
        cursor.execute(f"SELECT * FROM {table_name} WHERE {column_name}='{new_entry}'")
        rows = cursor.fetchall()
        if rows:
            if category_type_entry.get()=='language':
                cursor.execute(f"DELETE FROM {table_name} WHERE {column_name}='{new_entry}'")
                label.configure(text=f'Successfully removed {new_entry} from {table_name}',fg_color='#cc0000')

            else:
                cursor.execute(f"DELETE FROM {table_name} WHERE {column_name}='{new_entry}'")

       
                conn.commit()
                label.configure(text=f'Successfully removed {new_entry} from {table_name}',fg_color='#cc0000')


        else:
            label.configure(text=f"{new_entry} does not exist in {table_name}")
            return
    def check_add(event):
        table_name = ''
        column_name = ''
        new_entry = None
        if category_type_entry.get() == 'author':
            table_name = 'author'
            column_name = 'author_name'
            try:
                language_code.destroy()
            except:
                pass
        elif category_type_entry.get() == 'genre':
            table_name = 'genres'
            column_name = 'genre_name'
            try:
                language_code.destroy()
            except:
                pass
        elif category_type_entry.get() == 'language':
            table_name = 'book_language'
            column_name = 'language_name'
            langlabel=ctk.CTkLabel(frame_forframe, text="Language Code:", fg_color="#FFFFFF", bg_color="#F5F5F5", font=("Roboto",24))

            langlabel.grid(row=3,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
            language_code=ctk.CTkEntry(frame_forframe,placeholder_text="Enter language code",fg_color="#FFFFFF", corner_radius=20,placeholder_text_color="#7E7E7E")
            language_code.grid(row=3,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))
            languages=language_code.get()
        else:
            label.configure(text=f"Unknown category type: {category_type_entry.get()}")
            try:
                language_code.destroy()
            except:
                pass
            return
        newlabel=ctk.CTkLabel(frame_forframe,text=f"{column_name}:",fg_color="#FFFFFF",bg_color="#F5F5F5",font=("Roboto",24))
        newlabel.grid(row=2,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
        new_entry = ctk.CTkEntry(frame_forframe, placeholder_text=f"Enter new {category_type_entry.get()}",fg_color="#FFFFFF", corner_radius=20,placeholder_text_color="#7E7E7E")
        new_entry.grid(row=2,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))
        add_button = ctk.CTkButton(frame_forframe, text="Add", command= lambda: updating(None,table_name,column_name,new_entry.get()))
        add_button.grid(row=4, column=1)

        
        remove_button = ctk.CTkButton(frame_forframe, text="Remove", command= lambda: remove_category(None,table_name,column_name,new_entry.get()))
        remove_button.grid(row=4, column=2)
    label=ctk.CTkLabel(frame_forframe,text="")
    label.grid(row=0,column=1,columnspan=5,padx=(20,20),pady=(40,80))
   
    categorylabel=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="New Category:",font=("Roboto",24))
    categorylabel.grid(row=1,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
    category_type_entry=ctk.CTkEntry(frame_forframe,placeholder_text="Enter Category author,language,genre", fg_color="#FFFFFF", corner_radius=20,placeholder_text_color="#7E7E7E")
    category_type_entry.grid(row=1,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))    
    category_type_entry.bind("<Return>",command= lambda event: check_add(event))
