import os
import hashlib
from database.interface import upload_file_info

def compose_tree(connection, table_name, path):
    ''' Composes filetree of specified path (path to file, md5, size in bytes,
    filetype) and dynamically uploads it to database.'''
    tree = os.walk(path)
    for item in tree:
        #print (item)
        for filename in item[2]:
            file_info = {}
            file_path = (item[0] + os.sep + filename).replace("\\", os.sep)
            file_info["path"] = file_path.replace("\\", "/")
            file_info["md5"] = _get_hash(file_path)
            file_info["size"] = os.path.getsize(file_path) # in bytes
            filename_type = os.path.splitext(filename)
            file_info["type"] = filename_type[1][1:]
            file_info["description"] = ""
            upload_file_info(connection, table_name, file_info)

def _get_hash(file_path):
    BLOCKSIZE = 65536 # size to load into memory
    hasher = hashlib.md5()
    with open(file_path, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    hash_value = hasher.hexdigest()
    return hash_value
