'''
paper.data.scripts.move_files

moves files and updates database with new host and path

author | Immanuel Washington

Functions
---------
exist_check | checks to see if files to be moved all exist in database
set_move_table | updates database with moved file status
move_files | parses list of files then moves them
parse | parse command line input
'''
from __future__ import print_function
import os
import argparse
import datetime
import glob
import socket
import shutil
import uuid
import paper as ppdata
from paper.data import dbi as pdbi, file_data

def exist_check(s, source_host, source_paths):
    '''
    checks if file(s) is(are) in database

    Parameters
    ----------
    s | object: session object
    source_host | str: host of files
    source_paths | list[str]: uv* file paths

    Returns
    -------
    bool: are all files in the database
    '''
    table = pdbi.File
    FILEs = s.query(table).filter_by(host=source_host).all()
    paths = tuple(os.path.join(FILE.path, FILE.filename) for FILE in FILEs)

    return all(source_path in paths for source_path in source_paths)

def set_move_table(s, source_host, source_path, dest_host, dest_path):
    '''
    updates table for moved file

    Parameters
    ----------
    s | object: session object
    source_host | str: user host
    source_path | str: source file path
    dest_host | str: output host
    dest_path | str: output directory
    '''
    source = ':'.join((source_host, source_path))
    timestamp = datetime.datetime.utcnow()
    FILE = s.query(pdbi.File).get(source)
    move_dict = {'host': dest_host,
                 'base_path': dest_path,
                 'timestamp': timestamp}
    for field, value in move_dict.items():
        setattr(FILE, field, value)

    log_data = {'action': 'move',
                'table': 'File',
                'identifier': FILE.source,
                'log_id': str(uuid.uuid4()),
                'timestamp': timestamp}
    s.add(pdbi.Log(**log_data))

def move_files(s, source_host, source_paths_str, dest_host, dest_path, username, password):
    '''
    move files by rsyncing them and checking md5sum through rsync option

    Parameters
    ----------
    s | object: session object
    source_host | str: file host
    source_paths_str | str: file paths 
    dest_host | str: output host 
    dest_path | str: output directory 
    username | str: username 
    password | str: password 
    '''
    source_host, source_paths = file_data.parse_sources(source_host, source_paths_str,
                                                        username, password)

    is_existent = exist_check(source_host, source_paths)
    if not is_existent:
        print('File(s) not in database')
        return

    destination = ':'.join((dest_host, dest_path))
    if source_host == socket.gethostname():
        for source_path in source_paths:
            ppdata.rsync_copy(source_path, destination)
            set_move_table(s, source_host, source_path, dest_host, dest_path)
            shutil.rmtree(source_path)
    else:
        with ppdata.ssh_scope(source_host, username, password) as ssh:
            for source_path in source_paths:
                rsync_copy_command = '''rsync -ac {source_path} {destination}'''.format(source_path=source_path, destination=destination)
                rsync_del_command = '''rm -r {source_path}'''.format(source_path=source_path)
                ssh.exec_command(rsync_copy_command)
                set_move_table(s, source_host, source_path, dest_host, dest_path)
                ssh.exec_command(rsync_del_command)
    print('Completed transfer')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Move files, update database')
    parser.add_argument('--source_host', type=str, help='source host')
    parser.add_argument('--source_path', type=str, help='source path')
    parser.add_argument('--dest_host', type=str, help='destination host')
    parser.add_argument('--dest_path', type=str, help='destination path')
    parser.add_argument('--uname', type=str, help='host username')
    parser.add_argument('--pword', type=str, help='host password')

    args = parser.parse_args()

    source_host = pdbi.hostnames.get(args.source_host, args.source_host)
    dest_host = pdbi.hostnames.get(args.dest_host, args.dest_host)

    dbi = pdbi.DataBaseInterface()
    move_files(s,
               source_host=source_host, source_paths_str=args.source_path,
               dest_host=dest_host, dest_path=args.dest_path,
               username=args.uname, password=args.pword)
