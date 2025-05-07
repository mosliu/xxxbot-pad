import os
import sys
import json
import time
from typing import List, Optional
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from datetime import datetime
from pathlib import Path

# 确保当前目录在sys.path中
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 配置logger格式，添加文件名和行号
logger.remove()  # 移除默认处理器
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{line}</cyan> | {message}",
    level="INFO"
)
logger.add(
    "logs/api_service_{time}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
    rotation="1 day",
    retention="7 days",
    level="DEBUG"
)

# 导入路由
from message_api import register_message_routes

# 全局变量
app = FastAPI(title="API服务")
bot_instance = None
config = {
    "host": "0.0.0.0",
    "port": 18888,
    "secret_key": "your_secret_key_here",
    "debug": False
}

# 全局变量，用于跟踪服务器是否已启动
SERVER_RUNNING = False
SERVER_THREAD = None

# 设置模板目录
templates_path = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_path)

def set_bot_instance(bot):
    """设置bot实例供其他模块使用"""
    global bot_instance
    bot_instance = bot
    logger.info("API服务已设置bot实例")
    return bot_instance

def get_bot_instance():
    """获取bot实例"""
    global bot_instance
    if bot_instance is None:
        logger.warning("bot实例未设置")
    return bot_instance

# 加载配置
def load_config():
    global config
    try:
        # 从main_config.toml读取配置
        main_config_path = os.path.join(os.path.dirname(current_dir), "main_config.toml")
        if os.path.exists(main_config_path):
            with open(main_config_path, "rb") as f:
                try:
                    import tomllib
                except ImportError:
                    import tomli as tomllib
                main_config = tomllib.load(f)
                if "ApiService" in main_config:
                    api_config = main_config["ApiService"]
                    # 更新配置
                    if "host" in api_config:
                        config["host"] = api_config["host"]
                    if "port" in api_config:
                        config["port"] = api_config["port"]
                    if "secret_key" in api_config:
                        config["secret_key"] = api_config["secret_key"]
                    if "debug" in api_config:
                        config["debug"] = api_config["debug"]
                    logger.info(f"从main_config.toml加载API服务配置: {main_config_path}")
                else:
                    logger.warning("main_config.toml中未找到ApiService配置，使用默认配置")
        else:
            logger.warning(f"未找到配置文件: {main_config_path}，使用默认配置")

        # 从环境变量中读取配置（优先级最高）
        if "API_SECRET_KEY" in os.environ:
            config["secret_key"] = os.environ["API_SECRET_KEY"]
            logger.info("从环境变量API_SECRET_KEY加载密钥")

        if "API_HOST" in os.environ:
            config["host"] = os.environ["API_HOST"]
            logger.info("从环境变量API_HOST加载主机配置")

        if "API_PORT" in os.environ and os.environ["API_PORT"].isdigit():
            config["port"] = int(os.environ["API_PORT"])
            logger.info("从环境变量API_PORT加载端口配置")

        if "API_DEBUG" in os.environ:
            debug_value = os.environ["API_DEBUG"].lower()
            config["debug"] = debug_value in ("true", "1", "yes")
            logger.info("从环境变量API_DEBUG加载调试模式配置")

    except Exception as e:
        logger.error(f"加载API服务配置失败: {str(e)}")
        logger.warning("使用默认配置")

# 安全验证中间件
async def verify_api_key(request: Request):
    """验证API密钥 - 使用Bearer认证方式"""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 检查认证头格式
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="认证格式无效，应为'Bearer TOKEN'",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 验证令牌
    token = parts[1]
    if token != config["secret_key"]:
        raise HTTPException(
            status_code=401,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return True

# 初始化应用
def init_app():
    """初始化FastAPI应用"""
    # 加载配置
    load_config()
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 挂载静态文件目录
    static_path = os.path.join(current_dir, "statics")
    if os.path.exists(static_path):
        app.mount("/statics", StaticFiles(directory=static_path), name="statics")
    else:
        logger.warning(f"静态文件目录不存在: {static_path}")
    
    # 注册消息API路由
    register_message_routes(app, verify_api_key, get_bot_instance)
    
    # 添加健康检查端点
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "ok", "service": "API服务"}
    
    # 添加首页路由
    @app.get("/", response_class=HTMLResponse)
    async def index_page(request: Request):
        """API服务首页"""
        server_host = f"{config['host']}:{config['port']}"
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "server_host": server_host
            }
        )
    
    return app

# 启动服务器
def start_server(host_arg=None, port_arg=None, debug_arg=None, bot=None):
    """启动API服务器"""
    global SERVER_RUNNING, SERVER_THREAD, bot_instance, config
    
    # 检查服务器是否已经在运行
    if SERVER_RUNNING and SERVER_THREAD and SERVER_THREAD.is_alive():
        logger.warning("API服务器已经在运行中，跳过重复启动")
        # 如果有新的bot实例，仍然需要设置
        if bot is not None:
            set_bot_instance(bot)
        return SERVER_THREAD
    
    # 设置bot实例
    if bot is not None:
        set_bot_instance(bot)
    
    # 加载配置
    load_config()
    
    # 更新配置
    if host_arg is not None:
        config["host"] = host_arg
    if port_arg is not None:
        config["port"] = port_arg
    if debug_arg is not None:
        config["debug"] = debug_arg
    
    # 初始化应用
    init_app()
    
    # 在新线程中启动服务器
    def run_server():
        try:
            import uvicorn
            logger.info(f"启动API服务器: {config['host']}:{config['port']}")
            uvicorn.run(
                app,
                host=config["host"],
                port=config["port"],
                log_level="debug" if config["debug"] else "info"
            )
        except Exception as e:
            logger.error(f"启动服务器时出错: {str(e)}")
            global SERVER_RUNNING
            SERVER_RUNNING = False
    
    # 创建并启动线程
    import threading
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 更新全局状态
    SERVER_RUNNING = True
    SERVER_THREAD = server_thread
    
    # 创建状态文件
    try:
        status_path = os.path.join(current_dir, "api_service_status.txt")
        with open(status_path, "w", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"主机: {config['host']}:{config['port']}\n")
            f.write(f"状态: 运行中\n")
    except Exception as e:
        logger.error(f"创建状态文件失败: {str(e)}")
    
    logger.success(f"API服务器已启动，运行在 http://{config['host']}:{config['port']}")
    return server_thread

# 停止服务器
def stop_server():
    """停止API服务器"""
    global SERVER_RUNNING, SERVER_THREAD
    
    if not SERVER_RUNNING:
        logger.warning("API服务器未运行")
        return
    
    # 停止服务器
    SERVER_RUNNING = False
    logger.info("API服务器已停止")

# 如果直接运行此脚本，则启动服务器
if __name__ == "__main__":
    import threading
    start_server()
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_server()