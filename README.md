# TeleBase

A file store system based on Telegram.

## Needed Import Module

Module View

### To Install

\- [pyrogram](https://docs.pyrogram.org/) `$ pip3 install pyrogram` : MTProto Services to interface as user in Telegram

\- [tgcrypto](https://github.com/pyrogram/tgcrypto) `$ pip3 install tgcrypto` : [For Windows User], module needed for ***pyrogram***

### Preinstalled Module

\- tkinter

\- sqlite3

\- os

\- datetime

\- tqdm

## Initialize Telegram Client

~~~python
#Initializing Telegram Client
api_id = API_ID_HERE
api_hash = 'API_HASH_HERE'
chat = 'Public or Private Channel ID'
~~~

1. Get **API_ID** (int) and **API_HASH** (str) by this [telegram link](https://my.telegram.org/auth)



![](https://i.imgur.com/JAuzXxM.png)



![](https://i.imgur.com/97ASDjD.png)

2. Create Telegram **Channel** (*Public* or *Private*)

3. Get **CHAT**

   If ***Public*** : String Name without *@*

   If ***Private*** : Negative Integer. Guide on [StackOverflow](https://stackoverflow.com/questions/33858927/how-to-obtain-the-chat-id-of-a-private-telegram-channel)

4. Replace Value in **Code**

     Open **telebase.py** and replace value.

5. Now you can **use your database**

## :green_book: Features

- :pushpin: Cloud based database (**Single file less than 1.5GB** ***Telegram Limitation***)
- :pushpin: GUI Client
- :pushpin: Download File by GUI App
- :pushpin: Delete Functionality (Delete File or Files from Database)
- :pushpin: Added a Raw Progress Bar for Downloading and Uploading Files

## :closed_book: To Dos

- :pushpin: Improve GUI App
- :pushpin: Improve Showing Window Interface
- :pushpin: Add File Length in Showing Window
- :pushpin: Add File Type n Showing Window
- :pushpin: Permit to Upload File over 1.5 GB, by **splitting** them
- :pushpin: Add Folder Separation
- :pushpin: Improve Progress Bars
- :pushpin: Add Telegram Reference Link