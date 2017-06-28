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
# todir = todir.lstrip('/').rstrip('/')
# todirs = todir.split('/')
# todirs.reverse()

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
    pass
#_______________________________________________________________________________
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    pass
# ______________________________________________________________________________
def to_folder(tdir):
    i = 0
    j = 0
    folders = []
    unfolders =[]


    parentfolder = []
    parent_folder = []

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v2', http=http)
    results_folder = service.files().list(q="mimeType='application/vnd.google-apps.folder'").execute()
    folders_list = results_folder.get('items', [])


    to_dir = tdir.lstrip('/').rstrip('/').split('/')
    # to_dir.reverse()


    for tdir in to_dir:
        for folder in folders_list:
            if tdir == folder['title']:
                folders.append([folder['title'], folder['id'], folder['parents'][0]['id'], folder['parents'][0]['isRoot']])

    for folder in folders:
        if not folder in unfolders:
            unfolders.append(folder)
        pass

    for folder in unfolders:
        if (to_dir[0] == folder[0]) and (folder[3] == True):
            parentfolder.append(folder)
            del(unfolders[i])
        i+=1
        pass
    while len(unfolders) > 1:
        print(unfolders[j])
        del(unfolders[j])
        j+=1
        pass


    # print(unfolders)
                                                                                #
                                                                                #     for folder in unfolders:
                                                                                #         if (to_dir[0] == folder[0]) and (folder[3] == True):
                                                                                #             parentfolder.append(folder)
                                                                                #             del(unfolders[i])
                                                                                #         i+=1
                                                                                #
                                                                                #     while unfolders:
                                                                                #         if folder[2] == folders[i][1]:
                                                                                #             parentfolder.append(folder[1])
                                                                                #
                                                                                #     print(unfolders)
                                                                                #     print(parentfolder)
                                                                                #
                                                                                # [u'library', u'0B65HPGQlYSl2aWtVb2I5emxvVFU', u'0AK5HPGQlYSl2Uk9PVA'],
                                                                                # [u'123', u'0B65HPGQlYSl2bktZNkVYNS1iaEk', u'0B65HPGQlYSl2RGpHdmNGY0d0cnc'],
                                                                                # [u'123', u'0B65HPGQlYSl2RGpHdmNGY0d0cnc', u'0B65HPGQlYSl2aWtVb2I5emxvVFU']

    # for folder in folders:
    #     i += 1
    #     if len(folders) > i:
    #          if folder[2] == folders[i][1]:
    #              parentfolder.append(folder[1])
    #     else:
    #         if folders[i - 1][1] == folder[1]:
    #             parentfolder.append(folder[1])
    #
    # for pfolder in parentfolder:
    #     for folder in folders_list:
    #         if pfolder == folder['id']:
    #             parent_folder.append(folder['title'])
    #
    # if tdir == parent_folder:
    #     folderid = parentfolder[0]
    # else:
    #     folderid = ''
    #
    #
    # print(tdir)
    # print(parent_folder)
    pass

to_folder(todir)
# ______________________________________________________________________________

def main():
    # credentials = get_credentials()
    # http = credentials.authorize(httplib2.Http())
    # service = build('drive', 'v2', http=http)
    # results = service.files().list().execute()
    # # results = service.files().list(q="mimeType='application/vnd.google-apps.folder'").execute()
    # items = results.get('items', [])
    #
    # for result in items:
    #     print(result['title'])
    #     pass
    pass
    # now = datetime.now()
    # credentials = get_credentials()
    # http = credentials.authorize(httplib2.Http())
    # service = build('drive', 'v2', http=http)
    # results = service.files().list().execute()
    # items = results.get('items', [])
    # mime = magic.Magic(mime=True)
    #
    # filestobackup = []
    # folderindrive = []
    # itemtitle = []
    # gfiles = []
    # log = []
    # folderid = ''
