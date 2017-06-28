#!/usr/bin/python
# -*- coding: utf-8 -*-

    # sudo apt install python-pip
    # sudo apt install python-magic
    # pip install httplib2
    # pip install --upgrade google-api-python-client

from __future__ import print_function
import httplib2
import logging
import hashlib
import urllib
import magic
import time
import os

from apiclient.http import MediaFileUpload
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client import client
from apiclient import discovery
from oauth2client import tools
from datetime import datetime
# ______________________________________________________________________________
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser])
    flags.add_argument ('-g', '--gdrive', default='')
    flags.add_argument ('-d', '--dir', default='')
    flags.add_argument ('-m', '--md5', action='store_const', const=True)
    flags.parse_args()
except ImportError:
    flags = None
# ______________________________________________________________________________
logging.basicConfig(filename='sqltogdrive_all.log',level=logging.DEBUG)
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'backup database'
backupdir = flags.parse_args().dir
todir = flags.parse_args().gdrive
todirlog = todir
mdf = flags.parse_args().md5
todir = todir.lstrip('/').rstrip('/')
todirs = todir.split('/')
todirs.reverse()

CHUNKSIZE = 2 * 1024 * 1024
# ______________________________________________________________________________
def get_credentials():
    home_dir = os.path.expanduser('~')
    #credential_dir = os.path.join(home_dir, '.credentials')
    credential_dir = os.path.join('.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sqltodrive.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
#_______________________________________________________________________________
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
# ______________________________________________________________________________
def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v2', http=http)
    results = service.files().list(q="mimeType='application/vnd.google-apps.folder'").execute()
    items = results.get('items', [])
    # items = results.get('files', [])
    # mime = magic.Magic(mime=True)
    # drive_service = build('drive', 'v3', http=http)


    for result in items:
        print(result['title'])
        pass

# ______________________________________________________________________________
if __name__ == '__main__':
    main()
