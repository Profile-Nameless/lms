import customtkinter as ctk
from tkinter import  PhotoImage
from PIL import Image, ImageTk
import PIL.Image
import tkinter
from dbconnection import create_db_connection
import tkinter as tk
from tkinter import ttk

conn,cursor=create_db_connection()

def setup_window():
    global root
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(r"dark-blue")
    
    root = ctk.CTk()
    return root
def center_window(root, app_width, app_height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    app_center_coordinate_x = (screen_width / 3) - (app_width/3)
    app_center_coordinate_y = (screen_height / 3) - (app_height/3)
    root.geometry(f"{app_width}x{app_height}+{int(app_center_coordinate_x)}+{int(app_center_coordinate_y)}")
def topframe_search(root,event=None):
    global scrollbar
    reset_button_colors()
    conn,cursor=create_db_connection()
    search_term=search_entry.get()
    def load_more_data(results):
        conn,cursor=create_db_connection()
        
        last_book_id = results[-1]['book_id']
        
        query = f"""
            SELECT book.book_id, book.title, book.isbn13, book_language.language_name, book.num_pages, book.publication_date, publisher.publisher_name, book.file_path, COALESCE(book_status.status_name, 'Available') AS status_name
            FROM book
            LEFT JOIN borrowedreturned ON book.book_id = borrowedreturned.book_id
            LEFT JOIN book_status ON borrowedreturned.status_id = book_status.status_id
            LEFT JOIN book_language ON book.language_id = book_language.language_id
            LEFT JOIN publisher ON book.publisher_id = publisher.publisher_id
            WHERE book.book_id > {last_book_id}
            LIMIT 20"""
        cursor.execute(query)

        more_data = cursor.fetchall()
        results.extend(more_data)  
        return results

    def on_scroll(event,canvas,scrollable_frame,results):
        
        if canvas.yview()[1] == 1.0:
            
            results = load_more_data(results)  
            
            for i, book in enumerate(results, start=1):  
                for j, field in enumerate(book.values()):
                    cell_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", bg='white')
                    cell_frame.grid(row=i, column=j, sticky='nsew',padx=5,pady=5)
                    
                    book_label = tk.Label(cell_frame, text=str(field), bg='white', fg='black', font=('Arial', 12))
                        
                    book_label.pack(fill='both', expand=True)
                    canvas.configure(scrollregion=canvas.bbox("all"))
            
            scrollbar.bind("<B1-Motion>", lambda event: on_scroll(event,canvas,scrollable_frame,results))


    if search_term.lower()=='all':
        query = f"""
    SELECT book.book_id, book.title, book.isbn13, book_language.language_name, book.num_pages, book.publication_date, publisher.publisher_name, book.file_path, COALESCE(book_status.status_name, 'Available') AS status_name
    FROM book
    LEFT JOIN borrowedreturned ON book.book_id = borrowedreturned.book_id
    LEFT JOIN book_status ON borrowedreturned.status_id = book_status.status_id
    LEFT JOIN book_language ON book.language_id = book_language.language_id
    LEFT JOIN publisher ON book.publisher_id = publisher.publisher_id
    LIMIT 50"""

    else:
            query = f"""
        SELECT book.book_id, book.title, book.isbn13, book_language.language_name, book.num_pages, book.publication_date, publisher.publisher_name, book.file_path, COALESCE(book_status.status_name, 'Available') AS status_name
        FROM book
        LEFT JOIN borrowedreturned ON book.book_id = borrowedreturned.book_id
        LEFT JOIN book_status ON borrowedreturned.status_id = book_status.status_id
        LEFT JOIN book_language ON book.language_id = book_language.language_id
        LEFT JOIN publisher ON book.publisher_id = publisher.publisher_id
        WHERE book.book_id LIKE '%{search_term}%' 
        OR title LIKE '%{search_term}%' 
        OR isbn13 LIKE '%{search_term}%' 
        OR book_language.language_name LIKE '%{search_term}%' 
        OR num_pages LIKE '%{search_term}%' 
        OR publication_date LIKE '%{search_term}%' 
        OR publisher.publisher_name LIKE '%{search_term}%' 
        OR file_path LIKE '%{search_term}%' LIMIT 50"""




    cursor.execute(query)
    results=cursor.fetchall()
    for widget in frame_forframe.winfo_children():
        widget.destroy()
    
    
    canvas = tk.Canvas(frame_forframe,bg="#FFFFFF")
    scrollbar = ttk.Scrollbar(frame_forframe, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas,bg="#FFFFFF")
    
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(frame_id, width=e.width))
    
    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    for i in range(20):
        scrollable_frame.grid_rowconfigure(i,weight=1)
    for j in range(10):
        scrollable_frame.grid_columnconfigure(j,weight=1)
    print(results)
    tableframe=ctk.CTkFrame(scrollable_frame,fg_color="#FFFFFF")  
    tableframe.grid(row=0,rowspan=20,column=0,columnspan=10,sticky="nsew",padx=(10,10),pady=(0,0))
    header = ["Book_id", "Title", "ISBN13", "language_name","num_pages", "Publication Date",'Publisher' ,"File path","Status"]
    for j, field in enumerate(header):
        cell_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", bg='black')
        cell_frame.grid(row=0, column=j, sticky='nsew',padx=10,pady=0)
        header_label = tk.Label(cell_frame, text=str(field), bg='black', fg='white', font=('Arial', 12))
        header_label.pack(fill='both', expand=True)
    
    if results:
        
        for i, book in enumerate(results, start=1):  
           for j, field in enumerate(book.values()):  
            cell_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid", bg='white')
            cell_frame.grid(row=i, column=j, sticky='nsew',padx=5,pady=5)
        
            book_label = tk.Label(cell_frame, text=str(field), bg='white', fg='black', font=('Arial', 12))
               
            book_label.pack(fill='both', expand=True)
        
    else:
            print("not happening apple")
            for i in range(10):
                tableframe.grid_columnconfigure(i,weight=1,minsize=20)
                tableframe.grid_rowconfigure(i,weight=1,minsize=20)
            
            not_found=ctk.CTkLabel(tableframe,text=f"{search_term} not found or Book does not exist,\n Please check if you searched properly",font=("Arial bold",24),text_color="#7E7E7E")
            not_found.grid(column=2,row=3,columnspan=6,rowspan=4,sticky="nsew",padx=(60,0),pady=(0,0))
    scrollbar.bind("<B1-Motion>", on_scroll(None,canvas,scrollable_frame,results))




