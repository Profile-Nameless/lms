import customtkinter as ctk
from tkinter import  PhotoImage
from PIL import Image, ImageTk
import PIL.Image
import tkinter
from dbconnection import create_db_connection
import tkinter as tk
from dashboard_commands import *


global name


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


def reset_button_colors():
    dashboard_button.configure(fg_color="#FFFFFF", text_color="#7E7E7E")
    addbook_button.configure(fg_color="#FFFFFF", text_color="#7E7E7E")
    removebook_button.configure(fg_color="#FFFFFF", text_color="#7E7E7E")
    Issue_Return_button.configure(fg_color="#FFFFFF",text_color='#7E7E7E')
    addcategory_button.configure(fg_color="#FFFFFF",text_color="#7E7E7E")




def topframe_search(root,event=None):
    global scrollbar
    reset_button_colors()
    conn,cursor=create_db_connection()
    search_term=search_entry.get()
    def switch_to_edit_mode(event, id, widget):
        if isinstance(widget, tk.Label): 
            text = widget.cget("text")
            widget.destroy()
            entry = tk.Entry(widget.master, bg='white', fg='black', font=('Arial', 12))
            entry.insert(0, text)
            entry.bind('<Return>', lambda event, id=id, entry=entry: save_changes(event, id, entry))
            entry.pack(fill='both', expand=True)
        else:  
            pass

    def save_changes(event, id, entry):

        new_value = entry.get()
        conn,cursor=create_db_connection()
        query = f"""
        UPDATE book
        SET title = '{new_value}'
        WHERE book_id = {id}
        """
        cursor.execute(query)
        conn.commit()

        entry.destroy()
        label = tk.Label(entry.master, text=new_value, bg='white', fg='black', font=('Arial', 12))
        label.bind('<Button-3>', lambda event, id=id, widget=label: switch_to_edit_mode(event, id, widget))  
        label.pack(fill='both', expand=True)


    def update_book_status(book_id, new_status_id, options_frame, status_button):

        status_ids={'Issued':1,'Available':2,'Returned':3,'Missing':4,'Reserved':5}
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


    def update_status(event, book_id, cell_frame, status_button):
        if hasattr(update_status, 'options_frame'):
            update_status.options_frame.destroy()
            return
        status_options = ['Issued', 'Available', 'Returned','Missing','Reserved']
        status_ids={'Issued':1,'Available':2,'Returned':2,'Missing':4,'Reserved':3}
        options_frame = tk.Frame(cell_frame)
        options_frame.pack()
        update_status.options_frame = options_frame
        for option in status_options:
            button = tk.Button(options_frame, text=option, command=lambda option=option:update_book_status(book_id, status_ids[option], options_frame, status_button))
            button.pack(side='left')


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
                    if j == 8:  
                        status_button = tk.Button(cell_frame, text=str(field), bg='#FFFFFF', fg='black', font=('Arial', 12))
                        status_button.bind('<Button-1>', lambda event, book_id=book['book_id'], cell_frame=cell_frame: update_status(event, book_id, cell_frame, status_button))  
                        status_button.pack(fill='both', expand=True)
                    else:
                        book_label = tk.Label(cell_frame, text=str(field), bg='white', fg='black', font=('Arial', 12))
                        book_label.bind('<Double-1>', lambda event, id=book['book_id'], widget=book_label: switch_to_edit_mode(event, id, widget))  
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
            if j == 8:  
                status_button = tk.Button(cell_frame, text=str(field), bg='#FFFFFF', fg='black', font=('Arial', 12))
                status_button.bind('<Button-1>', lambda event, book_id=book['book_id'], cell_frame=cell_frame: update_status(event, book_id, cell_frame, status_button))  
                status_button.pack(fill='both', expand=True)
            else:
                book_label = tk.Label(cell_frame, text=str(field), bg='white', fg='black', font=('Arial', 12))
                book_label.bind('<Double-1>', lambda event, id=book['book_id'], widget=book_label: switch_to_edit_mode(event, id, widget)) 
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


