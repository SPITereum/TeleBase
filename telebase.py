from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Treeview, Progressbar
from PIL import ImageTk, Image

import sqlite3

from pyrogram import Client

import os
from datetime import datetime
from tqdm import tqdm

from threading import Thread

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


class MainWindow(Tk):
    def __init__(self, telegram_app, chat_id):
        super().__init__()

        self.geometry('280x120')
        self.title('TeleBase')
        self.iconbitmap('.\\gui\\icon\\telebase.ico')
        self.items = None

        self.app = telegram_app
        self.chat = chat_id

        Label(self, text='Single file have to be less than 1.5GB', font=('Roboto', 10), pady=10).grid(column=0, row=0,
                                                                                                      columnspan=2)

        self.up_leave_image = ImageTk.PhotoImage(file='.\\gui\\button\\upload_button.png')
        self.up_hover_image = ImageTk.PhotoImage(file='.\\gui\\button\\upload_button_pressed.png')

        self.uploadButton = Button(self, command=self.select_files, height=50, width=120, image=self.up_leave_image, bd=0)
        self.uploadButton.grid(column=0, row=1, padx=10)
        self.uploadButton.bind('<Enter>', lambda event: self.button_hover(event, button='uploadButton'))
        self.uploadButton.bind('<Leave>', lambda event: self.button_leave(event, button='uploadButton'))

        self.do_leave_image = ImageTk.PhotoImage(file='.\\gui\\button\\download_button.png')
        self.do_hover_image = ImageTk.PhotoImage(file='.\\gui\\button\\download_button_pressed.png')

        self.downloadButton = Button(self, command=self.show_files, height=50, width=120, image=self.do_leave_image, bd=0)
        self.downloadButton.grid(column=1, row=1)
        self.downloadButton.bind('<Enter>', lambda event: self.button_hover(event, button='downloadButton'))
        self.downloadButton.bind('<Leave>', lambda event: self.button_leave(event, button='downloadButton'))

        self.upload_bar = Progressbar(self, orient=HORIZONTAL, length=120, mode='determinate')
        self.upload_bar.grid(column=0, row=2, pady=3)
        self.upload_bar['maximum'] = 100

        self.mainloop()

    def button_hover(self, event, button):
        if button == 'uploadButton':
            self.uploadButton.configure(image=self.up_hover_image)
        elif button == 'downloadButton':
            self.downloadButton.configure(image=self.do_hover_image)

    def button_leave(self, event, button):
        if button == 'uploadButton':
            self.uploadButton.configure(image=self.up_leave_image)
        elif button == 'downloadButton':
            self.downloadButton.configure(image=self.do_leave_image)

    # User Visualization
    def select_files(self):
        self.items = filedialog.askopenfilenames(initialdir='./',
                                                 title='Select Files',
                                                 filetype=(('All Files', '*.*'),))
        # File Uploading
        uploader = UploadThread(self, self.app, self.chat, self.items)
        uploader.start()

    def show_files(self):
        show = ShowWindow(app, chat)


class UploadThread(Thread):
    def __init__(self, main_frame, client, chat_id, to_upload):
        super().__init__()

        self.main_frame = main_frame
        self.app = client
        self.chat_id = chat_id
        self.files = to_upload

        self.conn = None
        self.c = None

    def progress(self, current, total):
        self.main_frame.upload_bar['value'] = int(current * 100 / total)

    def run(self):

        self.conn = sqlite3.connect('references.db')
        self.c = self.conn.cursor()

        for file in self.files:
            msg = app.send_document(self.chat_id, file, progress=self.progress)

            # Referencing in Database
            self.c.execute("""INSERT INTO files VALUES(:name, :id, :time);""",
                           {
                               'name': file.split('/')[-1],
                               'id': int(msg['message_id']),
                               'time': datetime.now()
                            })
            self.conn.commit()

        self.main_frame.upload_bar['value'] = 0

        self.conn.close()


class ShowWindow(Tk):

    def __init__(self, telegram_app, chat_id):
        super().__init__()

        self.app = telegram_app
        self.chat_id = chat_id

        self.title('Showing')
        self.geometry('550x300')
        self.iconbitmap('.\\gui\\icon\\telebase.ico')

        Label(self, text='Double Click A Item to Download It').pack()
        Label(self, text='MultiSelect Items and Press Button to Download It').pack()
        Button(self, text='Refresh List', command=self.refresh_tree).pack()

        self.treeview = Treeview(self)
        self.treeview['columns'] = ('one', 'two')

        self.treeview.column('#0', width=80, minwidth=70)
        self.treeview.column('one', width=300, minwidth=200)
        self.treeview.column('two', width=150, minwidth=50)

        self.treeview.heading('#0', text='TelegramID')
        self.treeview.heading('one', text='Name')
        self.treeview.heading('two', text='Upload Date')
        self.treeview.pack()

        self.refresh_tree()

        self.treeview.bind('<Double-Button-1>', self.download)
        Button(self, text='Download It', command=self.multi_download, padx=20).pack(side=LEFT)

        Button(self, text='Delete Selected', command=self.delete, padx=20).pack(side=RIGHT)

        self.download_bar = Progressbar(self, orient=HORIZONTAL, length=280, mode='determinate')
        self.download_bar.pack(pady=3)
        self.download_bar['maximum'] = 100

        self.mainloop()
        conn.close()

    def delete(self):
        selected = self.treeview.selection()
        for identifier in selected:
            item = self.treeview.item(identifier)
            telegram_id = int(item['text'])
            self.app.delete_messages(self.chat_id, telegram_id)

            c.execute("""
                DELETE FROM files
                WHERE Tid = :id
            """, {'id': telegram_id})

            conn.commit()

        self.refresh_tree()

    def refresh_tree(self):

        for child in self.treeview.get_children():
            self.treeview.delete(child)

        c.execute("""
            SELECT * FROM files;
        """)

        conn.commit()

        for row in c.fetchall():
            self.treeview.insert('', 0, text=row[1], values=(row[0], row[2]))

    def download(self, event):
        item = self.treeview.item(self.treeview.selection())

        downloader = DownloaderThread(self, self.app, self.chat_id, [item])
        downloader.start()

    def multi_download(self):

        items = []

        selected = self.treeview.selection()
        for identifier in selected:
            
            item = self.treeview.item(identifier)

            items.append(item)

        downloader = DownloaderThread(self, self.app, self.chat_id, items)
        downloader.start()


class DownloaderThread(Thread):
    def __init__(self, showing_frame, client, chat_id, to_download):
        super().__init__()

        self.show_frame = showing_frame
        self.app = client
        self.chat_id = chat_id
        self.files = to_download

    def progress(self, current, total):
        self.show_frame.download_bar['value'] = int(current * 100 / total)

    def run(self):
        for file in self.files:
            self.app.download_media(self.app.get_messages(self.chat_id, int(file['text'])), progress=self.progress)

        self.show_frame.download_bar['value'] = 0


root = MainWindow(app, chat)
conn.close()
app.stop()

