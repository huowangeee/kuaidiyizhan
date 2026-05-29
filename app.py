from flask import Flask

# 1. 实例化 Flask 应用（也就是召唤一台服务器）
app = Flask(__name__)

# 2. 定义路由 (Routing) - 绑定网址与操作
@app.route('/')
def home():
    return "启动成功"

# 3. 启动服务器
if __name__ == '__main__':
    app.run(debug=True)