大部分运行不上dow的原因.

1. 必须849协议下运行，选择dual
2. 大部分人在下载目录修改配置，这是docker，需要在容器里修改
3. dify不回复，大部分人用了agent，需要用chatflow就行
4. dify_app_type:chatbot不要动这个
5. 扫码登录后没有继续登录按钮换协议，但是除了849以外其他的不一定适配dow框架，还没有测试
6. 855为安卓pad协议，这个协议比较容易封号，主要还是看脸。
7. 不要再页面修改main_config配置文件，容易无法启动容器，最好是进入容器修改。
8. 机器人状态文件:


  - /app/admin/bot_status.json - 管理后台使用的机器人状态文件
  - /app/bot_status.json - 主程序使用的机器人状态文件
  - 账号信息文件:/app/resource/robot_stat.json - 保存微信账号信息，包括昵称、微信ID、微信号等
  - 登录状态文件:/app/WechatAPI/Client/login_stat.json - 保存微信登录状态信息
  - Redis数据:/app/849/redis/appendonlydir - Redis数据持久化目录
  - 头像文件:/app/resource/avatars/ - 保存用户头像的目录
  - 插件数据:/app/plugins/[插件名称]/ - 各个插件的数据目录 例如，Leaderboard插件的积分数据保存在 /app/plugins/Leaderboard/ 目录下
  - 配置文件:/app/main_config.toml - 主配置文件
  - /app/plugins/[插件名称]/config.toml - 各个插件的配置文件
  - 版本信息:/app/version.json - 保存版本信息的文件
