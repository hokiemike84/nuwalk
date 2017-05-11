import argparse
import sqlite3
import sys
import jinja2
from jinja2 import Template, Environment

def main(args):
    parser = argparse.ArgumentParser(description='Exports tsk sqlite database file information into DFXML format as an alternative to fiwalk')
    parser.add_argument('database', help='tsk database containing file data to export to DFXML')
    parser.add_argument('output_file', help='output file name')

    args = parser.parse_args()
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment( loader=template_loader)
    tempy = templateEnv.get_template("DFXML_template.xml")

    conn = sqlite3.connect(args.database)

    fs_list = get_fs_info(conn, id);
    volumes = []
    for fs_info in fs_list:
        c = conn.cursor()
        offset = fs_info[1]
        results = c.execute('select distinct obj_id from tsk_files where fs_obj_id = ? and uid is not null order by obj_id ', (fs_info[0],)).fetchall()
        values = [process_item(conn, row, offset) for row in results]
        volumes.append((offset, values))
    f = open(args.output_file, 'w', encoding='utf-8')
    f.write(tempy.render(volumes=volumes))
    f.close()
    conn.close

def get_fs_info(conn, id):
    c = conn.cursor()
    results = c.execute('select obj_id, img_offset from tsk_fs_info').fetchall()
    return results

def process_item(conn, id, offset):
    data = fetch_file_info(conn, id)
    byte_data = fetch_byte_run_info(conn, id, offset)
    data['runs'] = byte_data
    return data

def fetch_image_info(conn, id):
    c = conn.cursor()
    info = {}
    result = c.execute('select tsk_ver from tsk_db_info').fetchone()
    info['version'] = result[0]

def fetch_byte_run_info(conn, id, offset):
    c = conn.cursor()
    result = c.execute('select sequence, byte_start + ?, byte_len from tsk_file_layout where obj_id = ? order by sequence', (offset, id[0])).fetchall()
    return result

def fetch_file_info(conn, id):
    """
    Fetches the file information for the specified file id.  May return 'None' if the file was not found.
    """
    c = conn.cursor()
    result = c.execute('select ifnull(parent_path || name, name) as filename, size as filesize, meta_type, mtime, atime, crtime, mode, uid, gid, md5 from tsk_files where obj_id = ?', id).fetchone()
    col_names = [description[0] for description in c.description]
    data = dict(zip(col_names, result))
    if result[0][0] == '/':
        data['filename'] = data['filename'][1:]
    return data

if __name__ == "__main__":
    main(sys.argv)
