import argparse
import sqlite3
import sys
import jinja2
from jinja2 import Template, Environment

def main(args):
    parser = argparse.ArgumentParser(description='Exports tsk sqlite database file information into DFXML format as an alternative to fiwalk')
    parser.add_argument('database', help='tsk database containint file data to export to DFXML')
    parser.add_argument('output_file', help='output file name')

    args = parser.parse_args()
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment( loader=template_loader)
    tempy = templateEnv.get_template("DFXML_template.xml")

    conn = sqlite3.connect(args.database)
    c = conn.cursor()
    results = c.execute('select distinct obj_id from tsk_file_layout order by obj_id').fetchall()

    values = [process_item(conn, row) for row in results]
    f = open(args.output_file, 'w')
    f.write(tempy.render(files=values))
    f.close()
    conn.close

def process_item(conn, id):
    data = fetch_file_info(conn, id)
    byte_data = fetch_byte_run_info(conn, id)
    data['runs'] = byte_data
    return data

def fetch_image_info(conn, id):
    c = conn.cursor()
    info = {}
    result = c.execute('select tsk_ver from tsk_db_info').fetchone()
    info['version'] = result[0]

def fetch_byte_run_info(conn, id):
    c = conn.cursor()
    result = c.execute('select sequence, byte_start, byte_len from tsk_file_layout where obj_id = ? order by sequence', id).fetchall()
    return result

def fetch_file_info(conn, id):
    """
    Fetches the file information for the specified file id.  May return 'None' if the file was not found.
    """
    c = conn.cursor()
    result = c.execute('select parent_path || name as filename, size as filesize, meta_type, mtime, atime, crtime, mode, uid, gid, md5 from tsk_files where obj_id = ?', id).fetchone()
    col_names = [description[0] for description in c.description]
    return dict(zip(col_names, result))

if __name__ == "__main__":
    main(sys.argv)
