# scp_project

## 说明

当你有一个局域网内的服务器时，你在你的电脑上开发的项目，想要更新到服务器上，但是又不想用github时，就可以试试这个。

基本逻辑：

服务器端扫描服务器的项目文件夹，获取所有文件的SHA512摘要字符串，让后返回给客户端。
客户端可以查看或更新本地项目和服务器项目的区别，一共三种区别类型：
1 新建文件，本地项目有的文件，但是服务器项目没有
2 改变了的文件，文件的相对路径一致，但是SHA512摘要字符串不一致
3 删除的文件，本地项目没有的文件，但是服务器项目有

文件夹没有SHA512摘要字符串，所以就只是路径对比，一共两种区别类型:
1 新建文件夹，本地项目有但是服务器项目没有
2 删除的文件夹，服务器项目有但是本地没有

	protect_file	protect_folder
create_file	路径相等时就不行	文件在该保护目录下时不行(两种情况，1，源文件被目录保护，2，目标文件被目录保护)
change_file	路径相等时就不行	文件在该保护目录下时不行(两种情况，1，源文件被目录保护，2，目标文件被目录保护)
delete_file	路径相等时就不行	文件在该保护目录下时不行（只有可能删除目标文件，所以只看目标文件是否被目录保护即可）
		
create_folder	不影响	创建的文件夹在保护目录下不行(两种情况，一，源文件夹收到保护，二，目标文件夹收到保护)
delete_folder	保护的文件有在该目录下的时候不行	删除的文件夹在保护目录下不行（只有可能删除目标目录，所以只用看目标目录是否被目录保护即可）

设置了protect_files和protect_folder两个list可以传参，保护你不想被改变的文件或文件夹，但是要写对绝对路径哦


## instruction

this project is designed for someone have a local area network server, and he wanna upload his new project to the server but he don't wanna use github.

basic logic:

server get the files SHA512 str of the project on the server, then send the file info to client.

client get the different bettween local project and server project.

there are totally three type of different file:

1 new create file, it's in local project but not in server project.

2 changed file, it's has the right relative path, but different SHA512 str.

3 deleted file, it's in server project but not in local project.
