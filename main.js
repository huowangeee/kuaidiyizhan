const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 850,
        title: "快递驿站管理系统 - 桌面版",
        icon: path.join(__dirname, 'favicon.ico'), // 如果有图标可以加上
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        autoHideMenuBar: true // 隐藏顶部的丑陋菜单栏
    });

    // 加载我们写好的本地页面
    mainWindow.loadFile(path.join(__dirname, 'index.html'));

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    // 核心科技：根据环境智能拉起后端服务
    if (app.isPackaged) {
        // 生产环境（打包后）：使用 electron-packager 路径
        const serverPath = path.join(__dirname, 'backend-dist', 'app.exe');
        pythonProcess = spawn(serverPath, []);
    } else {
        // 开发环境：直接跑 Python 代码
        pythonProcess = spawn('python', ['app.py'], {
            cwd: __dirname
        });
    }

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Flask] ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Flask Error] ${data}`);
    });

    // 延迟 1 秒，等待 Flask 启动完毕后再打开窗口
    setTimeout(() => {
        createWindow();
    }, 1000);
    
    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

// 所有的窗口关闭时触发
app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// 安全护航：在应用程序彻底退出前，把挂靠的 Python 进程强行杀掉，防止端口被锁死
app.on('before-quit', () => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
});
