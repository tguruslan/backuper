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
import time
import os

if os.name == 'nt':
    import urllib
    from mimetypes import MimeTypes
    mime = MimeTypes()
else:
    import magic
    mime = magic.Magic(mime=True)


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
mdf = flags.parse_args().md5

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
def drive_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('drive', 'v2', http=http)

    return service
    pass
# ______________________________________________________________________________
def to_folder(tdir):
    service = drive_service()
    results_folder = service.files().list(q="mimeType='application/vnd.google-apps.folder'").execute()
    folders_list = results_folder.get('items', [])

    if tdir:
        i = 0
        j = 0
        folders = []
        parentfolder = []

        to_dir = tdir.lstrip('/').rstrip('/').split('/')

        for tdir in to_dir:
            for folder in folders_list:
                if tdir == folder['title']:
                    if not ([folder['title'], folder['id'], folder['parents'][0]['id'], folder['parents'][0]['isRoot']]) in folders:
                        folders.append([folder['title'], folder['id'], folder['parents'][0]['id'], folder['parents'][0]['isRoot']])
            pass

        for folder in folders:
            if (to_dir[0] == folder[0]) and (folder[3] == True):
                parentfolder.append(folder)
                del(folders[i])
            i+=1
            pass

        while (len(parentfolder) < len(to_dir)) and (j <= (len(folders))):
            for folder in folders:
                if ((folder[2] == parentfolder[(len(parentfolder) - 1)][1]) and (folder[0] == to_dir[len(parentfolder)])):
                    parentfolder.append(folder)
                    j = 0
                else:
                    j+=1
            pass

        if len(parentfolder) == len(to_dir):
            return parentfolder[len(parentfolder) - 1][1]
        else:
            return False
            pass

    else:
        about = service.about().get().execute()
        return about['rootFolderId']
    pass

# print(to_folder(todir))
# ______________________________________________________________________________
def filestobackup(fdir):
    if not fdir:
        return '0'
    else:
    	backupfiles = []

    	for fname in os.listdir(fdir):
            path = os.path.join(fdir, fname)
            if not os.path.isdir(path):
                    backupfiles.append(fname)

        if not backupfiles:
            return '1'
        else:
            service = drive_service()
            results = service.files().list(q="parents='" + to_folder(todir) + "'").execute()
            flist = results.get('items', [])

            k = []
            filestobackup = []

            for lst in flist:
                if (lst['mimeType'] != 'application/vnd.google-apps.folder') and (lst['labels']['trashed'] == False):
                    k.append(lst['title'])
                pass

            for backupfile in backupfiles:
                if not backupfile in k:
                    filestobackup.append([fdir + '/' + backupfile, md5(fdir + '/' + backupfile)])

            return filestobackup
    pass

# print(filestobackup(backupdir))
# ______________________________________________________________________________
def up_log(to_log):
    print(to_log)
    logging.info(to_log)
    drivelog = open('sqltogdrive.log', 'a')
    drivelog.write(to_log + '\n')
    drivelog.close()

    pass
# ______________________________________________________________________________

def drive_up(upfiles):
    service = drive_service()

    for upfile in upfiles:
        backupfile = upfile[0].split('/')
        if os.name == 'nt':
            url = urllib.pathname2url(upfile[0])
            mime_type = mime.guess_type(url)
            file_mime = mime_type[0]
        else:
            file_mime = mime.from_file(upfile[0])

        folder_id = to_folder(todir)

        file_metadata = {'title' : backupfile[len(backupfile) - 1],'parents': [{ 'id': folder_id }]}
        media = MediaFileUpload(upfile[0], chunksize=CHUNKSIZE, resumable=True, mimetype=file_mime)
        request = service.files().insert(media_body=media, body=file_metadata).execute()

        logfile = datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + ' ' + upfile[0] + ' > ' + todir
        zfile = service.files().get(fileId=request.get('id')).execute()
        if zfile['md5Checksum'] == upfile[1]:
            up_log(logfile + ' (md5 sums identical file transferred successfully)')
        else:
            up_log(logfile + ' (md5 sums are not identical, the file transferred successfully)')

    pass

# drive_up(filestobackup(backupdir))
# ______________________________________________________________________________
def create_md(name_files):
    md5files = []
    for bfile in name_files:
        md5_file = open(bfile[0] + '.md5', 'w')
        md5_file.write(bfile[1])
        md5_file.close()
        md5files.append([bfile[0] + '.md5', md5(bfile[0] + '.md5')])
    return md5files
    pass
#_______________________________________________________________________________
def main():
    if mdf:
        mdfile = create_md(filestobackup(backupdir))

        drive_up(mdfile)
        for md_file in mdfile:
            os.unlink(md_file[0])
            # up_log(md_file[0] + '- removed from disk')

    if filestobackup(backupdir) == '0':
        up_log('please set source folder, use -d path_to_folder/folder_name')
    elif filestobackup(backupdir) == '1':
        up_log('In the folder there are no files which would not be on the google drive')
    else:
        drive_up(filestobackup(backupdir))

    pass
# ______________________________________________________________________________
if __name__ == '__main__':
    main()