def topframe_widgets(root,name):
    global search_entry
    for i in range(1,10):
        topframe.grid_columnconfigure(i,weight=1,minsize=28)
    logo_icon=PIL.Image.open("photos\\vecteezy_graduation-hat-vector-icon-isolated-on-white-background_6309469.jpg")
    logo_icon=ctk.CTkImage(dark_image=logo_icon, light_image=logo_icon, size=(17,17))
    logo=ctk.CTkLabel(topframe,text="StudySpark",font=("Roboto",24),anchor="center",image=logo_icon, compound="left")
    logo.grid(row=0,column=0,columnspan=3,sticky="nsew",padx=(0,0),pady=(0,0))
    topframe.grid_propagate(False)


    search_img = PIL.Image.open("photos//search-icon-png-9966.png")
    
    search_img =ctk.CTkImage(dark_image=search_img,light_image=search_img,size=(17,17))
    search_img=ctk.CTkLabel(topframe,text="",image=search_img,compound="left")

    search_img.grid(row=0,column=6,padx=(0,0),pady=(10,0),sticky="nsew")
    search_entry=ctk.CTkEntry(topframe,placeholder_text="Enter author,book,publisherid,etc",placeholder_text_color="#7E7E7E",fg_color="#FFFFFF",border_color= "#7E7E7E",corner_radius=15,width=300)
    search_entry.grid(row=0,column=7,columnspan=3,sticky="nsew",pady=(10,0))
    print(name)
    name_label=ctk.CTkLabel(topframe,text=f"Welcome, {name}",font=("Roboto",20),text_color="#708090",justify="right")
    name_label.grid(row=0,column=10,sticky="nsew",padx=(500,0))
    search_entry.bind("<Return>",lambda event: topframe_search(root,"a"))

def reset_button_colors():
    dashboard_button.configure(fg_color="#FFFFFF", text_color="#7E7E7E")
    
    reservebook_button.configure(fg_color="#FFFFFF",text_color="#7E7E7E")
    