tableframe=None
def dashboard(root,dashboard_button):
    for widget in frame_forframe.winfo_children():
        widget.destroy()
    reset_button_colors()


    for i in range(18):
        frame_forframe.grid_rowconfigure(i,weight=1)
    for j in range(8):
        frame_forframe.grid_columnconfigure(j,weight=1)
    
    dashboard_button.configure(fg_color="#008B8B",text_color="#FFFFFF")
    totalbooks=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    totalbooks.grid(row=0,column=0,rowspan=3,columnspan=3,sticky="nsew",padx=(40,80),pady=(20,20))
    totalbooks_get(totalbooks)
    totalvisitors=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    totalvisitors.grid(row=3,column=0,rowspan=3,columnspan=3,sticky="nsew",padx=(40,80),pady=(20,20))
    totalusers_get(totalvisitors)
    borrowedbooks=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    borrowedbooks.grid(row=0,column=2,rowspan=3,columnspan=4,sticky="nsew",padx=(140,110),pady=(20,20))
    borrowedbooks_get(borrowedbooks)
    returnedbooks=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    returnedbooks.grid(row=3,column=2,rowspan=3,columnspan=4,sticky="nsew",padx=(140,110),pady=(20,20))
    returnedbooks_get(returnedbooks)
    overduebooks=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    overduebooks.grid(row=0,column=5,rowspan=3,columnspan=3,sticky="nsew",padx=(80,30),pady=(20,20))
    overduebooks_get(overduebooks)
    missingbooks=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    missingbooks.grid(row=3,column=5,rowspan=3,columnspan=3,sticky="nsew",padx=(80,30),pady=(20,20))
    missingbooks_get(missingbooks)    
    graphframe=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    graphframe.grid(row=6,column=0,rowspan=5,columnspan=4,sticky="nsew",padx=(40,55),pady=(10,20))
    graph(graphframe)

    overduetable=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    overduetable.grid(row=6,column=4,rowspan=5,columnspan=4,sticky="nsew",padx=(65,30),pady=(10,20))
    get_outdated_books(overduetable)
    
    recentborrowed=ctk.CTkFrame(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5")
    recentborrowed.grid(row=12,column=0,rowspan=6,columnspan=8,sticky="nsew",padx=(40,30),pady=(0,20))

    reservedtable(recentborrowed)

def addbook(root,addbook_button):
    def get_publisher_id(publisher_name):
        query = "SELECT publisher_id FROM publisher WHERE publisher_name = %s"
        cursor.execute(query, (publisher_name,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the publisher_id
        else:
            return 0  
    def get_language_id(language_id):
        
        query = "SELECT language_id FROM book_language WHERE language_code = %s or language_name =%s"
        cursor.execute(query, (language_id, language_id))  
        result = cursor.fetchone()
        if result:
            return result[0] 
        else:
            return 0

    def addingbook():
        file_pathss=file_path_entry.get()
        if file_pathss == "":
            file_pathss=None

        publisher_name=publisher_id_entry.get()
        publisher_id=get_publisher_id(publisher_name)
        language_id=language_id_entry.get()
        language_id=get_language_id(language_id)
        query="SELECT * FROM book WHERE book_id=%s"
        cursor.execute(query, (book_id_entry.get(),))

        result=cursor.fetchone()
        if result:
            book_id_entry.delete(0, 'end')
            book_title_entry.delete(0, 'end')
            book_isbn13_entry.delete(0, 'end')
            language_id_entry.delete(0, 'end')
            num_pages_entry.delete(0, 'end')
            publication_dates_entry.delete(0, 'end')
            file_path_entry.delete(0, 'end')
            errorlabel.configure(text="Book already exists")
        else:
          
            query="INSERT INTO book (book_id,title, isbn13, language_id, num_pages, publication_date, file_path,publisher_id) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
            cursor.execute(query, (book_id_entry.get(), book_title_entry.get(), book_isbn13_entry.get(), language_id, num_pages_entry.get(), publication_dates_entry.get(), file_pathss,publisher_id))
            conn.commit() 
            errorlabel.configure(text="Succesfully Added")
        
    for widget in frame_forframe.winfo_children():
        widget.destroy()
    reset_button_colors()
    addbook_button.configure(fg_color="#008B8B",text_color="#FFFFFF")
    for i in range(18):
        frame_forframe.grid_rowconfigure(i,weight=1)
    for j in range(8):
        frame_forframe.grid_columnconfigure(j,weight=1)
    book_id=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Book ID:",font=("Roboto",24))
    book_id.grid(row=1,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
    book_id_entry=ctk.CTkEntry(frame_forframe,placeholder_text="Enter Book id", fg_color="#FFFFFF", corner_radius=20,placeholder_text_color="#7E7E7E")
    book_id_entry.grid(row=1,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    book_title=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Book Title",font=("Roboto",24))
    book_title.grid(row=2,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
    book_title_entry=ctk.CTkEntry(frame_forframe,placeholder_text="Enter Book Title", fg_color="#FFFFFF", corner_radius=20,placeholder_text_color="#7E7E7E")
    book_title_entry.grid(row=2,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    # Additional fields
    book_isbn13=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Book ISBN13:",font=("Roboto",24))
    book_isbn13.grid(row=3,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
    book_isbn13_entry=ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20,placeholder_text="Enter ISBN13",placeholder_text_color="#7E7E7E")
    book_isbn13_entry.grid(row=3,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    language_id=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Language ID:",font=("Roboto",24))
    language_id.grid(row=4,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
    language_id_entry=ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20,placeholder_text="Enter language id",placeholder_text_color="#7E7E7E")
    language_id_entry.grid(row=4,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    num_pages=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Number of Pages:",font=("Roboto",24))
    num_pages.grid(row=5,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
    num_pages_entry=ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20,placeholder_text="Enter No of Pages",placeholder_text_color="#7E7E7E")
    num_pages_entry.grid(row=5,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    publication_dates=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Publication Dates:",font=("Roboto",24))
    publication_dates.grid(row=6,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
    publication_dates_entry=ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20,placeholder_text="Enter Publication Date",placeholder_text_color="#7E7E7E")
    publication_dates_entry.grid(row=6,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    file_path=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="File Path:",font=("Roboto",24))
    file_path.grid(row=7,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20),)
    file_path_entry=ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20,placeholder_text="Enter file path if applicable",placeholder_text_color="#7E7E7E")
    file_path_entry.grid(row=7,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    publisher_id=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Publisher:",font=("Roboto",24))
    publisher_id.grid(row=8,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20),)
    publisher_id_entry=ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20,placeholder_text="Enter Publisher",placeholder_text_color="#7E7E7E")
    publisher_id_entry.grid(row=8,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))

    addbook_button=ctk.CTkButton(frame_forframe,compound="left",text="Add Book",text_color="#7E7E7E",fg_color="#FFFFFF",corner_radius=20,height=40,command=lambda: addingbook())
    addbook_button.grid(row=9,columnspan=3,column=1,padx=(40,0),sticky="ew")
    
    errorlabel=ctk.CTkLabel(frame_forframe,fg_color="#F5F5F5",bg_color="#F5F5F5",text="")
    errorlabel.grid(row=0,column=2,rowspan=1,columnspan=2,sticky='nsew')

    


def removebook(root, removebook_button):
        
        def delete_option(event, book_id):

                menu = tk.Menu(root, tearoff=0)
                menu.add_command(label="Delete", command=lambda: delete_book(book_id))
                menu.post(event.x_root, event.y_root)

        def delete_book(book_id):

                    query = "DELETE FROM book WHERE book_id = %s"

                    try:
                    
                        cursor.execute(query, (book_id,))
                        conn.commit()
                        removingbook()
                        errorlabel.configure(text="Succesfully Deleted")
                    except Exception as e:
                        removingbook()
        def removingbook(event=None):
            
            book_id = book_id_entry.get()
            query = """
    SELECT book.book_id, book.title, book.isbn13, book_language.language_name, book.num_pages, book.publication_date, publisher.publisher_name, book.file_path, COALESCE(book_status.status_name, 'Available') AS status_name 
    FROM book 
    LEFT JOIN borrowedreturned ON book.book_id = borrowedreturned.book_id 
    LEFT JOIN book_status ON borrowedreturned.status_id = book_status.status_id 
    LEFT JOIN book_language ON book.language_id = book_language.language_id 
    LEFT JOIN publisher ON book.publisher_id = publisher.publisher_id 
    WHERE book.book_id = %s"""
            try:
                cursor.execute(query, (book_id,))
                all_results = cursor.fetchall()
                if all_results:
                    print(3)
                else:
                    print('happy')
                header = ['Book ID', 'Title', 'ISBN13', 'Language ID', 'Number of Pages', 'Publication Date', 'Publisher ID', 'File Path','Status']
                
                for j, field in enumerate(header):
                    cell_frame = tk.Frame(frame_forframe, borderwidth=1, relief="solid", bg='black')
                    cell_frame.grid(row=2, column=j, sticky='nsew',padx=10,pady=10)
                    header_label = tk.Label(cell_frame, text=str(field), bg='black', fg='white', font=('Arial', 12))
                    header_label.pack(fill='both', expand=True)
                if all_results:
                    for i, results in enumerate(all_results, start=3): 
                        for j, field in enumerate(results.values()):
                            cell_frame = tk.Frame(frame_forframe, borderwidth=1, relief="solid", bg='white')
                            cell_frame.grid(row=i, column=j, sticky='nsew',padx=5,pady=5)
                            field_label = tk.Label(cell_frame, text=str(field), bg='white', fg='black', font=('Arial', 12))
                            field_label.pack(fill='both', expand=True)
                else:
                    errorlabel.configure(text="Book Doesn't Exist")

                frame_forframe.bind('<Button-3>', lambda event, book_id=book_id: delete_option(event, book_id))
            except Exception as e:
                print("Exception type:", type(e))
                print("Exception message:", e)

                errorlabel.configure(text="Book Doesn't Exist")

        for widget in frame_forframe.winfo_children():
            widget.destroy()
        reset_button_colors()
        removebook_button.configure(fg_color="#008B8B",text_color="#FFFFFF")
        for i in range(18):
            frame_forframe.grid_rowconfigure(i,weight=1)
        for j in range(8):
            frame_forframe.grid_columnconfigure(j,weight=1)
        book_id=ctk.CTkLabel(frame_forframe,fg_color="#FFFFFF",bg_color="#F5F5F5",text="Book ID:",font=("Roboto",24))
        book_id.grid(row=0,column=1,rowspan=1,columnspan=1,sticky="nsew",padx=(40,80),pady=(20,20))
        book_id_entry=ctk.CTkEntry(frame_forframe,placeholder_text="Enter Book id", fg_color="#FFFFFF", corner_radius=20,placeholder_text_color="#7E7E7E")
        book_id_entry.grid(row=0,column=2,rowspan=1,columnspan=5,sticky="nsew",padx=(40,80),pady=(20,20))
        book_id_entry.bind("<Return>", removingbook)
        errorlabel=ctk.CTkLabel(frame_forframe,fg_color='#F5F5F5',bg_color="#F5F5F5",text="")
        errorlabel.grid(row=4,column=2,columnspan=4)


def issue_return(root, Issue_Return_button):
    book_id_entry=None
    user_email_entry=None
    borrow_date_entry=None
    return_date_entry=None
    status_label=ctk.CTkLabel(frame_forframe,text="")
    status_label.grid(row=8, column=1, rowspan=1, columnspan=7, sticky="nsew")

    def get_user_id(user_email):
        query = "SELECT user_id FROM users WHERE email = %s"
        cursor.execute(query, (user_email,))
        result = cursor.fetchone()
        if result:
            return result['user_id']   
        else:
            return None

    def update_borrowed_returned_status(button_pressed):
        nonlocal book_id_entry,user_email_entry,borrow_date_entry,return_date_entry
        status_dict = {
            'issue': 1,
            'reserve': 3,
            'return': 2,
            'cancelled': 2
        }
        book_id = book_id_entry.get()
        user_email = user_email_entry.get() if button_pressed in ['issue', 'reserve'] else None


        query = "SELECT status_id, user_id FROM borrowedreturned WHERE book_id = %s"
        cursor.execute(query, (book_id,))
        result = cursor.fetchone()

        if result:
            status = result['status_id']
            user_id2=result['user_id']

            if button_pressed == 'issue':
                if status == 1:
                    print("1")

                    status_label = ctk.CTkLabel(frame_forframe, fg_color="#cc0000", bg_color="#F5F5F5", text="The book is already issued.", font=("Roboto", 24))
                elif status == 3:
                    if user_id2==get_user_id(user_email_entry.get()):
                        query = "UPDATE borrowedreturned SET  Borrowdate = %s, Returndate = %s,status_id=1 WHERE book_id = %s"
                        cursor.execute(query, ( borrow_date_entry.get(), return_date_entry.get(), book_id))

                        conn.commit()
                        status_label = ctk.CTkLabel(frame_forframe, fg_color="#cc0000", bg_color="#F5F5F5", text="Book issued successfully.", font=("Roboto", 24))
                    else:

                        status_label = ctk.CTkLabel(frame_forframe, fg_color="#cc0000", bg_color="#F5F5F5", text="The book is reserved by another user.", font=("Roboto", 24))
                elif status == 2:

                    query = "UPDATE borrowedreturned SET user_id = %s, Borrowdate = %s, Returndate = %s,status_id=1 WHERE book_id = %s"
                    cursor.execute(query, (get_user_id(user_email), borrow_date_entry.get(), return_date_entry.get(), book_id))
                    conn.commit()

                    status_label = ctk.CTkLabel(frame_forframe, fg_color="#cc0000", bg_color="#F5F5F5", text="Book issued successfully.", font=("Roboto", 24))

            elif button_pressed=='reserve':
                if status == 1:

                    status_label = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="The book is already issued.", font=("Roboto", 24))
                elif status == 3:

                        status_label = ctk.CTkLabel(frame_forframe, fg_color="#cc0000", bg_color="#F5F5F5", text="The book is reserved by another user.", font=("Roboto", 24))
            elif button_pressed=='return':
                if status==1:
                    cursor.execute("UPDATE status_id FROM borrowedreturn WHERE book_id=%s",book_id_entry.get())
            elif button_pressed=='cancel':
                if status==3:
                    cursor.execute("UPDATE  status_id FROM borrowedreturn WHERE book_id=%s",book_id_entry.get())
        else:
                print("testing")

                query = f"""
INSERT INTO borrowedreturned (Borrowdate, Returndate,book_id,user_id,status_id) 
VALUES (%s, %s, %s, %s, {status_dict[button_pressed]})
"""
                

                cursor.execute(query, ( borrow_date_entry.get(), return_date_entry.get(),book_id, get_user_id(user_email),))
                conn.commit()          
                print(book_id_entry.get())
                

                status_label = ctk.CTkLabel(frame_forframe, fg_color="#cc0000", bg_color="#F5F5F5", text="Book issued successfully.", font=("Roboto", 24))
   
    for widget in frame_forframe.winfo_children():
        widget.destroy()
    reset_button_colors()
    Issue_Return_button.configure(fg_color="#008B8B", text_color="#FFFFFF")

    issue_button = ctk.CTkButton(frame_forframe, text="Issue Book", text_color="#7E7E7E", fg_color="#24a0ed",command=lambda: create_fields('issue'))
    issue_button.grid(row=11, column=0, columnspan=2, padx=(50, 50), sticky='nsew')

    return_button = ctk.CTkButton(frame_forframe, text="Return Book", text_color="#7E7E7E", fg_color="#24a0ed",command=lambda: create_fields('return'))
    return_button.grid(row=11, column=2, columnspan=2, padx=(50, 50), sticky='nsew')

    reserve_button = ctk.CTkButton(frame_forframe, text="Reserve Book", text_color="#7E7E7E", fg_color="#24a0ed",command=lambda: create_fields('reserve'))
    reserve_button.grid(row=11, column=4, columnspan=2, padx=(50, 50), sticky='nsew')

    cancel_button = ctk.CTkButton(frame_forframe, text="Cancel Reservation", text_color="#7E7E7E", fg_color="#24a0ed",command=lambda: create_fields('cancelled'))
    cancel_button.grid(row=11, column=6, columnspan=2, padx=(50, 50), sticky='nsew')

    def create_fields(button_pressed):
        nonlocal book_id_entry,return_date_entry,borrow_date_entry,user_email_entry
        for widget in frame_forframe.winfo_children():
            if widget not in [issue_button,return_button,reserve_button,cancel_button,status_label] :
                widget.destroy()
        if button_pressed in ['issue', 'reserve']:
            book_id = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="Book ID:", font=("Roboto", 24))
            book_id.grid(row=1, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
            book_id_entry = ctk.CTkEntry(frame_forframe, placeholder_text="Enter Book id", fg_color="#FFFFFF", corner_radius=20, placeholder_text_color="#7E7E7E")
            book_id_entry.grid(row=1, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))

            user_email = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="User email:", font=("Roboto", 24))
            user_email.grid(row=2, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
            user_email_entry = ctk.CTkEntry(frame_forframe, placeholder_text="Enter User email", fg_color="#FFFFFF", corner_radius=20, placeholder_text_color="#7E7E7E")
            user_email_entry.grid(row=2, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))

            borrow_date = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="Borrow Date:", font=("Roboto", 24))
            borrow_date.grid(row=3, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
            borrow_date_entry = ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20, placeholder_text="Enter borrow date", placeholder_text_color="#7E7E7E")
            borrow_date_entry.grid(row=3, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))

            return_date = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="Return Date:", font=("Roboto", 24))
            return_date.grid(row=4, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
            return_date_entry = ctk.CTkEntry(frame_forframe, fg_color="#FFFFFF", corner_radius=20, placeholder_text="Enter Return Date", placeholder_text_color="#7E7E7E")
            return_date_entry.grid(row=4, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))

            return_date_entry.bind('<Return>', lambda event: update_borrowed_returned_status(button_pressed) if book_id_entry.get() and user_email_entry.get() and borrow_date_entry.get() and return_date_entry.get() else None)
        elif button_pressed in ['return', 'cancelled']:
            book_id = ctk.CTkLabel(frame_forframe, fg_color="#FFFFFF", bg_color="#F5F5F5", text="Book ID:", font=("Roboto", 24))
            book_id.grid(row=1, column=1, rowspan=1, columnspan=1, sticky="nsew", padx=(40, 80), pady=(20, 20))
            book_id_entry = ctk.CTkEntry(frame_forframe, placeholder_text="Enter Book id", fg_color="#FFFFFF", corner_radius=20, placeholder_text_color="#7E7E7E")
            book_id_entry.grid(row=1, column=2, rowspan=1, columnspan=5, sticky="nsew", padx=(40, 80), pady=(20, 20))

            book_id_entry.bind('<Return>', lambda event: update_borrowed_returned_status(button_pressed) if book_id_entry.get() else None)



