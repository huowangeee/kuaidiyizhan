# 📦 快递驿站管理系统 (Kuaidi Station Manager)

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Frontend](https://img.shields.io/badge/Frontend-Vue.js%203-4FC08D)
![Backend](https://img.shields.io/badge/Backend-Python%20Flask-000000)
![Desktop](https://img.shields.io/badge/Desktop-Electron-47848F)

这是一个专为“快递驿站”场景打造的**现代化跨语言微服务桌面客户端**。

本项目摒弃了传统的“Web代码+文档运行说明”的原始交付方式，采用 **Electron + PyInstaller** 实现了 Python 后端的隐式嵌入与跨端融合，做到真正的**下载即用，零配置运行**，达到了商业级软件的交付标准。

---

## ✨ 核心特性 (Features)

- ⚡ **开箱即用的桌面级体验**：依托 Electron 容器，主进程智能调度 `child_process` 静默拉起底层 Python 服务，无惧端口死锁，进程生命周期绝对安全。
- 🛡️ **微服务物理打包**：使用 PyInstaller 深度编译 Flask 后端引擎及运行环境，并在 Python 内核中实现了基于 `%APPDATA%` 动态环境变量的数据沙盒隔离，彻底解决权限锁死问题。
- 🎨 **企业级 UI/UX 设计**：拒绝传统组件库的堆砌！纯手写 CSS3 现代化交互体系（包含 Glassmorphism 毛玻璃弹窗、流式 Toast 消息列队、CSS状态机底线平滑追踪页签）。
- 🔒 **内置 RBAC 权限引擎**：完整的端到端闭环权限控制，管理员与普通员工享有不同的 UI 渲染策略及数据管控接口，自带防自毁熔断机制。
- ⚙️ **“千人千面”的容量动态配置**：底层不再依靠硬编码，而是通过读取独立化配置流 (`config.json`) 实现驿站容量的灵活缩放。

---

## 🚀 快速体验 (Quick Start)

想要体验该系统，你完全不需要懂编程，也不需要安装任何环境！

1. 前往本仓库的 [Releases 页面](../../releases/latest)。
2. 下载最新的 `快递驿站管理系统-v1.1.0-Windows.zip` 压缩包。
3. 解压后，双击运行绿色的 `快递驿站管理系统.exe` 即可进入系统！
> **默认超级管理员账号**：`admin` 
> **默认密码**：`123456`

---

## 🛠️ 开发者指南 (For Developers)

如果你想对本项目进行二次开发（如课程设计扩展），请按照以下步骤启动本地环境：

### 1. 环境准备
确保你的电脑中已安装以下工具：
- [Node.js](https://nodejs.org/) (用于支持打包与 Electron 环境)
- [Python 3.x](https://www.python.org/) (用于支持后端微服务)

### 2. 克隆项目与安装依赖
```bash
# 1. 克隆项目
git clone https://github.com/huowangeee/kuaidiyizhan.git
cd kuaidiyizhan

# 2. 安装 Python 依赖
pip install flask flask-cors pyinstaller

# 3. 安装 Node.js 依赖
npm install
```

### 3. 开发模式与打包发布
- **进入开发模式**：
  ```bash
  npm start
  ```
  *(注：该命令会自动在后台以 Python 源码模式启动 Flask，并弹出前端调试窗口)*

- **编译并发布 Windows 安装程序**：
  ```bash
  # 第一步：把 Python 后端编译为 exe 库
  pyinstaller --onefile --noconsole --distpath ./backend-dist app.py
  
  # 第二步：将前后端进行缝合打包
  npm run build
  ```
  *(注：打包完成后的独立软件文件夹会输出在项目根目录的 `dist` 文件夹中)*

---

## 📖 技术白皮书与研发日志
如果你对本项目深层的技术原理感兴趣，或者想了解如何解决开发中遇到的同源跨域、Electron 与 Python 通信编排、数据库环境挂载等难题，可以查阅我编写的内部技术文档：
- 📄 [《技术白皮书与架构解析》](./TECHNICAL_DOCUMENT.md)
- 📝 [《开发历程迭代日志》](./DEVVLOG.md)