def dashboard(root,dashboard_button):
    for widget in frame_forframe.winfo_children():
        widget.destroy()
    reset_button_colors()


    for i in range(18):
        frame_forframe.grid_rowconfigure(i,weight=1)
    for j in range(8):
        frame_forframe.grid_columnconfigure(j,weight=1)
        def get_outdated_books(outdated_books_table):
            if outdated_books_table is not None:
                for widgets in outdated_books_table.winfo_children():
                    widgets.destroy()

            conn, cursor = create_db_connection()

            query = f"""
SELECT borrowedreturned.borrowdate, borrowedreturned.returndate, book.book_id, book.title
FROM borrowedreturned INNER JOIN users ON borrowedreturned.user_id = users.user_id
INNER JOIN book ON borrowedreturned.book_id = book.book_id
WHERE borrowedreturned.status_id = 1 AND
users.user_id = {user_idd}
"""

            cursor.execute(query)
            results = cursor.fetchall()

            
            for i in range(min(len(results), 1000) + 1):  
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

    def get_reserved_books(outdated_books_table):
            if outdated_books_table is not None:
                for widgets in outdated_books_table.winfo_children():
                    widgets.destroy()

            conn, cursor = create_db_connection()

            query =  f"""
    SELECT borrowedreturned.borrowdate, borrowedreturned.returndate, book.book_id, book.title
    FROM borrowedreturned INNER JOIN users ON borrowedreturned.user_id = users.user_id
    INNER JOIN book ON borrowedreturned.book_id = book.book_id
    WHERE borrowedreturned.status_id = 3 AND
    users.user_id = {user_idd}
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

            header = ["BorrowDate", "ReturnDate", "Book_ID", "Title"]
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
                label=ctk.CTkLabel(scrollable_frame,text="No reserved books")
                label.grid()

    def currently_borrowed(outdated_books_table):
            if outdated_books_table is not None:
                for widgets in outdated_books_table.winfo_children():
                    widgets.destroy()

            conn, cursor = create_db_connection()

            query = f"""
