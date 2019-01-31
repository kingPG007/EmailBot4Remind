#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import time
import email
import base64
import poplib
import requests
import threading
import traceback
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

email = 'king1993@protonmail.com'
password = 'GP19931025'
mail_server = 'mail.protonmail.com'

bot_token = "10201787:mbds5stgmf122gCJSiOnVvWu"
chat_id = 1071283

send_msg = {}

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def auth():
    try:
        server = poplib.POP3_SSL(mail_server)
        server.user(email)
        server.pass_(password)
        msg_num, _ = server.stat()
        return server, msg_num
    except:
        sys.exit('Auth failed')

def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def get_info(msg, indent=0):
    send_msg['text'] = send_msg['attach'] = ""
    try:
        if indent == 0:
            send_msg['subject'] = ""
            for header in ['From', 'To', 'Subject']:
                value = msg.get(header, '')
                if value:
                    if header=='Subject':
                        value = decode_str(value)
                        send_msg['subject'] = value

        if (msg.is_multipart()):
            parts = msg.get_payload()
            for n, part in enumerate(parts):
                get_info(part, indent + 1)
        else:
            content_type = msg.get_content_type()
            if content_type=='text/plain' or content_type=='text/html':
                content = msg.get_payload(decode=True)
                charset = guess_charset(msg)
                if charset:
                    try:
                        content = content.decode(charset)
                    except:
                        content = content.decode('utf-8')
                send_msg['text'] = content.replace('--', '\\n')
            else:
                send_msg['attach'] = content_type
    except:
        traceback.print_exc()  

def make_message(send_msg):
    try:
        text = "@King\\n[%s]\\nking1993@protonmail.com receive a new email\\n[subject]\\n%s\\n[text]\\n%s"%(get_time(), send_msg['subject'].encode('utf-8'), send_msg['text'].encode('utf-8'))
    except:
        text = "@King\\n[%s]\\nking1993@protonmail.com receive a new email\\n[subject]\\nUnknown\\n[text]\\nSecBot send message failed, Please log in"%(get_time())
    return text

def send_message(bot_token, chat_id, text, type="msg"):
    if type == "mail":
        text = make_message(text)
    url = "https://api.potato.im:8443/%s/sendTextMessage"%(bot_token)
    headers = {
    'Content-Type':'application/json',
    }
    post_data = """{"chat_type":2,"chat_id":%d,"text":"%s"}"""%(chat_id, text)
    try:
        req = requests.post(url, post_data, headers=headers)
        if 'error_code' in str(req.content):
            post_data = """{"chat_type":2,"chat_id":%d,"text":"%s"}"""%(chat_id, '@King\\n[%s]\\nBot send message failed\\n'%(get_time()))
            req = requests.post(url, post_data, headers=headers)
    except:
        traceback.print_exc()
        try:
            post_data = """{"chat_type":2,"chat_id":%d,"text":"%s"}"""%(chat_id, '@King\\n[%s]\\nBot send message failed\\n'%(get_time()))
            req = requests.post(url, post_data, headers=headers)
        except:
            traceback.print_exc()

def get_message(bot_token):
    msg = []
    url = "https://api.potato.im:8443/%s/getUpdates"%(bot_token)
    try:
        req = requests.get(url)
        msg = req.content
        pattern = re.compile(r'"text":"(.*?)","')
        msg = pattern.findall(req.content)
    except:
        traceback.print_exc()
    return msg

def check_new_mail():
    server, msg_num_ord = auth()
    server.quit()
    msg_num_ord = msg_num_ord
    while True:
        server, msg_num = auth()
        if msg_num != msg_num_ord:
            for i in range(msg_num - msg_num_ord):
                resp, lines, octets = server.retr(msg_num_ord + 1 + i)
                msg = Parser().parsestr('\r\n'.join(lines))
                get_info(msg)
                send_message(bot_token, chat_id, send_msg, type="mail")
        msg_num_ord = msg_num
        server.quit()
        time.sleep(60)

def check_thread_status():
    while 1:
        alive = False
        for t in thread_list:
            alive = alive or t.isAlive()
        if not alive: break

if __name__ == "__main__":
    check_new_mail()
