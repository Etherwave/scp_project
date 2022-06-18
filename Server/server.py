import os
from socket import *
from Config.scp_config import config
from FileChangeDetector.model.RecordDetector import FolderRecord
import multiprocessing
import struct
from Functions.Base163264 import *
import time

class TCPServer:

    def __init__(self):
        self.server_ip = config.server.ip
        self.server_port = config.server.port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.process_list = []

    def bind_listen(self):
        # 绑定IP地址和固定端口
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)

    def accept(self):
        while 1:
            client_socket, client_address = self.server_socket.accept()
            p = multiprocessing.Process(target=analyze_command, args=(SCPServer(), client_socket, client_address,))
            p.start()
            self.process_list.append(p)
            process_number = len(self.process_list)
            i = 0
            while i < process_number:
                if self.process_list[i].is_alive() == False:
                    self.process_list.__delitem__(i)
                    i = 0
                    process_number = len(self.process_list)
                else:
                    i += 1

def analyze_command(scp_server, client_socket, client_address):
    scp_server.analyze_command(client_socket, client_address)

class SCPServer:

    def __init__(self):
        pass

    def send(self, t_socket, data):
        data = str(data)
        data_encode = data.encode('utf-8')
        t_socket.sendall(struct.pack('i', len(data_encode)))
        t_socket.sendall(data_encode)

    def recv(self, t_socket):
        data = b''
        message_size_data = t_socket.recv(4)
        if len(message_size_data) == 0:
            return data

        message_size = struct.unpack('i', message_size_data)[0]
        while message_size > 0:
            t_buffsize = config.server.buff_size
            if message_size < t_buffsize:
                t_buffsize = message_size
            t_data = t_socket.recv(t_buffsize)
            data = data + t_data
            message_size -= len(t_data)
        return data

    def recv_file(self, t_socket, file_path):
        message_size_data = t_socket.recv(4)
        if len(message_size_data) == 0:
            return

        message_size = struct.unpack('i', message_size_data)[0]
        file = open(file_path, "wb")
        while message_size > 0:
            t_buffsize = config.server.buff_size
            if message_size < t_buffsize:
                t_buffsize = message_size
            t_data = t_socket.recv(t_buffsize)
            file.write(t_data)
            message_size -= len(t_data)
        file.close()
        return

    def analyze_command(self, client_socket, client_address):
        while 1:
            data = self.recv(client_socket)
            if len(data) == 0:
                break
            data_str = bytes(data).decode("utf-8")
            data_str_split = data_str.split("\n")
            command = data_str_split[0]
            args = data_str_split[1:]
            print(command)

            if command == config.command.get_server_project_message_digest_str:
                print(args[0])
                data = self.get_server_project_message_digest_str(args[0])
                self.send(client_socket, data)
            elif command == config.command.delete_server_file:
                print(args[0])
                self.delete_server_file(args[0])
            elif command == config.command.create_server_folder:
                print(args[0])
                self.create_server_folder(args[0])
            elif command == config.command.exists:
                print(args[0])
                data = 1 if self.exists(args[0]) else 0
                self.send(client_socket, data)
            elif command == config.command.scp_file:
                print(args[0])
                self.scp_file(client_socket, args[0])

        client_socket.close()

    def get_server_project_message_digest_str(self, project_path):
        folder_record = FolderRecord(project_path, project_path, config.server.message_digest_algorithm)
        files = folder_record.get_files()
        data = ""
        for i in range(len(files)):
            if i != 0:
                data += "\n"
            data = data+str(files[i])
        return data

    def delete_server_file(self, file_path):
        try:
            os.remove(file_path)
        except:
            pass

    def create_server_folder(self, folder_path):
        try:
            os.mkdir(folder_path)
        except:
            pass

    def exists(self, path):
        return os.path.exists(path)

    def scp_file(self, client_socket, file_path):
        try:
            self.recv_file(client_socket, file_path)
        except:
            pass

if __name__ == '__main__':
    tcp_server = TCPServer()
    tcp_server.bind_listen()
    tcp_server.accept()



