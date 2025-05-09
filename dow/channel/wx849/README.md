# WX849 通道

这是一个基于wx849协议的微信机器人通道实现，用于对接DoW平台。

## 文件结构

- `wx849_channel.py`: 通道主文件，负责通道的初始化、消息收发、会话管理等
- `wx849_message.py`: 消息处理文件，处理各类微信消息的解析和格式化

## 功能特点

- 支持私聊和群聊消息
- 支持文本、图片、语音等多种消息类型
- 自动处理群系统消息（如入群、退群通知）
- 支持849、855、ipad等不同协议版本
- 健壮的错误处理和重连机制
- 日志记录详细

## 配置说明

在`config.json`中可以配置以下参数：

```json
{
  "wx849_api_host": "127.0.0.1",    // wx849服务器地址
  "wx849_api_port": 9000,           // wx849服务器端口
  "wx849_protocol_version": "849",  // 协议版本，可选值：849、855、ipad
  "expires_in_seconds": 3600        // 消息过期时间
}
```

## 使用方法

1. 确保wx849服务已启动
2. 在配置文件中启用wx849通道
3. 启动DoW程序
4. 通过控制台提示扫码登录微信

## 代码说明

- `WX849Channel`: 通道主类，处理消息收发
- `WX849Message`: 消息处理类，负责消息的解析和格式化
- `_check`: 装饰器函数，用于过滤重复消息和过期消息

## 常见问题

1. 如果遇到连接问题，请检查wx849服务是否正常运行
2. 如果消息解析错误，可能是不同协议版本消息格式不一致导致
3. 如果遇到"logger is not defined"错误，请确保所有Client文件都正确导入了logger 