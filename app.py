from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import os

# 1. 实例化 Flask 应用
app = Flask(__name__)
CORS(app)

# 定义数据存储目录 (Windows 默认在 AppData/Roaming/kuaidiyizhan)
DATA_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'kuaidiyizhan')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, 'station.db')
CONFIG_PATH = os.path.join(DATA_DIR, 'config.json')
MOCK_DATA_PATH = os.path.join(DATA_DIR, 'mock_data.json')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        );
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
    admin = cursor.execute("SELECT * FROM user WHERE username='admin'").fetchone()
    if not admin:
        cursor.execute("INSERT INTO user (username, password, role) VALUES ('admin', '123456', 'admin')")
    conn.commit()
    conn.close()

    if not os.path.exists(MOCK_DATA_PATH):
        default_mock_data = {
            "YT123456": {"recipient_name": "张三", "phone_number": "13800138000"},
            "ZT654321": {"recipient_name": "李四", "phone_number": "13912345678"},
            "SF987654": {"recipient_name": "王五", "phone_number": "15898765432"},
            "JD111222": {"recipient_name": "赵六", "phone_number": "18611112222"},
            "YD333444": {"recipient_name": "孙七", "phone_number": "19933334444"}
        }
        with open(MOCK_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_mock_data, f, ensure_ascii=False, indent=2)

# 启动前自动初始化数据库
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
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

# --- 新增：智能拉取物流信息 Mock 接口 ---
@app.route('/api/mock-info/<tracking_number>', methods=['GET'])
def get_mock_info(tracking_number):
    try:
        # 如果文件不存在，返回空
        if not os.path.exists(MOCK_DATA_PATH):
            return jsonify({"success": False, "message": "未查询到上游数据"})
        
        # 打开并读取 json 文件
        with open(MOCK_DATA_PATH, 'r', encoding='utf-8') as f:
            mock_data = json.load(f)
            
        # 查找对应的单号数据
        if tracking_number in mock_data:
            return jsonify({
                "success": True,
                "data": mock_data[tracking_number]
            })
        else:
            return jsonify({
                "success": False,
                "message": "未查询到上游数据"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"服务器内部错误: {str(e)}"
        }), 500
# --- 新增：读取和更新系统配置接口 ---
@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        if not os.path.exists(CONFIG_PATH):
            # 如果配置文件不存在，返回一个默认的配置，并写入文件
            default_config = {"maxShelf": 100, "maxLayer": 10, "maxTail": 9999}
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_config, f)
            return jsonify(default_config)
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['PUT'])
def update_config():
    try:
        data = request.get_json()
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return jsonify({"success": True, "message": "配置已成功保存！"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
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

# --- 新增：包裹删除接口 ---
@app.route('/api/express/<int:id>', methods=['DELETE'])
def delete_express(id):
    # 1. 获取数据库连接
    conn = get_db_connection()
    
    # 2. 执行 DELETE 语句，根据 id 从数据库中彻底删除该条记录
    conn.execute('DELETE FROM express WHERE id = ?', (id,))
    
    # 3. 提交并关闭连接
    conn.commit()
    conn.close()
    
    # 4. 返回成功提示
    return jsonify({"message": "包裹已永久删除！", "status": "success"})
# --------------------------------

# --- 新增：用户登录接口 ---
@app.route('/api/login', methods=['POST'])
def login():
    # 1. 接收前端传来的账号密码
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 2. 查询数据库进行比对
    conn = get_db_connection()
    # 查找是否有匹配的账号和密码
    user = conn.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    
    # 3. 根据比对结果返回响应
    if user:
        # 如果找到了，说明账号密码正确
        return jsonify({
            "status": "success", 
            "message": "登录成功！",
            "user": {
                "username": user['username'],
                "role": user['role']
            }
        })
    else:
        # 如果没找到，说明账号或密码错误
        # 401 代表 Unauthorized (未授权)
        return jsonify({"status": "error", "message": "账号或密码错误！"}), 401
# --------------------------------

# --- 新增：员工管理接口 (CRUD) ---
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, role, password FROM user').fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'employee')
    
    conn = get_db_connection()
    # 检查用户名是否已存在
    existing = conn.execute('SELECT id FROM user WHERE username = ?', (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({"success": False, "message": "该账号已存在！"}), 400
        
    conn.execute('INSERT INTO user (username, password, role) VALUES (?, ?, ?)', (username, password, role))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "添加员工成功！"})

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "message": "账号不存在！"}), 404
        
    conn.execute('UPDATE user SET password = ? WHERE id = ?', (password, id))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "密码修改成功！"})

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({"success": False, "message": "账号不存在！"}), 404
    if user['username'] == 'admin':
        conn.close()
        return jsonify({"success": False, "message": "安全限制：不能删除超级管理员账号！"}), 403
        
    conn.execute('DELETE FROM user WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "账号已永久删除！"})
# --------------------------------

if __name__ == '__main__':
    app.run(debug=True)