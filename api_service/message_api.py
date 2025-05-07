from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from loguru import logger

# 创建路由器
router = APIRouter(prefix="", tags=["消息"])

# 全局变量
check_auth = None
get_bot_instance = None

# 消息请求模型
class MessageRequest(BaseModel):
    room_id: str
    text: str
    at_users: Optional[str] = ""
    message_type: Optional[str] = "text"  # text, image, file, etc.
    extra_data: Optional[Dict[str, Any]] = None

# 注册路由
def register_message_routes(app, auth_func, bot_instance_func):
    """
    注册消息相关路由

    Args:
        app: FastAPI应用实例
        auth_func: 认证检查函数
        bot_instance_func: 获取bot实例的函数
    """
    global check_auth, get_bot_instance
    check_auth = auth_func
    get_bot_instance = bot_instance_func

    # 注册路由
    app.include_router(router)

# API路由
@router.post("/push")
async def send_message(request: Request, message: MessageRequest):
    """
    发送消息API

    Args:
        request: 请求对象
        message: 消息请求对象

    Returns:
        JSONResponse: 发送结果
    """
    try:
        # 检查认证状态
        await check_auth(request)

        # 获取bot实例
        bot = get_bot_instance()
        if not bot:
            return JSONResponse(status_code=500, content={"success": False, "error": "机器人未初始化"})

        # 根据消息类型发送不同类型的消息
        if message.message_type == "text":
            # 发送文本消息
            result = await bot.bot.send_text_message(message.room_id, message.text, message.at_users)
            
            return JSONResponse(
                content={
                    "success": True,
                    "message": "消息发送成功",
                    "data": {
                        "client_msg_id": result[0],
                        "create_time": result[1],
                        "new_msg_id": result[2]
                    }
                }
            )
        # elif message.message_type == "image":
        #     # 发送图片消息
        #     if not message.extra_data or "image_path" not in message.extra_data:
        #         return JSONResponse(status_code=400, content={"success": False, "error": "发送图片需要提供image_path"})
        #
        #     image_path = message.extra_data["image_path"]
        #     result = await bot.bot.send_image(message.to_wxid, image_path)
        #
        #     return JSONResponse(
        #         content={
        #             "success": True,
        #             "message": "图片发送成功",
        #             "data": result
        #         }
        #     )
        # elif message.message_type == "file":
        #     # 发送文件消息
        #     if not message.extra_data or "file_path" not in message.extra_data:
        #         return JSONResponse(status_code=400, content={"success": False, "error": "发送文件需要提供file_path"})
        #
        #     file_path = message.extra_data["file_path"]
        #     result = await bot.bot.send_file(message.to_wxid, file_path)
        #
        #     return JSONResponse(
        #         content={
        #             "success": True,
        #             "message": "文件发送成功",
        #             "data": result
        #         }
        #     )
        else:
            return JSONResponse(status_code=400, content={"success": False, "error": f"不支持的消息类型: {message.message_type}"})
            
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"success": False, "error": e.detail})
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("/batch_send")
async def batch_send_message(request: Request, messages: List[MessageRequest]):
    """
    批量发送消息API

    Args:
        request: 请求对象
        messages: 消息请求对象列表

    Returns:
        JSONResponse: 发送结果
    """
    try:
        # 检查认证状态
        await check_auth(request)

        # 获取bot实例
        bot = get_bot_instance()
        if not bot:
            return JSONResponse(status_code=500, content={"success": False, "error": "机器人未初始化"})

        results = []
        for message in messages:
            try:
                # 根据消息类型发送不同类型的消息
                if message.message_type == "text":
                    # 发送文本消息
                    result = await bot.bot.send_text_message(message.to_wxid, message.content, message.at_users)
                    results.append({
                        "to_wxid": message.to_wxid,
                        "success": True,
                        "data": {
                            "client_msg_id": result[0],
                            "create_time": result[1],
                            "new_msg_id": result[2]
                        }
                    })
                elif message.message_type == "image":
                    # 发送图片消息
                    if not message.extra_data or "image_path" not in message.extra_data:
                        results.append({
                            "to_wxid": message.to_wxid,
                            "success": False,
                            "error": "发送图片需要提供image_path"
                        })
                        continue
                    
                    image_path = message.extra_data["image_path"]
                    result = await bot.bot.send_image(message.to_wxid, image_path)
                    results.append({
                        "to_wxid": message.to_wxid,
                        "success": True,
                        "data": result
                    })
                elif message.message_type == "file":
                    # 发送文件消息
                    if not message.extra_data or "file_path" not in message.extra_data:
                        results.append({
                            "to_wxid": message.to_wxid,
                            "success": False,
                            "error": "发送文件需要提供file_path"
                        })
                        continue
                    
                    file_path = message.extra_data["file_path"]
                    result = await bot.bot.send_file(message.to_wxid, file_path)
                    results.append({
                        "to_wxid": message.to_wxid,
                        "success": True,
                        "data": result
                    })
                else:
                    results.append({
                        "to_wxid": message.to_wxid,
                        "success": False,
                        "error": f"不支持的消息类型: {message.message_type}"
                    })
            except Exception as e:
                results.append({
                    "to_wxid": message.to_wxid,
                    "success": False,
                    "error": str(e)
                })
        
        return JSONResponse(
            content={
                "success": True,
                "message": "批量发送消息完成",
                "results": results
            }
        )
            
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"success": False, "error": e.detail})
    except Exception as e:
        logger.error(f"批量发送消息失败: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})