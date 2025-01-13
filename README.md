# 华为云资源监控系统

## 项目简介
该系统用于监控多个华为云账号的资源使用情况和账户余额，并通过企业微信和邮件发送告警通知。

## 功能特性
- 多账号管理：支持同时监控多个华为云账号
- 资源监控：追踪各类云资源的到期时间
- 余额监控：实时监控账户余额
- 历史记录：保存资源和余额的历史变化
- 多渠道通知：支持企业微信和邮件通知
- 自定义告警：可配置资源到期告警天数

## 系统架构
```
huawei_cloud/
├── main.py                 # 主程序入口
├── .env                    # 环境变量配置文件
├── README.md              # 项目说明文档
├── sql/                   # SQL文件目录
│   ├── create_resources_table.sql    # 资源表结构
│   └── create_balances_table.sql     # 余额表结构
└── src/                   # 源代码目录
    ├── config.py          # 配置管理
    ├── db.py             # 数据库操作
    ├── logger.py         # 日志管理
    ├── notification.py   # 企业微信通知
    ├── email_notification.py  # 邮件通知
    ├── resource_query.py  # 资源查询
    └── balance_query.py   # 余额查询
```

## 安装部署
1. 环境要求
   - Python 3.8+
   - MySQL 5.7+

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置文件
复制 `.env.example` 到 `.env` 并填写以下配置：
- 华为云账号信息（AK/SK）
- 数据库连接信息
- 企业微信机器人配置
- 邮件服务器配置
- 告警阈值设置

## 配置说明
### 华为云账号配置
```env
ACCOUNT1_NAME=account1
ACCOUNT1_AK=your_ak
ACCOUNT1_SK=your_sk
```

### 数据库配置
```env
ENABLE_DATABASE=true
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=huaweicloud_monitor
```

### 企业微信配置
```env
WEWORK_ENABLED=true
WEWORK_SEND_TO_ALL=false
WEWORK_DEFAULT_BOT=your_bot_name
WECHAT_BOT1_NAME=bot_name
WECHAT_BOT1_WEBHOOK=webhook_url
```

### 邮件配置
```env
SMTP_ENABLED=true
SMTP_SERVER=smtp.example.com
SMTP_PORT=465
SMTP_USERNAME=your_email
SMTP_PASSWORD=your_password
SMTP_FROM=sender@example.com
SMTP_TO=receiver@example.com
```

## 使用说明
1. 启动监控
```bash
python main.py
```

2. 监控内容
- 资源监控：记录所有资源的到期时间，提前告警
- 余额监控：记录账户余额变化
- 通知功能：当资源即将到期或余额不足时发送通知

3. 数据库表结构
- resources：记录资源信息及历史变化
- account_balances：记录账户余额历史

## 告警规则
- 资源到期提醒：默认提前65天告警
- 告警等级：
  - 剩余15天内：高危警告
  - 剩余30天内：中度警告
  - 剩余65天内：提前提醒

## 注意事项
1. 数据库备份：建议定期备份数据库
2. 密钥安全：请妥善保管华为云AK/SK
3. 权限控制：确保数据库用户具有适当权限
4. 日志管理：定期检查系统日志

## 常见问题
1. 企业微信通知失败
   - 检查webhook地址是否正确
   - 确认机器人是否启用

2. 邮件发送失败
   - 验证SMTP配置是否正确
   - 检查邮箱密码或授权码

3. 数据库连接失败
   - 确认数据库服务是否运行
   - 检查连接信息是否正确

## 更新日志
### v1.0.0 (2025-01-13)
- 初始版本发布
- 支持多账号监控
- 实现企业微信和邮件通知
- 添加资源和余额历史记录功能 