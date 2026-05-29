from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

# 1. 实例化 Flask 应用（也就是召唤一台服务器）
app = Flask(__name__)
CORS(app)

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


# --- 新增：包裹入库接口 ---
@app.route('/api/express', methods=['POST'])
def add_express():
    # 1. 获取前端发来的 JSON 格式数据
    data = request.get_json()
    
    # 2. 从数据中提取各个字段 [cite: 18]
    tracking_number = data.get('tracking_number')
    recipient_name = data.get('recipient_name')
    phone_number = data.get('phone_number')
    pickup_code = data.get('pickup_code')
    arrival_time = data.get('arrival_time')
    status = '待取件'  # 刚入库的包裹，状态默认都是“待取件”
    
    # 3. 连接数据库，执行 INSERT 插入语句 [cite: 15]
    conn = get_db_connection()
    # 注意：这里的 ? 是占位符，能有效防止 SQL 注入攻击，是保障数据库安全的标准写法
    conn.execute('''
        INSERT INTO express (tracking_number, recipient_name, phone_number, pickup_code, status, arrival_time)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tracking_number, recipient_name, phone_number, pickup_code, status, arrival_time))
    
    # 4. 提交保存并关闭连接 [cite: 15]
    conn.commit()
    conn.close()
    
    # 5. 返回成功的提示信息，201 代表 "Created"（创建成功）
    return jsonify({"message": "包裹入库成功！", "status": "success"}), 201
# --------------------------------
    # --- 新增：包裹出库（更新状态）接口 ---
# 注意网址里加上了 <int:id>，它能动态接收前端传来的包裹 ID
@app.route('/api/express/<int:id>/checkout', methods=['PUT'])
def checkout_express(id):
    # 1. 接收前端传来的出库时间
    data = request.get_json()
    pickup_time = data.get('pickup_time')
    
    # 2. 连接数据库，执行 UPDATE 语句
    conn = get_db_connection()
    # 根据包裹的 id，将其状态修改为已签收，并填入签收时间
    conn.execute('''
        UPDATE express
        SET status = '已签收', pickup_time = ?
        WHERE id = ?
    ''', (pickup_time, id))
    
    # 3. 提交并关闭连接
    conn.commit()
    conn.close()
    
    # 4. 返回成功提示
    return jsonify({"message": "包裹出库成功！", "status": "success"})
# --------------------------------

if __name__ == '__main__':
    app.run(debug=True)