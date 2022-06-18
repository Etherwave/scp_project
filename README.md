# scp_project

##说明

当你有一个局域网内的服务器时，你在你的电脑上开发的项目，想要更新到服务器上，但是又不想用github时，就可以试试这个。

基本逻辑：

服务器端扫描服务器的项目文件夹，获取所有文件的SHA512摘要字符串，让后返回给客户端。
客户端可以查看或更新本地项目和服务器项目的区别，一共三种区别类型：
1 新建文件，本地项目有的文件，但是服务器项目没有
2 改变了的文件，文件的相对路径一致，但是SHA512摘要字符串不一致
3 删除的文件，本地项目没有的文件，但是服务器项目有

未来计划：

添加不更新文件及文件夹列表。

## instruction

this project is designed for someone have a local area network server, and he wanna upload his new project to the server but he don't wanna use github.

basic logic:

server get the files SHA512 str of the project on the server, then send the file info to client.

client get the different bettween local project and server project.

there are totally three type of different file:

1 new create file, it's in local project but not in server project.

2 changed file, it's has the right relative path, but different SHA512 str.

3 deleted file, it's in server project but not in local project.
