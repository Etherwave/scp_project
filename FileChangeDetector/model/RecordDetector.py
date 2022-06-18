from FileChangeDetector.functions.MessageDigestAlgorithm import MessageDigestAlgorithmForFile, MessageDigestAlgorithmForStr
import os
import time

def get_time_str():
    t = time.localtime()
    return "%d_%d_%d_%d_%d_%d" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

class FileRecord:

    def __init__(self):
        self.project_path = ""
        self.file_path = ""
        self.message_digest_str = ""

    def init_from_file(self, project_path, file_path, algorithm):
        self.project_path = project_path
        self.file_path = file_path
        self.message_digest_str = MessageDigestAlgorithmForFile(self.file_path, algorithm)

    def init_from_str(self, project_path, file_path, message_digest_str):
        self.project_path = project_path
        self.file_path = file_path
        self.message_digest_str = message_digest_str

    def __str__(self):
        return self.project_path+"\n"+self.file_path+"\n"+self.message_digest_str

    def __eq__(self, other):
        return self.file_path[len(self.project_path):] == other.file_path[len(other.project_path):] and self.message_digest_str == other.message_digest_str


class FolderRecord:

    def __init__(self, project_path, folder_path, algorithm):
        self.project_path = project_path
        self.folder_path = folder_path
        self.files = []
        self.sub_folders = []
        if os.path.exists(self.folder_path) == True:
            file_names = os.listdir(self.folder_path)
            for i in range(len(file_names)):
                file_path = self.folder_path+"/"+file_names[i]
                if os.path.isdir(file_path):
                    self.sub_folders.append(FolderRecord(self.project_path, file_path, algorithm))
                else:
                    file_record = FileRecord()
                    file_record.init_from_file(self.project_path, file_path, algorithm)
                    self.files.append(file_record)

    def get_files(self):
        files = self.files
        for i in range(len(self.sub_folders)):
            files.extend(self.sub_folders[i].get_files())
        return files


class FileChangeDetector:

    def __init__(self, project_path, algorithm="SHA512"):
        self.project_path = project_path
        self.algorithm = algorithm

        self.time_str = get_time_str()
        self.folder_record = FolderRecord(self.project_path, self.project_path, self.algorithm)
        self.current_files = self.folder_record.get_files()

        self.server_time_str = ""
        self.server_files = []

    def load_server_files(self, server_project_message_digest_str):
        self.server_files = []
        self.server_time_str = get_time_str()
        server_project_message_digest_str = bytes(server_project_message_digest_str).decode('utf-8')
        server_project_message_digest_str_split = server_project_message_digest_str.split("\n")
        for i in range(int(len(server_project_message_digest_str_split)/3)):
            project_path = server_project_message_digest_str_split[i*3]
            file_path = server_project_message_digest_str_split[i*3+1]
            message_digest_str = server_project_message_digest_str_split[i*3+2]
            file_record = FileRecord()
            file_record.init_from_str(project_path, file_path, message_digest_str)
            self.server_files.append(file_record)


    def get_created_changed_deleted_files(self):
        created_files = []
        changed_files = []
        deleted_files = []
        current_file_flag = [0 for i in range(len(self.current_files))]
        server_file_flag = [0 for i in range(len(self.server_files))]

        for i in range(len(self.current_files)):
            current_file_path = self.current_files[i].file_path
            current_project_path = self.current_files[i].project_path
            current_file_relative_path = current_file_path[len(current_project_path):]
            current_file_message_digest_str = self.current_files[i].message_digest_str
            for j in range(len(self.server_files)):
                server_file_path = self.server_files[j].file_path
                server_project_path = self.server_files[j].project_path
                server_file_relative_path = server_file_path[len(server_project_path):]
                server_file_message_digest_str = self.server_files[j].message_digest_str

                if current_file_relative_path == server_file_relative_path:
                    current_file_flag[i] = 1
                    server_file_flag[j] = 1
                    if current_file_message_digest_str == server_file_message_digest_str:
                        current_file_flag[i] = 2
                        server_file_flag[j] = 2

        for i in range(len(current_file_flag)):
            if current_file_flag[i] == 0:
                created_files.append(self.current_files[i])
            elif current_file_flag[i] == 1:
                changed_files.append(self.current_files[i])

        for j in range(len(server_file_flag)):
            if server_file_flag[j] == 0:
                deleted_files.append(self.server_files[j])
        return created_files, changed_files, deleted_files