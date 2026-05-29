from flask import Flask
from flask import Flask, jsonify
import sqlite3

# 1. 实例化 Flask 应用（也就是召唤一台服务器）
app = Flask(__name__)

def get_db_connection():
    # 创建一个到SQLite数据库的连接，数据库文件名为'station.db'
    conn = sqlite3.connect('station.db')
    # 下面这行非常关键！它能让我们像操作 Python 字典一样，通过字段名（如 row['username']）来获取数据
    conn.row_factory = sqlite3.Row 
    # 返回数据库连接对象
    return conn


# 2. 定义路由 (Routing) - 绑定网址与操作
@app.route('/')
def home():
    return "启动成功"

# --- 新增：测试数据库连接的路由 ---
@app.route('/test_db')
def test_db():
    try:
        # 1. 调用我们刚刚写的函数建立连接
        conn = get_db_connection()
        # 2. 用完立刻关闭是一个好习惯
        conn.close()
        return "太棒了！数据库 station.db 连接成功！"
    except Exception as e:
        return f"糟糕，连接失败了，错误信息是：{e}"
# --------------------------------

# --- 新增：获取所有快递记录的接口 ---
@app.route('/api/express', methods=['GET'])
def get_all_express():
    # 1. 获取数据库连接
    conn = get_db_connection()
    
    # 2. 执行原生 SQL 查询所有记录
    # fetchall() 的意思是“把查询到的所有结果都拿出来”
    express_records = conn.execute('SELECT * FROM express').fetchall()
    
    # 3. 及时关闭连接
    conn.close()
    
    # 4. 把数据转成前端需要的 JSON 格式
    # 因为我们之前设置了 conn.row_factory = sqlite3.Row，
    # 这里可以直接用 dict(row) 把每一行数据库记录方便地转成 Python 字典
    express_list = [dict(row) for row in express_records]
    
    # 5. 返回 JSON 数据
    return jsonify(express_list)
# --------------------------------



if __name__ == '__main__':
    app.run(debug=True)