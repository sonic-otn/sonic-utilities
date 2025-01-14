import math
import os
import sys
import tarfile
from ftplib import FTP, error_perm
import click
import socket
import paramiko

class Pysftp(object):
    def __init__(self, host, port, user, password,local_path='~/',remote_path='~/',time_out=10):

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.local_path = local_path
        self.server_path = remote_path
        self.time_out = time_out

    def connect(self):
        try:
            self.t = paramiko.Transport((self.host, int(self.port)))
            self.t.banner_timeout = self.time_out
            self.t.connect(username=self.user, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.t)
        except Exception as e:
            click.echo(f"Connect Error: {e}")
            return (False,e)
        else:
            return True

    def put(self,path='',call_back=True):
        try:
            if call_back:
                call_back = self.printTotals
            else:
                call_back = None
            self.sftp.put(self.local_path,self.server_path,callback=call_back)
        except Exception as e:
            click.echo(e)
            raise
        else:
            return True

    def get(self,call_back=True):
        try:
            if call_back:
                call_back = self.printTotals
            else:
                call_back = None
            self.sftp.stat(self.server_path)
            self.sftp.get(self.server_path, self.local_path,callback=call_back)
        except Exception as e:
            click.echo(e)
            return False, e
        else:
            return True

    def printTotals(self, transferred, toBeTransferred):
        self.progressbar(transferred,toBeTransferred)

    def progressbar(self,cur, total):

        try:
            percent = '{:.2%}'.format(cur / total)
            if float(percent.split('%')[0]) > float('100.00'):
                return
            sys.stdout.write('\r')
            sys.stdout.write('[%-50s] %s' % ('=' * int(math.floor(cur * 50 / total)), percent))
            sys.stdout.flush()
            if cur >= total:
                sys.stdout.write('\r\n')
        except Exception as e:
            click.echo(e)
            raise e

    def close(self):
        self.sftp.close()


def make_file_zip(output_filename,source_dir):
    try:
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
    except Exception as e:
        raise Exception(f' cannot create directory {output_filename} Permission denied')


class FTP_OPS(object):
    def __init__(self, ftp_ip, ftp_port, ftp_user, ftp_pwd):
        self.ftp_ip = ftp_ip
        self.ftp_port = ftp_port
        self.ftp_user = ftp_user
        self.ftp_pwd = ftp_pwd

    def ftp_connect(self,is_print=True):
        ftp = FTP()
        ftp.connect(host=self.ftp_ip, port=self.ftp_port)
        ftp.encoding = 'utf-8'
        try:
            ftp.login(self.ftp_user, self.ftp_pwd)
            if is_print:
                click.echo('[{}]login ftp {}'.format(self.ftp_user,ftp.getwelcome()))  
        except(socket.error, socket.gaierror):  
            click.echo("ERROR: cannot connect [{}:{}]".format(self.ftp_ip, self.ftp_port))
            return None
        except error_perm:  
            click.echo("ERROR: user Authentication failed ")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        return ftp

    def upload_file(self, ftp: FTP, remotepath: str,localpath: str, file: str):
        flag = False
        buffer_size = 10240 
        fp = open(os.path.join(localpath, file), 'rb')
        try:
            ftp.cwd(remotepath) 
            click.echo("found folder [{}] in ftp server, upload processing.".format(remotepath))
            ftp.voidcmd('TYPE I')
            ftp.storbinary('STOR ' + file, fp, buffer_size)
            ftp.set_debuglevel(0)
            click.echo("upload [{}] success".format(file))
            flag = True
        except error_perm as e:
            click.echo('file[{}] upload failure,{}'.format(file, str(e)))
        except TimeoutError:
            click.echo('file[{}] upload timeout'.format(file))
            pass
        except Exception as e:
            click.echo('file[{}] upload exception'.format(file, str(e)))
            pass
        finally:
            fp.close()

        return {'file_name': file, 'flag': flag}

    def dowmload_log_file(self, ftp_file_path, dst_file_path,is_print=True):
        buffer_size = 10240
        ftp = self.ftp_connect(is_print)
        ftp.voidcmd('TYPE I')
        remote_file_size = ftp.size(ftp_file_path)  
        lsize = 0
        if os.path.exists(dst_file_path):
            lsize = os.stat(dst_file_path).st_size
        # print(lsize,remote_file_size)
        if remote_file_size <= lsize:
            # print('local file is bigger or equal remote file')
            return
        conn = ftp.transfercmd('RETR {0}'.format(ftp_file_path), lsize)
        f = open(dst_file_path, "ab")
        while True:
            data = conn.recv(buffer_size)
            if not data:
                break
            f.write(data)
        # self.progressbar(local_file_size, total_size)
        f.close()
        return remote_file_size

    def download_file(self, ftp_file_path, dst_file_path,is_print=True):
        ftp = self.ftp_connect(is_print)
        buffer_size = 10240  
        ftp.voidcmd('TYPE I')
        remote_file_size = ftp.size(ftp_file_path)  

        cmpsize = 0  
        lsize = 0
        # check local file isn't exists and get the local file size
        if os.path.exists(dst_file_path):
            lsize = os.stat(dst_file_path).st_size
        if remote_file_size <= lsize:
            return
        conn = ftp.transfercmd('RETR {0}'.format(ftp_file_path), lsize)
        f = open(dst_file_path, "ab")
        while True:
            data = conn.recv(buffer_size)
            if not data:
                break
            f.write(data)
            cmpsize += len(data)
            self.progressbar(cmpsize, remote_file_size)
        f.close()


    def progressbar(self,cur, total):
        percent = '{:.2%}'.format([1 if cur / total >= 1 else cur / total][0])
        sys.stdout.write('\r')
        sys.stdout.write('[%-50s] %s' % ('=' * int(math.floor(cur * 50 / total)), percent))
        sys.stdout.flush()
        if cur >= total:
            sys.stdout.write('\n')

    def get_card_tarlog_file_list(self, remote_path,is_print=True):
        ftp = self.ftp_connect(is_print)
        log_file_name_lists = []
        if remote_path:
            ftp.cwd(remote_path)
        for file in ftp.nlst():
            if file.startswith('LOG'):
                log_file_name_lists.append(file)
        return log_file_name_lists

    def get_file_exist(self,file_path_name,is_print=True):
        path,file = '/'.join(file_path_name.split('/')[:-1]),file_path_name.split('/')[-1]
        ftp = self.ftp_connect(is_print)
        if file_path_name in ftp.nlst(path):
            return True
        else:
            return False