SELECT borrowedreturned.borrowdate, borrowedreturned.returndate, book.book_id, book.title
FROM borrowedreturned INNER JOIN users ON borrowedreturned.user_id = users.user_id
INNER JOIN book ON borrowedreturned.book_id = book.book_id
WHERE borrowedreturned.status_id = 1 AND
users.user_id = {user_idd}
"""

            cursor.execute(query)
            results = cursor.fetchall()

            
            for i in range(min(len(results), 1000) + 1):  
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

            header = ["BorrowDate", "ReturnDate", "Book_ID", "Title"]
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
                label=ctk.CTkLabel(scrollable_frame,text="No borrowed books")
                label.grid()

    
    borrowedlabel=ctk.CTkLabel(frame_forframe,fg_color="#7E7E7E",bg_color="#F5F5F5",text="Borrowed Books:",font=("Arial Bold",24))
    borrowedlabel.grid(row=3,column=0,columnspan=2)
    currently=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    currently.grid(row=4,column=0,rowspan=5,columnspan=5,sticky="nsew",padx=(0,65),pady=(10,20))
    currently_borrowed(currently)
    
    overduelabel=ctk.CTkLabel(frame_forframe,fg_color="#7E7E7E",bg_color="#F5F5F5",text="OverdueBooks:",font=("Arial Bold",24))
    overduelabel.grid(row=3,column=5,columnspan=2)
    overduetable=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    overduetable.grid(row=4,column=4,rowspan=5,columnspan=5,sticky="nsew",padx=(65,10),pady=(10,20))
    get_outdated_books(overduetable)
    
    reservedlabel=ctk.CTkLabel(frame_forframe,fg_color="#7E7E7E",bg_color="#F5F5F5",text="Reserved Books:",font=("Arial Bold",24))
    reservedlabel.grid(row=11,column=0,columnspan=2)
    recentborrowed=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    recentborrowed.grid(row=12,column=0,rowspan=6,columnspan=8,sticky="nsew",padx=(40,30),pady=(0,20))

    get_reserved_books(recentborrowed)

def frames(root):
    global topframe,dashboard_button,frame_forframe,removebook_button,dashboard_img,reservebook_img,removebook_img,reservebook_button
    n = 20
    k = 10
    
    for i in range(n):
        root.grid_rowconfigure(i, weight=1, minsize=20)
    for j in range(k):
        root.grid_columnconfigure(j, weight=1, minsize=20)
    def reservebooks(reservebook_button):
        for widget in frame_forframe.winfo_children():
            widget.destroy()
        reset_button_colors()
        reservebook_button.configure(fg_color="#008B8B", text_color="#FFFFFF")
        def querying(event):
                book_id = book_id_entry.get()
                borrow_date = borrow_date_entry.get()
                return_date = return_date_entry.get()
                query = "SELECT status_id FROM borrowedreturned WHERE book_id = %s"
                cursor.execute(query, (book_id,))
                result = cursor.fetchone()
            

                if result:
                    print("test")
                    status = result['status_id']
    
                    if status == 1:
                        print("1")
                        label.configure(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="The book is already issued.", font=("Roboto", 24))
                    elif status == 3:
                        print("2")
                        label.configure(frame_forframe, fg_color="#cc0000", bg_color="#F5F5F5", text="The book is reserved by another user.", font=("Roboto", 24))
                else:
                        print("3")
                        query = f"""
            INSERT INTO borrowedreturned (Borrowdate, Returndate,book_id,user_id,status_id) 
            VALUES (%s, %s, %s, %s, 3)"""
                        cursor.execute(query, (borrow_date, return_date, book_id, user_idd))
                        conn.commit()
                        label.configure(text="Succesfully added Reservation")
        book_id = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="Book ID:", font=("Roboto", 24))
        book_id.grid(row=1, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
        book_id_entry = ctk.CTkEntry(frame_forframe, placeholder_text="Enter Book id", fg_color="#FFFFFF", corner_radius=20, placeholder_text_color="#7E7E7E")
        book_id_entry.grid(row=1, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))

        borrow_date = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="Borrow Date:", font=("Roboto", 24))
        borrow_date.grid(row=3, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
        borrow_date_entry = ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20, placeholder_text="Enter borrow date", placeholder_text_color="#7E7E7E")
        borrow_date_entry.grid(row=3, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))

        return_date = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="Return Date:", font=("Roboto", 24))
        return_date.grid(row=4, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
        return_date_entry = ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20, placeholder_text="Enter Return Date", placeholder_text_color="#7E7E7E")
        return_date_entry.grid(row=4, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))
        label=ctk.CTkLabel(frame_forframe)
        label.grid(row=0,column=1,columnspan=3)
        return_date_entry.bind("<Return>",command= lambda event: querying(event=None))
        

    
    frame_forframe=ctk.CTkFrame(root,fg_color="#F5F5F5")
    frame_forframe.grid(row=1,rowspan=n,column=2,columnspan=10,sticky="nsew",padx=(10,10),pady=(30,20))
    topframe=ctk.CTkFrame(root,height=50,fg_color="#FFFFFF")
    topframe.grid(row=0,column=0,rowspan=n,columnspan=k,sticky="new",padx=(1,1),pady=(1,1))
    
    sidebar=ctk.CTkFrame(root,fg_color="#FFFFFF",width=300)
    sidebar.grid(row=0,column=0,rowspan=n,columnspan=2,sticky="nsew",pady=(52,1),padx=(0,10))
    for l in range(10):
        sidebar.grid_rowconfigure(l,weight=1,minsize=20)
    
    dashboard_img=PIL.Image.open("photos/icons8-dashboard-24.png")
    dashboard_img=ctk.CTkImage(dark_image=dashboard_img,light_image=dashboard_img,size=(17,17))
    dashboard_button = ctk.CTkButton(sidebar, image=dashboard_img,compound="left",text="Dashboard",text_color="#7E7E7E",fg_color="#FFFFFF",corner_radius=20,width=200,height=40)
    dashboard_button.grid(row=1,columnspan=3,column=0,padx=(40,0), sticky="ew")

    reservebook_img=PIL.Image.open("photos\icons8-book-50.png")
    reservebook_img=ctk.CTkImage(dark_image=reservebook_img,light_image=reservebook_img,size=(17,17))
    reservebook_button=ctk.CTkButton(sidebar,image=reservebook_img,compound="left",text="Reserve Book",text_color="#7E7E7E",fg_color="#FFFFFF",corner_radius=20,height=40,command=lambda: reservebooks(reservebook_button))
    reservebook_button.grid(row=2,columnspan=3,column=0,padx=(40,0),sticky="ew")
    

    

def admin_widgets(root,name):
    topframe_widgets(root,name)
    dashboard(root,dashboard_button)
def open_user_dashboard(rname,id):
    global name,user_idd
    name=rname
    user_idd=id
    app_width = 1000
    app_height = 500
    root=setup_window()
    center_window(root, app_width, app_height)
    frames(root)  
    admin_widgets(root,name)
    root.mainloop()
    
if __name__ == "__main__":
    open_user_dashboard("apple",1)
