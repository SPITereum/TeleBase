from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Treeview
from PIL import ImageTk, Image

import sqlite3

from pyrogram import Client

import os
from datetime import datetime
from tqdm import tqdm

# Initializing Telegram Client
api_id = API_ID_HERE
api_hash = 'API_HASH_HERE'
chat = 'Public or Private Channel ID'

app = Client('UserName', api_id, api_hash)
app.start()

# Initializing Database Connection and Cursor

if os.path.exists('.\\references.db'):  # Checking if database already exists...
    conn = sqlite3.connect('references.db')
    c = conn.cursor()
else:                                   # Or not.
    conn = sqlite3.connect('references.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE files (
        fName TEXT,
        TID INTEGER,
        UpTime TEXT
        );
    """)
    conn.commit()


# User Visualization
def select_files():
    root.filenames = filedialog.askopenfilenames(initialdir='./',
                                                 title='Select Files',
                                                 filetype=(('All Files', '*.*'),))
    #  File Uploading
    for nfile in tqdm(range(0, len(root.filenames)), ncols=70):
        try:
            file = root.filenames[nfile]
            msg = app.send_document(chat, file)

            # Referencing in Database
            c.execute("""INSERT INTO files VALUES(:name, :id, :time);""",
            {
                'name': file.split('/')[-1],
                'id': int(msg['message_id']),
                'time': datetime.now()
            })
            conn.commit()

        except ValueError:
            Label(root, text='File {} is larger than 1.5GB'.format(file)).pack()


def download(tree):
    """
    clicked = tree.focus()
    print(tree.item(clicked))
    for item in clicked:
        print(tree.focus(item))"""

    print(tree.selection())


def show_files():

    show = ShowWindow(app, chat)
    """
    show = Tk()
    show.title('Showing')
    show.geometry('550x300')
"""
    #c.execute("""
     #   SELECT * FROM files;
    #""")

    """scrollbary = Scrollbar(show, orient=VERTICAL)
    scrollbary.pack(side=RIGHT, fill=Y)

    scrollbarx = Scrollbar(show, orient=HORIZONTAL)
    scrollbarx.pack(side=BOTTOM, fill=X)

    listbox = Listbox(show, width=30, height=15, selectmode=MULTIPLE, xscrollcommand=scrollbarx.set, yscrollcommand=scrollbary.set)
    listbox.pack()

    scrollbarx.config(command=listbox.xview)
    scrollbary.config(command=listbox.yview)

    for row in c.fetchall():
        listbox.insert(0, (row[0], row[1]))
    
    Button(show, text='Download Selected', command=lambda: download(listbox)).pack()
    """

    """tree = Treeview(show)
    tree['columns'] = ('one', 'two')

    tree.column('#0', width=80, minwidth=70)
    tree.column('one', width=300, minwidth=200)
    tree.column('two', width=150, minwidth=50)

    tree.heading('#0', text='TelegramID')
    tree.heading('one', text='Name')
    tree.heading('two', text='Upload Date')
    tree.pack()

    for row in c.fetchall():
        tree.insert('', 0, text=row[1], values=(row[0], row[2]))
    
    tree.bind('<<TreeviewSelect>>', lambda: download(tree=tree))

    #Button(show, text='Download Selected', command=lambda: download(tree)).pack()

    conn.commit()



    show.mainloop()"""


class ShowWindow(Tk):

    def __init__(self, telegram_app, chat_id):
        Tk.__init__(self)

        self.conn = sqlite3.connect('references.db')
        self.c = self.conn.cursor()

        self.app = telegram_app
        self.chat_id = chat_id

        self.title('Showing')
        self.geometry('550x300')
        self.iconbitmap('.\\gui\\icon\\telebase.ico')

        Label(self, text='Double Click A Item to Download It').pack()
        Label(self, text='MultiSelect Items and Press Button to Download It').pack()

        self.treeview = Treeview(self)

        self.treeview['columns'] = ('one', 'two')

        self.treeview.column('#0', width=80, minwidth=70)
        self.treeview.column('one', width=300, minwidth=200)
        self.treeview.column('two', width=150, minwidth=50)

        self.treeview.heading('#0', text='TelegramID')
        self.treeview.heading('one', text='Name')
        self.treeview.heading('two', text='Upload Date')
        self.treeview.pack()

        self.update_tree()

        self.treeview.bind('<Double-Button-1>', self.download)
        Button(self, text='Download It', command=self.multi_download, padx=20).pack(side=LEFT)

        Button(self, text='Delete Selected', command=self.delete, padx=20).pack(side=RIGHT)

        self.mainloop()
        self.conn.close()

    def delete(self):
        selected = self.treeview.selection()
        for identifier in selected:
            item = self.treeview.item(identifier)
            telegram_id = int(item['text'])
            self.app.delete_messages(self.chat_id, telegram_id)

            self.c.execute("""
                DELETE FROM files
                WHERE Tid = :id
            """, {'id': telegram_id})

            self.conn.commit()
        self.update_tree()

    def update_tree(self):

        for child in self.treeview.get_children():
            self.treeview.delete(child)

        self.c.execute("""
                    SELECT * FROM files;
                """)

        self.conn.commit()

        for row in self.c.fetchall():
            self.treeview.insert('', 0, text=row[1], values=(row[0], row[2]))

    def download(self, event):
        item = self.treeview.item(self.treeview.selection())
        self.app.download_media(self.app.get_messages(self.chat_id, int(item['text'])))

    def multi_download(self):
        selected = self.treeview.selection()
        for identifier in selected:
            
            item = self.treeview.item(identifier)
            self.app.download_media(self.app.get_messages(self.chat_id, int(item['text'])))   


def button_hover(event, button):
    if button == 'uploadButton':
        uploadButton.configure(image=up_hover_image)
    elif button == 'downloadButton':
        downloadButton.configure(image=do_hover_image)


def button_leave(event, button):
    if button == 'uploadButton':
        uploadButton.configure(image=up_leave_image)
    elif button == 'downloadButton':
        downloadButton.configure(image=do_leave_image)


root = Tk()
root.geometry('280x110')
root.title('TeleBase')
root.iconbitmap('.\\gui\\icon\\telebase.ico')

Label(root, text='Single file have to be less than 1.5GB', font=('Roboto', 10), pady=10).grid(column=0, row=0, columnspan=2)

up_leave_image = ImageTk.PhotoImage(file='.\\gui\\button\\upload_button.png')
up_hover_image = ImageTk.PhotoImage(file='.\\gui\\button\\upload_button_pressed.png')

uploadButton = Button(root, command=select_files, height=50, width=120, image=up_leave_image, bd=0)
uploadButton.grid(column=0, row=1, padx=10)
uploadButton.bind('<Enter>', lambda event: button_hover(event, button='uploadButton'))
uploadButton.bind('<Leave>', lambda event: button_leave(event, button='uploadButton'))

do_leave_image = ImageTk.PhotoImage(file='.\\gui\\button\\download_button.png')
do_hover_image = ImageTk.PhotoImage(file='.\\gui\\button\\download_button_pressed.png')

downloadButton = Button(root, command=show_files, height=50, width=120, image=do_leave_image, bd=0)
downloadButton.grid(column=1, row=1)
downloadButton.bind('<Enter>', lambda event: button_hover(event, button='downloadButton'))
downloadButton.bind('<Leave>', lambda event: button_leave(event, button='downloadButton'))


root.mainloop()
conn.commit()
conn.close()
app.stop()

