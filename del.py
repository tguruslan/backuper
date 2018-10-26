import os
import argparse
import time

arg = argparse.ArgumentParser()
arg.add_argument ('-d', '--dir', default='')
arg.add_argument ('-n', '--num', default='')
arg.parse_args()

backupdir = arg.parse_args().dir
n = arg.parse_args().num
backupdir = backupdir.rstrip('/')

backupfiles = []
delete = []

for fname in os.listdir(backupdir):
    path = os.path.join(backupdir, fname)
    if not os.path.isdir(path):
        backupfiles.append(fname)

for backupfile in backupfiles:
    if not backupfile.startswith('.'):
        delete.append(time.strftime('%d%m%Y%H%M%S', time.gmtime(os.path.getmtime(backupdir + '/' + backupfile))) + ' ' + backupdir + '/' + backupfile)

delete.sort()
delete.reverse()

if n:
    n = int(n)
    i = 0
    if (len(delete) > n):
        while i < n:
            del delete[0]
            i += 1
    else:
        del delete[:]

for deletes in delete:
    files = deletes.split(' ')
    print(files[1])
    os.unlink(files[1])
