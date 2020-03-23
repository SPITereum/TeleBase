from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Treeview, Progressbar
from PIL import ImageTk, Image

import sqlite3

from pyrogram import Client
import webbrowser

import os
from datetime import datetime
import subprocess

from threading import Thread

# Initializing Telegram Client
api_id = API_ID_HERE
api_hash = 'API_HASH_HERE'
chat = 'Public or Private Channel ID'

# Generate Link, based on chat type (Private or Public) [Used on Database]
telegram_url = ''
if type(chat) == int:
    telegram_url = 'https://t.me/c/' + str(chat)[4:] + '/'
elif type(chat) == str:
    telegram_url = 'https://t.me/' + str(chat) + '/'

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
        FileName TEXT,
        TelegramID INTEGER PRIMARY KEY,
        UploadTime TEXT,
        TelegramLink TEXT,
        FileDimension TEXT,
        FileType TEXT
        );
    """)
    conn.commit()


class MainWindow(Tk):
    def __init__(self, telegram_app, chat_id):
        super().__init__()

        self.geometry('280x170')
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

        self.status_up_text = Label(self, text='Upload Progress...')
        self.status_up_text.grid(row=2, column=0, padx=2)

        self.status_up_number = Label(self, fg='green')
        self.status_up_number.grid(row=2, column=1, sticky=NW)

        self.status_up_byte = Label(self, fg='green')
        self.status_up_byte.grid(row=4, column=0, columnspan=2)

        self.upload_bar = Progressbar(self, orient=HORIZONTAL, length=250, mode='determinate')
        self.upload_bar.grid(column=0, row=3, padx=12, pady=3, columnspan=2)
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

    def calculate_file_size(self, size):
        size = ((size/1024)/1024)/1024  # Gibibyte Value

        if int(size) != 0:  # Is GiB Size?
            return str(round(size, 2)) + ' GiB'
        size = size*1024
        if int(size) != 0:  # Is MiB Size?
            return str(round(size, 2)) + ' MiB'
        size = size*1024
        if int(size) != 0:  # Is KiB Size?
            return str(round(size, 2)) + ' KiB'
        return str(round(size, 2)) + 'B'

    def progress(self, current, total):
        self.main_frame.upload_bar['value'] = int(current * 100 / total)

        self.main_frame.status_up_byte.config(text=self.calculate_file_size(current) + ' / ' + self.calculate_file_size(total))


    def run(self):

        self.conn = sqlite3.connect('references.db')
        self.c = self.conn.cursor()

        file_num = str(len(self.files))
        self.main_frame.status_up_number.config(text='0/' + file_num)

        count_file = 1
        for file in self.files:
            self.main_frame.status_up_number.config(text=str(count_file) + '/' + file_num)

            msg = app.send_document(self.chat_id, file, progress=self.progress)

            count_file += 1

            # Referencing in Database
            try:
                self.c.execute("""INSERT INTO files VALUES(:name, :id, :time, :link, :file_dim, :file_type);""",
                               {
                                   'name': file.split('/')[-1],
                                   'id': int(msg['message_id']),
                                   'time': datetime.now(),
                                   'link': telegram_url + str(msg['message_id']),
                                   'file_dim': str(msg['document']['file_size']),
                                   'file_type': msg['document']['mime_type']
                                })
                self.conn.commit()
            except TypeError:
                if msg['audio']:
                    self.c.execute("""INSERT INTO files VALUES(:name, :id, :time, :link, :file_dim, :file_type);""",
                                   {
                                       'name': file.split('/')[-1],
                                       'id': int(msg['message_id']),
                                       'time': datetime.now(),
                                       'link': telegram_url + str(msg['message_id']),
                                       'file_dim': str(msg['audio']['file_size']),
                                       'file_type': msg['audio']['mime_type']
                                   })
                    self.conn.commit()
                else:
                    self.c.execute("""INSERT INTO files(FileName, TelegramID, UploadTime, TelegramLink) 
                                                            VALUES(:name, :id, :time, :link);""",
                                   {
                                       'name': file.split('/')[-1],
                                       'id': int(msg['message_id']),
                                       'time': datetime.now(),
                                       'link': telegram_url + str(msg['message_id'])
                                   })
                    self.conn.commit()

        self.main_frame.status_up_number.config(text='')
        self.main_frame.status_up_byte.config(text='')
        self.main_frame.upload_bar['value'] = 0

        self.conn.close()


class ShowWindow(Tk):

    def __init__(self, telegram_app, chat_id):
        super().__init__()

        self.app = telegram_app
        self.chat_id = chat_id

        self.title('Showing')
        self.geometry('473x365')
        self.iconbitmap('.\\gui\\icon\\telebase.ico')

        Label(self, text='Double Click A Item to Download It\n'
                         'MultiSelect Items and Press Button to Download It').grid(row=0, column=0, columnspan=2)
        Button(self, text='Refresh List', command=self.refresh_tree).grid(row=0, column=2)
        Button(self, text='Download Path', command=self.open_do_path).grid(row=2, column=1, sticky=W)

        self.treeview = Treeview(self)
        self.treeview['columns'] = ('one', 'two')

        self.treeview.column('#0', width=80, minwidth=70, anchor=CENTER)
        self.treeview.column('one', width=300, minwidth=200, anchor=W)
        self.treeview.column('two', width=90, minwidth=50, anchor=CENTER)

        self.treeview.heading('#0', text='TelegramID')
        self.treeview.heading('one', text='Name')
        self.treeview.heading('two', text='Size')

        self.treeview.grid(row=1, column=0, columnspan=3)

        self.refresh_tree()

        self.treeview.bind('<Double-Button-1>', self.download)
        self.treeview.bind('<Button-3>', self.popup)
        Button(self, text='Download It', command=self.multi_download, padx=20).grid(row=2, column=0, sticky=W)

        Button(self, text='Delete Selected', command=self.delete, padx=20).grid(row=2, column=2, sticky=E)

        self.download_bar = Progressbar(self, orient=HORIZONTAL, length=280, mode='determinate')
        self.download_bar.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky=SW)
        self.download_bar['maximum'] = 100

        self.status_do_text = Label(self, text='Download Progress...')
        self.status_do_text.grid(row=3, column=0, padx=2)

        self.status_do_number = Label(self, fg='green')
        self.status_do_number.grid(row=3, column=1, padx=2, sticky=NW)

        self.status_do_byte = Label(self, fg='green')
        self.status_do_byte.grid(row=5, column=0, columnspan=2)

        self.item = None

        self.popup_dx = Menu(self, tearoff=0)
        self.popup_dx.add_command(label='Copy Telegram Link', command=self.copy_telegram_link)
        self.popup_dx.add_command(label='Open Telegram Link', command=self.open_telegram_link)
        self.popup_dx.add_command(label='Show More Info', command=self.show_info)

        self.mainloop()
        conn.close()

    def show_info(self):
        c.execute("""
                            SELECT * FROM files WHERE TelegramID=:id;
                        """, {
            'id': self.treeview.item(self.item)['text']
        })

        infos = c.fetchall()

        info = Tk()
        info.geometry('400x150')
        info.title('Info File')
        info.iconbitmap('.\\gui\\icon\\telebase.ico')

        Label(info, text='Name : ').grid(row=0, column=0, sticky=W)
        Label(info, text='Telegram ID : ').grid(row=1, column=0, sticky=W)
        Label(info, text='Upload Date : ').grid(row=2, column=0, sticky=W)
        Label(info, text='Telegram Link : ').grid(row=3, column=0, sticky=W)
        Label(info, text='File Size (B) : ').grid(row=4, column=0, sticky=W)
        Label(info, text='File Type : ').grid(row=5, column=0, sticky=W)

        Label(info, text=str(infos[0][0])).grid(row=0, column=1, sticky=W)
        Label(info, text=str(infos[0][1])).grid(row=1, column=1, sticky=W)
        Label(info, text=str(infos[0][2])).grid(row=2, column=1, sticky=W)
        Label(info, text=str(infos[0][3])).grid(row=3, column=1, sticky=W)
        Label(info, text=str(infos[0][4])).grid(row=4, column=1, sticky=W)
        Label(info, text=str(infos[0][5])).grid(row=5, column=1, sticky=W)

        info.mainloop()

    def copy_telegram_link(self):
        c.execute("""
                    SELECT * FROM files WHERE TelegramID=:id;
                """, {
            'id': self.treeview.item(self.item)['text']
        })
        link = c.fetchall()[0][3]
        subprocess.Popen(['clip'], stdin=subprocess.PIPE).communicate(link.encode())

        conn.commit()

    def open_telegram_link(self):
        c.execute("""
            SELECT * FROM files WHERE TelegramID=:id;
        """, {
            'id': self.treeview.item(self.item)['text']
        })
        webbrowser.open(c.fetchall()[0][3])

        conn.commit()

    def popup(self, event):
        self.item = self.treeview.identify_row(event.y)  # Get Item from Treeview
        self.treeview.selection_set(self.item)  # Color the row of Mouse DX Pressed

        if event.y > 24:
            self.popup_dx.post(event.x_root, event.y_root)

    def delete(self):
        selected = self.treeview.selection()
        for identifier in selected:
            item = self.treeview.item(identifier)
            telegram_id = int(item['text'])
            self.app.delete_messages(self.chat_id, telegram_id)

            c.execute("""
                DELETE FROM files
                WHERE TelegramID = :id
            """, {'id': telegram_id})

            conn.commit()

        self.refresh_tree()

    def open_do_path(self):
        path = '.\\downloads'
        if os.path.exists(path):
            os.startfile(path)
        else:
            os.mkdir(path)
            os.startfile(path)

    def calculate_file_size(self, size):
        size = ((size/1024)/1024)/1024  # Gibibyte Value

        if int(size) != 0:  # Is GiB Size?
            return str(round(size, 2)) + ' GiB'
        size = size*1024
        if int(size) != 0:  # Is MiB Size?
            return str(round(size, 2)) + ' MiB'
        size = size*1024
        if int(size) != 0:  # Is KiB Size?
            return str(round(size, 2)) + ' KiB'
        return str(round(size, 2)) + 'B'

    def refresh_tree(self):

        for child in self.treeview.get_children():
            self.treeview.delete(child)

        c.execute("""
            SELECT TelegramID, FileName, FileDimension FROM files;
        """)

        conn.commit()

        for row in c.fetchall():

            size = self.calculate_file_size(int(row[2]))
            self.treeview.insert('', 0, text=row[0], values=(row[1], size))

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

    def calculate_file_size(self, size):
        size = ((size/1024)/1024)/1024  # Gibibyte Value

        if int(size) != 0:  # Is GiB Size?
            return str(round(size, 2)) + ' GiB'
        size = size*1024
        if int(size) != 0:  # Is MiB Size?
            return str(round(size, 2)) + ' MiB'
        size = size*1024
        if int(size) != 0:  # Is KiB Size?
            return str(round(size, 2)) + ' KiB'
        return str(round(size, 2)) + 'B'

    def progress(self, current, total):
        self.show_frame.download_bar['value'] = int(current * 100 / total)

        self.show_frame.status_do_byte.config(text=self.calculate_file_size(current) + ' / ' + self.calculate_file_size(total))

    def run(self):

        file_num = str(len(self.files))
        self.show_frame.status_do_number.config(text='0/' + file_num)

        count_file = 1
        for file in self.files:
            self.show_frame.status_do_number.config(text=str(count_file) + '/' + file_num)

            self.app.download_media(self.app.get_messages(self.chat_id, int(file['text'])), progress=self.progress)

            count_file += 1

        self.show_frame.status_do_number.config(text='')
        self.show_frame.status_do_byte.config(text='')
        self.show_frame.download_bar['value'] = 0


root = MainWindow(app, chat)
conn.close()
app.stop()

