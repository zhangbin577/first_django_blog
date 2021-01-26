

# 导入pymysql：并防止连接Mysql时，报"No module named 'MySQLdb'"！
import pymysql
pymysql.install_as_MySQLdb()
