'''
paper.data.add

add info to database

author | Immanuel Washington

Functions
---------
calc_obs_info | pulls observation and file data from files
dupe_check | checks database for duplicate files
add_files_to_db | pulls file and observation data and adds to database
add_files | parses list of files and adds data to database
'''
from __future__ import print_function
import os
import argparse
import datetime
import uuid
from paper.data import dbi as pdbi, uv_data, file_data, refresh

def calc_obs_info(s, host, path):
    '''
    generates all relevant data from uv* file

    Parameters
    ----------
    s | object: session object
    host | str: host of system
    path | str: path of uv* file

    Returns
    -------
    tuple:
        dict: observation values
        dict: file values
        dict: log values
    '''
    base_path, filename, filetype = file_data.file_names(path)
    source = ':'.join((host, path))

    if filetype in ('uv', 'uvcRRE'):
        time_start, time_end, delta_time, julian_date, polarization, length, obsnum = uv_data.calc_uv_data(
            host, path, username='obs')
    elif filetype in ('npz',):
        time_start, time_end, delta_time, julian_date, polarization, length, obsnum = uv_data.calc_npz_data(
            s, filename, username='obs')

    era, julian_day, lst = uv_data.date_info(julian_date)

    timestamp = datetime.datetime.utcnow()

    obs_info = {'obsnum': obsnum,
                'julian_date': julian_date,
                'polarization': polarization,
                'julian_day': julian_day,
                'lst': lst,
                'era': era,
                'era_type': None,
                'length': length,
                'time_start': time_start,
                'time_end': time_end,
                'delta_time': delta_time,
                'prev_obs': None, 
                'next_obs': None,
                'is_edge': None,
                'timestamp': timestamp}

    file_info = {'host': host,
                 'base_path': base_path,
                 'filename': filename,
                 'filetype': filetype,
                 'source': source,
                 'obsnum': obsnum,
                 'filesize': file_data.calc_size(host, path, username='obs'),
                 'md5sum': file_data.calc_md5sum(host, path, username='obs'),
                 'tape_index': None,
                 'init_host': host,
                 'is_tapeable': False,
                 'is_deletable': False,
                 'timestamp': timestamp}

    log_info = {'action': 'add by scan',
                'table': None,
                'identifier': source,
                'log_id': str(uuid.uuid4()),
                'timestamp': timestamp}

    return obs_info, file_info, log_info

def dupe_check(s, source_host, source_paths, verbose=False):
    '''
    checks for duplicate paths and removes to not waste time if possible
    checks for paths only on same host

    Parameters
    ----------
    s | object: session object
    source_host | str: host of uv* files
    source_paths | list[str]: paths of uv* files
    verbose | bool: whether paths are printed or not

    Returns
    -------
    list[str]: paths that are not already in database
    '''
    table = pdbi.File
    #FILEs = s.query(table).filter_by(host=source_host).all()
    # New find allows for hostname mangling to make ssh work
    FILEs = s.query(table).filter(table.host.like("%{}%".format(source_host))).all()
    paths = tuple(os.path.join(FILE.base_path, FILE.filename) for FILE in FILEs)

    unique_paths = set(source_paths) - set(paths)
    if verbose:
        print(len(unique_paths), 'unique paths')

    return unique_paths

def add_files_to_db(s, source_host, source_paths, verbose=False):
    '''
    adds files to the database

    Parameters
    ----------
    s | object: session object
    source_host | str: host of files
    source_paths | list[str]: paths of uv* files
    verbose | bool: whether paths are printed or not
    '''
    for source_path in source_paths:
        if verbose:
            print(source_path)
        obs_info, file_info, log_info = calc_obs_info(s, source_host, source_path)
        if obs_info['time_start'] == None:
            # We're not going to add this to the database
            continue
        try:
            s.add(pdbi.Observation(**obs_info))
        except:
            print('Failed to load in obs ', source_path)
        try:
            s.add(pdbi.File(**file_info))
        except:
            print('Failed to load in file ', source_path)
        #try:
        #    s.add(pdbi.Log(**log_info))
        #except:
        #    print('Failed to load in log ', source_path)

def add_files(source_host, source_paths):
    '''
    generates list of input files, check for duplicates, add information to database

    Parameters
    ----------
    source_host | str: host of files
    source_paths | list[str]: list of paths of uv* files
    '''
    dbi = pdbi.DataBaseInterface()
    with dbi.session_scope() as s:
        source_paths = sorted(dupe_check(s, source_host, source_paths, verbose=True))

        #uv_paths = [uv_path for uv_path in source_paths if not uv_path.endswith('.npz')]
        uv_paths = [uv_path for uv_path in source_paths if uv_path.endswith('.uv')]
        npz_paths = [npz_path for npz_path in source_paths if npz_path.endswith('.npz')]
        add_files_to_db(s, source_host, uv_paths, verbose=True)
        #add_files_to_db(s, source_host, npz_paths, verbose=True)
    #refresh.refresh_db()

if __name__ == '__main__':
    print('This is just a module')
