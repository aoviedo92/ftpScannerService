import ftputil
import sys
import json
from ftputil.error import PermanentError, FTPOSError
from _datetime import datetime
from os import path, environ
from slugify import slugify

servers = []
scan_result = []
not_found = []


def scan_ftp():
    count_scanned_files = 0
    count_scanned_dirs = 0
    dirs_to_scan = [scan_dir]
    try:
        ftp = ftputil.FTPHost(host, user, passw)
    except (TimeoutError, FTPOSError) as e:
        error = "Se produjo un error durante el intento de conexión"
        return 1  # los errores son manejados en el js
    while dirs_to_scan:
        try:
            current_url = dirs_to_scan.pop(0)
            # print("+ " + current_url)
            # scanned_dir = {"url": current_url, "name": "", "files": [], "slug": ""}
            scanned_dir = {"url": current_url, "name": "", "files": []}
            try:
                res = ftp.listdir(current_url)
                _name = current_url.split('/')[-1]  # dir/sub-dir/<valor a tomar>
                scanned_dir['name'] = _name
                # scanned_dir['slug'] = slugify(_name)
                for name in res:
                    new_url = current_url + "/" + name
                    if ftp.path.isdir(new_url):
                        new_url = new_url
                        dirs_to_scan.append(new_url)
                        count_scanned_dirs += 1
                    if ftp.path.isfile(new_url):
                        # print("    " + new_url)
                        # scanned_dir["files"].append((name, slugify(name)))
                        scanned_dir["files"].append(name)
                        count_scanned_files += 1
                scan_result.append(scanned_dir)
            except PermanentError:
                # file_or_dir_not_found = "No se encontró el fichero o directorio: " + current_url
                not_found.append(current_url)
                continue
            except FTPOSError as e:
                # si se produjera una desconexion una vez empezado el escaneo.
                # "No se pudo conectar al servidor, revise la conexión."
                return 2
        except UnicodeEncodeError:
            continue
    return [count_scanned_dirs, count_scanned_files]


def encode_json():
    try:
        json_data = json.dumps(servers, indent=4)
        with open(json_data_file_abs_path, "w", encoding='utf-8') as data_file:
            data_file.write(json_data)
    except FileNotFoundError:
        print(3)  # enviar el dato a la standar output
        return 3


def load_data_from_json():
    try:
        with open(json_data_file_abs_path, "r", encoding='utf-8') as data_file:
            read = data_file.read()
            return json.loads(read)
    except FileNotFoundError:
        print(3)  # enviar el dato a la standar output
        return 3


def removing_server_for_updating(server_remove_to):
    servers_from_json = load_data_from_json()
    for server in servers_from_json:
        if server['server_name'] == server_remove_to:
            continue
        servers.append(server)


if __name__ == '__main__':
    args = sys.argv
    json_data_file = "\myftpsearch_data.json"
    json_data_file_abs_path = environ['HOMEDRIVE'] + '\\' + environ[
        'HOMEPATH'] + json_data_file  # todo mejorar expresion, buscar como obtenr el homedir

    # 5 args --> update o save new server
    server_name = args[1]
    host = args[2]
    user = args[3]
    if not user or user == 'undefined':
        user = 'anonymous'
    passw = args[4]
    scan_dir = args[5]
    # server_name = "test2"
    # host = "localhost"
    # scan_dir = "test"
    # user = "anonymous"
    # passw = ""

    return_code = scan_ftp()
    if return_code in [1, 2, 3]:
        print(return_code)
    if type(return_code) is list:
        if scan_result:
            count_scanned_dirs = return_code[0]
            count_scanned_files = return_code[1]
            removing_server_for_updating(server_name)
            server_updated = {
                "server_name": server_name,
                "active": False,
                "scan_dir": scan_dir,
                "host": host,
                "user": user,
                "passw": passw,
                "update_at": datetime.now().strftime('%b %d, %Y'),
                "count_files": count_scanned_files,
                "count_dirs": count_scanned_dirs,
                "scanned_dirs": scan_result
            }
            servers.append(server_updated)
            encode_json()
        if not_found:
            print('No fueron encontrados:\n')
            print("\n".join(not_found))
        print(4)#el 4 se maneja en el js como exito.
