import os.path
from socket import *
from Config.scp_config import config
import multiprocessing
from FileChangeDetector.model.RecordDetector import FileChangeDetector
from Functions.Base163264 import *
import struct
import sys

class TCPClient:

    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.buff_size = config.client.buff_size
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
        except:
            print("client connect failed!")

    def send(self, data):
        data = str(data)
        data_encode = data.encode('utf-8')
        self.client_socket.send(struct.pack('i', len(data_encode)))
        self.client_socket.send(data_encode)

    def send_file(self, src_file_path):
        file_size = os.path.getsize(src_file_path)
        self.client_socket.send(struct.pack('i', file_size))
        file = open(src_file_path, "rb")
        while file_size > 0:
            t_buffsize = self.buff_size
            if file_size < t_buffsize:
                t_buffsize = file_size
            t_data = file.read(t_buffsize)
            self.client_socket.send(t_data)
            file_size -= len(t_data)
        file.close()

    def recv(self):
        data = b''
        # 接收数据
        message_size_data = self.client_socket.recv(4)
        if len(message_size_data) == 0:
            return data
        message_size = struct.unpack('i', message_size_data)[0]

        while message_size > 0:
            t_buffsize = config.client.buff_size
            if message_size < t_buffsize:
                t_buffsize = message_size
            t_data = self.client_socket.recv(t_buffsize)
            data = data + t_data
            message_size -= len(t_data)
        return data

    def __del__(self):
        self.client_socket.close()

class SCPClient:

    def __init__(self):
        self.tcp_client = TCPClient(config.server.ip, config.server.port)

    def create_folder_for_scp_file(self, target_file_path, server_project_path):
        flag = True
        target_file_relative_path = target_file_path[len(server_project_path):]
        folder_name_split = target_file_relative_path.split("/")[1:-1]
        t_folder_path = server_project_path
        self.create_server_folder(t_folder_path)
        if self.exists(t_folder_path) == False:
            flag = False
        if flag:
            for i in range(len(folder_name_split)):
                t_folder_path = t_folder_path+"/"+folder_name_split[i]
                self.create_server_folder(t_folder_path)
                if self.exists(t_folder_path) == False:
                    flag = False
                    break
        return flag

    def scp_file(self, src_file_path, target_file_path, server_project_path):
        try:
            if self.create_folder_for_scp_file(target_file_path, server_project_path) == True:
                self.tcp_client.send(config.command.scp_file+"\n"+target_file_path)
                self.tcp_client.send_file(src_file_path)
            else:
                print("project {0} not exists!".format(server_project_path))
        except:
            print("scp file {0} failed!".format(src_file_path))
            pass

    def get_server_project_message_digest_str(self, project_path):
        self.tcp_client.send(config.command.get_server_project_message_digest_str+"\n"+project_path)
        server_project_message_digest_str = self.tcp_client.recv()
        return server_project_message_digest_str

    def delete_server_file(self, file_path):
        self.tcp_client.send(config.command.delete_server_file+"\n"+file_path)

    def create_server_folder(self, folder_path):
        self.tcp_client.send(config.command.create_server_folder+"\n"+folder_path)

    def exists(self, server_file_path):
        self.tcp_client.send(config.command.exists+"\n"+server_file_path)
        data = self.tcp_client.recv()
        data_str = bytes(data).decode('utf-8')
        return data_str == "1"

    def show_project_different(self, local_project_path, server_project_path):
        server_project_message_digest_str = self.get_server_project_message_digest_str(server_project_path)
        file_change_detector = FileChangeDetector(local_project_path)
        file_change_detector.load_server_files(server_project_message_digest_str)
        created_files, changed_files, deleted_files = file_change_detector.get_created_changed_deleted_files()
        print("create files:")
        for i in range(len(created_files)):
            print(created_files[i].file_path)
        print("changed files:")
        for i in range(len(changed_files)):
            print(changed_files[i].file_path)
        print("deleted files:")
        for i in range(len(deleted_files)):
            print(deleted_files[i].file_path)

    def update_project_without_delete(self, local_project_path, server_project_path):
        server_project_message_digest_str = self.get_server_project_message_digest_str(server_project_path)
        file_change_detector = FileChangeDetector(local_project_path)
        file_change_detector.load_server_files(server_project_message_digest_str)
        created_files, changed_files, deleted_files = file_change_detector.get_created_changed_deleted_files()
        print("create files:")
        for i in range(len(created_files)):
            print(created_files[i].file_path)
            src_file_path = created_files[i].file_path
            src_file_project_path = created_files[i].project_path
            src_file_relative_path = src_file_path[len(src_file_project_path):]
            target_file_path = server_project_path + src_file_relative_path
            self.scp_file(src_file_path, target_file_path, server_project_path)
        print("changed files:")
        for i in range(len(changed_files)):
            print(changed_files[i].file_path)
            src_file_path = changed_files[i].file_path
            src_file_project_path = changed_files[i].project_path
            src_file_relative_path = src_file_path[len(src_file_project_path):]
            target_file_path = server_project_path + src_file_relative_path
            self.scp_file(src_file_path, target_file_path, server_project_path)

    def update_project(self, local_project_path, server_project_path):
        self.create_server_folder(server_project_path)
        server_project_message_digest_str = self.get_server_project_message_digest_str(server_project_path)
        file_change_detector = FileChangeDetector(local_project_path)
        file_change_detector.load_server_files(server_project_message_digest_str)
        created_files, changed_files, deleted_files = file_change_detector.get_created_changed_deleted_files()
        print("create files:")
        for i in range(len(created_files)):
            print(created_files[i].file_path)
            src_file_path = created_files[i].file_path
            src_file_project_path = created_files[i].project_path
            src_file_relative_path = src_file_path[len(src_file_project_path):]
            target_file_path = server_project_path+src_file_relative_path
            self.scp_file(src_file_path, target_file_path, server_project_path)
        print("changed files:")
        for i in range(len(changed_files)):
            print(changed_files[i].file_path)
            src_file_path = changed_files[i].file_path
            src_file_project_path = changed_files[i].project_path
            src_file_relative_path = src_file_path[len(src_file_project_path):]
            target_file_path = server_project_path + src_file_relative_path
            self.scp_file(src_file_path, target_file_path, server_project_path)
        print("deleted files:")
        for i in range(len(deleted_files)):
            print(deleted_files[i].file_path)
            self.delete_server_file(deleted_files[i].file_path)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        project_path = sys.argv[1]
        server_project_path = sys.argv[2]
    else:
        project_path, server_project_path = config.client.project_path, config.server.project_path
    my_scp_client = SCPClient()
    # my_scp_client.show_project_different(config.client.project_path, config.server.project_path)
    my_scp_client.update_project(project_path, server_project_path)