# ______________________________________________________________________________
    # folders = []
    # parentfolder = []
    # parent_folder = []
    # t_dir = []
    # i = 0
    #
    # for tdir in todirs:
    #     for item in items:
    #         if item['mimeType'] == 'application/vnd.google-apps.folder':
    #             if tdir == item['title']:
    #                 folders.append([item['title'], item['id'], item['parents'][0]['id']])
    # for folder in folders:
    #     i += 1
    #     if len(folders) > i:
    #          if folder[2] == folders[i][1]:
    #              parentfolder.append(folder[1])
    #     else:
    #         if folders[i - 1][1] == folder[1]:
    #             parentfolder.append(folder[1])
    #
    # for pfolder in parentfolder:
    #     for item in items:
    #         if pfolder == item['id']:
    #             parent_folder.append(item['title'])
    #
    # if todirs == parent_folder:
    #     folderid = parentfolder[0]
    # else:
    #     folderid = ''
# ______________________________________________________________________________
    # if not backupdir:
    #             log.append(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' ' + 'unset folder, use -d /folder to define the folder')
    # else:
    # 	backupfiles = []
    # 	for fname in os.listdir(backupdir):
    #         path = os.path.join(backupdir, fname)
    #         if not os.path.isdir(path):
    #                 backupfiles.append(fname)
    #     if not backupfiles:
    #                     log.append(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' ' + 'empty folder')
    #     else:
    #         for item in items:
    #             if not item['mimeType'] == 'application/vnd.google-apps.folder':
    #                 if item['parents'][0]['id'] == folderid:
    #                     if item['labels']['trashed'] == False:
    #                         gfiles.append(item['title'])
    #
    #         for backupfile in backupfiles:
    #             if not backupfile in gfiles:
    #                 filestobackup.append(backupfile)
#_______________________________________________________________________________
    # md5files = []
    # if mdf:
    #     if filestobackup:
    #         for backupfile in filestobackup:
    #             md5_file = open(backupdir + '/' + backupfile + '.md5', 'w')
    #             md5_file.write(md5(backupdir + '/' + backupfile))
    #             md5_file.close()
    #             md5files.append(backupfile + '.md5')
    #     filesandmd5 = md5files + filestobackup
    # else:
    #     filesandmd5 = filestobackup
#_______________________________________________________________________________
    # if not folderid and todir:
    #             log.append(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' ' + 'no such folders on google drive! create one or use one of the existing')
    # else:
    #     if filesandmd5:
    #         for backupfile in filesandmd5:
    #             need_upload = backupdir + '/' + backupfile
    #             url = urllib.pathname2url(need_upload)
    #             file_mime = mime.from_file(need_upload)
    #             if folderid:
    #                 file_metadata = {'title' : backupfile,'parents': [ folderid ]}
    #             else:
    #                 file_metadata = {'title' : backupfile}
    #             fmedia = MediaFileUpload(need_upload, chunksize=CHUNKSIZE, resumable=True, mimetype=file_mime)
    #             ufile = service.files().insert(body=file_metadata,media_body=fmedia).execute()
    #             logfile = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' ' + backupdir + '/' + backupfile + ' > ' + todirlog
    #             zfile = service.files().get(fileId=ufile.get('id')).execute()
    #             if zfile['md5Checksum'] == md5(need_upload):
    #                 log.append(logfile + ' (md5 sums identical file transferred successfully)')
    #             else:
    #                 log.append(logfile + ' (md5 sums are not identical, the file transferred successfully)')
    #     else:
    #         log.append(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' ' + 'all files already on google drive')
    # if md5files:
    #     for md5file in md5files:
    #         os.unlink(backupdir + '/' + md5file)
# ______________________________________________________________________________
    # for logs in log:
    #     print(logs)
    #     logging.info(logs)
    #     drivelog = open('sqltogdrive.log', 'a')
    #     drivelog.write(logs + '\n')
    #     drivelog.close()
# ______________________________________________________________________________
if __name__ == '__main__':
    main()
