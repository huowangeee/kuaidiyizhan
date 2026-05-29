from flask import Flask
import sqlite3

# 1. 实例化 Flask 应用（也就是召唤一台服务器）
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('station.db')
    # 下面这行非常关键！它能让我们像操作 Python 字典一样，通过字段名（如 row['username']）来获取数据
    conn.row_factory = sqlite3.Row 
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

if __name__ == '__main__':
    app.run(debug=True)