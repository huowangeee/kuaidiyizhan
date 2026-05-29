import sqlite3

# 1. 连接到数据库文件（如果文件不存在，会自动创建一个名为 station.db 的文件）
conn = sqlite3.connect('station.db')

# 2. 获取游标
cursor = conn.cursor()

# 3. 执行建表 SQL 语句

cursor.execute('''
    -- 创建用户表
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );
    -- 创建快递信息表
    CREATE TABLE IF NOT EXISTS express (
    id INTEGER PRIMARY KEY AUTOINCREMENT,             
    tracking_number TEXT NOT NULL,                            
    recipient_name TEXT NOT NULL,                             
    phone_number TEXT NOT NULL,                                  
    pickup_code TEXT NOT NULL,                                   
    status TEXT NOT NULL,                                             
    arrival_time TEXT,                                                   
    pickup_time TEXT                                                      
);

''')
# 4. 提交保存并关闭连接
conn.commit()
conn.close()

print("数据库初始化成功！")