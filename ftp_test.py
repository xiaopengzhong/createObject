#@File   : .py
#@Time   : 2024/4/12 11:22
#@Author : 
#@Software: PyCharm
from ftplib import FTP
import sys


def ftp_connect(host, username, password):
    try:
        # 创建 FTP 对象，并设置编码为 UTF-8
        ftp = FTP(host)


        # 登录到 FTP 服务器
        ftp.login(username, password)

        print("Connected to FTP server.")

        # 列出当前目录内容
        ftp.dir()

        # 关闭 FTP 连接
        ftp.quit()

    except Exception as e:
        print("Failed to connect to FTP server:", e)


# 设置 FTP 服务器的地址、用户名和密码
host = "70fb22c.all123.net"
username = "zxp"
password = "zxp19960603111"

# 连接到 FTP 服务器
ftp_connect(host, username, password)