def frames(root):
    global topframe,dashboard_button,frame_forframe,addbook_button,removebook_button,Issue_Return_button,dashboard_img,addbook_img,removebook_img,addcategory_button
    n = 20
    k = 10

    for i in range(n):
        root.grid_rowconfigure(i, weight=1, minsize=20)
    for j in range(k):
        root.grid_columnconfigure(j, weight=1, minsize=20)

    
    frame_forframe=ctk.CTkFrame(root,fg_color="#F5F5F5")
    frame_forframe.grid(row=1,rowspan=n,column=2,columnspan=10,sticky="nsew",padx=(10,10),pady=(30,20))
    topframe=ctk.CTkFrame(root,height=50,fg_color="#FFFFFF")
    topframe.grid(row=0,column=0,rowspan=n,columnspan=k,sticky="new",padx=(1,1),pady=(1,1))
    
    sidebar=ctk.CTkFrame(root,fg_color="#FFFFFF",width=300)
    sidebar.grid(row=0,column=0,rowspan=n,columnspan=2,sticky="nsew",pady=(52,1),padx=(0,10))
    for l in range(10):
        sidebar.grid_rowconfigure(l,weight=1,minsize=20)
    
    
    def addingnewcategories(addcategory_button):
        for widget in frame_forframe.winfo_children():
            widget.destroy()
        reset_button_colors()
        for i in range(18):
            frame_forframe.grid_rowconfigure(i,weight=1)
        for j in range(8):
            frame_forframe.grid_columnconfigure(j,weight=1)
        
        addcategory_button.configure(fg_color="#008B8B",text_color="#FFFFFF")
        addnewcat(frame_forframe)
    
    dashboard_img=PIL.Image.open("photos/icons8-dashboard-24.png")
    dashboard_img=ctk.CTkImage(dark_image=dashboard_img,light_image=dashboard_img,size=(17,17))
    dashboard_button = ctk.CTkButton(sidebar, image=dashboard_img,compound="left",text="Dashboard",text_color="#7E7E7E", command=lambda: dashboard(root,dashboard_button),fg_color="#FFFFFF",corner_radius=20,width=200,height=40)
    dashboard_button.grid(row=1,columnspan=3,column=0,padx=(40,0), sticky="ew")

    addbook_img=PIL.Image.open("photos\icons8-book-50.png")
    addbook_img=ctk.CTkImage(dark_image=addbook_img,light_image=addbook_img,size=(17,17))
    addbook_button=ctk.CTkButton(sidebar,image=addbook_img,compound="left",text="Add Book",text_color="#7E7E7E",fg_color="#FFFFFF",corner_radius=20,height=40,command=lambda: addbook(root,addbook_button))
    addbook_button.grid(row=2,columnspan=3,column=0,padx=(40,0),sticky="ew")
    

    removebook_img=PIL.Image.open("photos\icons8-remove-book-50.png")
    removebook_img=ctk.CTkImage(dark_image=removebook_img,light_image=removebook_img,size=(17,17))
    removebook_button=ctk.CTkButton(sidebar,image=removebook_img,command=lambda: removebook(root,removebook_button),text="Remove Book",text_color="#7E7E7E",fg_color="#FFFFFF",corner_radius=20,height=40)
    removebook_button.grid(row=3,columnspan=3,column=0,padx=(40,0),sticky="ew")

    
    
    Issue_Return_button=ctk.CTkButton(sidebar,command=lambda: issue_return(root,Issue_Return_button),text="Issue/Return Book",text_color="#7E7E7E",fg_color="#FFFFFF",corner_radius=20,height=40)
    Issue_Return_button.grid(row=4,columnspan=3,column=0,padx=(40,0),sticky="ew")

    addcategory_button=ctk.CTkButton(sidebar,text="Add new Image/language/author",compound='left',text_color="#7E7E7E",fg_color="#FFFFFF",corner_radius=20,height=40,command= lambda: addingnewcategories(addcategory_button))
    addcategory_button.grid(row=5,columns=3,column=0,padx=(40,0),sticky="ew")



def admin_widgets(root,name):
    topframe_widgets(root,name)
    dashboard(root,dashboard_button)
def open_admin_dashboard(rname):
    global name
    name=rname
    app_width = 1000
    app_height = 500
    root=setup_window()
    center_window(root, app_width, app_height)
    frames(root)  
    admin_widgets(root,name)
    root.mainloop()
    
if __name__ == "__main__":
    open_admin_dashboard("apple")
