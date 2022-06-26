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

    def get_server_project_files(self, project_path):
        self.tcp_client.send(config.command.get_server_project_files+"\n"+project_path)
        server_project_files_bytes = self.tcp_client.recv()
        return server_project_files_bytes

    def get_server_project_folders(self, project_path):
        self.tcp_client.send(config.command.get_server_project_folders+"\n"+project_path)
        server_project_folders_bytes = self.tcp_client.recv()
        return server_project_folders_bytes

    def delete_server_file(self, file_path):
        self.tcp_client.send(config.command.delete_server_file+"\n"+file_path)

    def delete_server_folder(self, folder_path):
        self.tcp_client.send(config.command.delete_server_folder + "\n" + folder_path)

    def create_server_folder(self, folder_path):
        self.tcp_client.send(config.command.create_server_folder+"\n"+folder_path)

    def exists(self, server_file_path):
        self.tcp_client.send(config.command.exists+"\n"+server_file_path)
        data = self.tcp_client.recv()
        data_str = bytes(data).decode('utf-8')
        return data_str == "1"

    def show_project_different(self, local_project_path, server_project_path):
        server_project_files_bytes = self.get_server_project_files(server_project_path)
        server_project_folder_bytes = self.get_server_project_folders(server_project_path)
        file_change_detector = FileChangeDetector(local_project_path)
        file_change_detector.load_server_files_folders(server_project_files_bytes, server_project_folder_bytes)
        created_files, changed_files, deleted_files = file_change_detector.get_created_changed_deleted_files()
        created_folders, deleted_folders = file_change_detector.get_created_deleted_folders()
        print("create files:")
        for i in range(len(created_files)):
            print(created_files[i].file_path)
        print("changed files:")
        for i in range(len(changed_files)):
            print(changed_files[i].file_path)
        print("deleted files:")
        for i in range(len(deleted_files)):
            print(deleted_files[i].file_path)
        print("created_folders")
        for i in range(len(created_folders)):
            print(created_folders[i])
        print("deleted_folders")
        for i in range(len(deleted_folders)):
            print(deleted_folders[i])

    def remove_file_path_file_name_left_folder_path(self, file_path):
        file_name_start = file_path.rfind("/")
        folder_path = file_path[:file_name_start]
        return folder_path

    def update_project_with_protect_folder_and_files(self, local_project_path, server_project_path, protect_files_path, protect_folders_path):
        self.create_server_folder(server_project_path)
        server_project_files_bytes = self.get_server_project_files(server_project_path)
        server_project_folder_bytes = self.get_server_project_folders(server_project_path)
        file_change_detector = FileChangeDetector(local_project_path)
        file_change_detector.load_server_files_folders(server_project_files_bytes, server_project_folder_bytes)
        created_files, changed_files, deleted_files = file_change_detector.get_created_changed_deleted_files()
        created_folders, deleted_folders = file_change_detector.get_created_deleted_folders()
        print("create files:")
        for i in range(len(created_files)):

            src_file_path = created_files[i].file_path
            src_file_project_path = created_files[i].project_path
            src_file_relative_path = src_file_path[len(src_file_project_path):]
            target_file_path = server_project_path + src_file_relative_path

            flag = False
            j = 0
            protect_info = ""
            while j < len(protect_files_path) and flag == False:
                if src_file_path == protect_files_path[j]:
                    flag = True
                    protect_info = "create "+target_file_path+" failed! because "+protect_files_path[j] +" protected!"
                j += 1
            j = 0
            while j < len(protect_folders_path) and flag == False:
                # 注意判断一个文件是否属于某一个文件夹的时候，不能简单的用startswith，反例：D:/1 指文件夹 D:/1.txt前缀是那个文件夹，但不在那里面
                # 可以先去除掉文件路径的最后一个/及之后的东西，这样就不包含文件名了，就只剩下了目录，此时就可以用startswith了
                src_file_folder = self.remove_file_path_file_name_left_folder_path(src_file_path)
                target_file_folder = self.remove_file_path_file_name_left_folder_path(target_file_path)
                if str(src_file_folder).startswith(protect_folders_path[j]) or str(target_file_folder).startswith(protect_folders_path[j]):
                    flag = True
                    protect_info = "create " + target_file_path + " failed! because " + protect_folders_path[
                        j] + " protected!"
                j += 1
            if flag:
                print(protect_info)
                continue
            print(target_file_path)
            self.scp_file(src_file_path, target_file_path, server_project_path)
        print("changed files:")
        for i in range(len(changed_files)):
            src_file_path = changed_files[i].file_path
            src_file_project_path = changed_files[i].project_path
            src_file_relative_path = src_file_path[len(src_file_project_path):]
            target_file_path = server_project_path + src_file_relative_path

            flag = False
            j = 0
            protect_info = ""
            while j < len(protect_files_path) and flag == False:
                if src_file_path == protect_files_path[j]:
                    flag = True
                    protect_info = "change " + target_file_path + " failed! because " + protect_files_path[
                        j] + " protected!"
                j += 1
            j = 0
            while j < len(protect_folders_path) and flag == False:
                src_file_folder = self.remove_file_path_file_name_left_folder_path(src_file_path)
                target_file_folder = self.remove_file_path_file_name_left_folder_path(target_file_path)
                if str(src_file_folder).startswith(protect_folders_path[j]) or str(target_file_folder).startswith(
                        protect_folders_path[j]):
                    flag = True
                    protect_info = "change " + target_file_path + " failed! because " + protect_folders_path[
                        j] + " protected!"
                j += 1
            if flag:
                print(protect_info)
                continue
            print(target_file_path)
            self.scp_file(src_file_path, target_file_path, server_project_path)
        print("deleted files:")
        for i in range(len(deleted_files)):

            flag = False
            j = 0
            protect_info = ""
            while j < len(protect_files_path) and flag == False:
                if deleted_files[i].file_path == protect_files_path[j]:
                    flag = True
                    protect_info = "delete " + deleted_files[i].file_path + " failed! because " + protect_files_path[
                        j] + " protected!"
                j += 1
            j = 0
            while j < len(protect_folders_path) and flag == False:
                deleted_file_folder = self.remove_file_path_file_name_left_folder_path(deleted_files[i].file_path)
                if str(deleted_file_folder).startswith(protect_folders_path[j]):
                    flag = True
                    protect_info = "delete " + deleted_files[i].file_path + " failed! because " + protect_folders_path[
                        j] + " protected!"
                j += 1
            if flag:
                print(protect_info)
                continue
            print(deleted_files[i].file_path)
            self.delete_server_file(deleted_files[i].file_path)
        print("created_folders")
        for i in range(len(created_folders)):
            local_folder_path = created_folders[i].folder_path
            local_folder_relative_path = local_folder_path[len(local_project_path):]
            server_folder_path = server_project_path + local_folder_relative_path

            flag = False
            j = 0
            protect_info = ""
            while j < len(protect_folders_path) and flag == False:
                if str(local_folder_path).startswith(protect_folders_path[j]) or str(
                        server_folder_path).startswith(protect_folders_path[j]):
                    flag = True
                    protect_info = "create " + server_folder_path + " failed! because " + protect_folders_path[
                    j] + " protected!"
                j += 1
            if flag:
                print(protect_info)
                continue
            print(server_folder_path)
            self.create_server_folder(server_folder_path)
        print("deleted_folders")
        for i in range(len(deleted_folders)):
            server_folder_path = deleted_folders[i].folder_path

            # 这里需要注意，判断一个目录是否可以删除不能只看有没有保护它或它的父目录，而且要看有没有保护它的子目录或子文件，因为
            # 如果有人保护它的子目录或子文件也相当于保护了这个目录
            flag = False
            j = 0
            protect_info = ""
            while j < len(protect_files_path) and flag == False:
                protect_file_folder = self.remove_file_path_file_name_left_folder_path(protect_files_path[j])
                if str(protect_file_folder).startswith(server_folder_path):
                    flag = True
                    protect_info = "delete " + server_folder_path + " failed! because " + protect_files_path[
                    j] + " protected!"
                j += 1
            j = 0
            while j < len(protect_folders_path) and flag == False:
                if str(server_folder_path).startswith(protect_folders_path[j]):
                    flag = True
                    protect_info = "delete " + server_folder_path + " failed! because " + protect_folders_path[
                    j] + " protected!"
                j += 1
            if flag:
                print(protect_info)
                continue
            print(server_folder_path)
            self.delete_server_folder(server_folder_path)

if __name__ == '__main__':
    if len(sys.argv) == 3:
        project_path = sys.argv[1]
        server_project_path = sys.argv[2]
    else:
        project_path, server_project_path = config.client.project_path, config.server.project_path
    my_scp_client = SCPClient()
    # my_scp_client.show_project_different(config.client.project_path, config.server.project_path)

    protect_files = [

    ]
    protect_folders = [
        "/media/zxr409/data1/python_data/SiamRPNPP_Change/train/SiamRPNPP_FeatureMap_Train/train_log",
        "/media/zxr409/data1/python_data/SiamRPNPP_Change/train/SiamRPNPP_Train/train_log",
        "/media/zxr409/data1/python_data/SiamRPNPP_Change/train/SiamRPNPPChange_FeatureMap_Train/train_log",
        "/media/zxr409/data1/python_data/SiamRPNPP_Change/train/SiamRPNPPChange_Train/train_log",
        "/media/zxr409/data1/python_data/SiamRPNPP_Change/save",
    ]

    my_scp_client.update_project_with_protect_folder_and_files(project_path, server_project_path, protect_files, protect_folders)