from yacs.config import CfgNode as CN

config = CN()

config.server = CN()
config.server.port = 9999
config.server.ip = "127.0.0.1"
config.server.buff_size = 40960
config.server.project_path = "/home/xxx/test_project"
config.server.message_digest_algorithm = "SHA512"


config.client = CN()
config.client.port = 8888
config.client.ip = "127.0.0.1"
config.client.buff_size = 40960
config.client.project_path = "D:/python/python_data/test_project"
config.client.message_digest_algorithm = "SHA512"

config.command = CN()
config.command.get_server_project_message_digest_str = "get_server_project_message_digest_str"
config.command.delete_server_file = "delete_server_file"
config.command.create_server_folder = "create_server_folder"
config.command.exists = "exists"
config.command.scp_file = "scp_file"


