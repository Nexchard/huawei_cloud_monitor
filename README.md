# 华为云资源监控系统

## 功能概述
该系统用于监控华为云账号的资源使用情况，包括：
1. 资源到期提醒
2. 账户余额查询
3. 按需计费账单查询
4. 储值卡信息查询

## 项目简介
该系统用于监控多个华为云账号的资源使用情况和账户余额，并通过企业微信和邮件发送告警通知。

## 功能特性
- 多账号管理：支持同时监控多个华为云账号
- 资源监控：追踪各类云资源的到期时间
- 余额监控：实时监控账户余额
- 历史记录：保存资源和余额的历史变化
- 多渠道通知：支持企业微信、云之家和邮件通知
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
    ├── yunzhijia_notification.py  # 云之家通知
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
### 环境变量配置 (.env)
1. 华为云账户配置
```
ACCOUNT1_NAME=账号名称
ACCOUNT1_AK=Access Key
ACCOUNT1_SK=Secret Key
```

2. 数据库配置
```
ENABLE_DATABASE=true/false
DB_HOST=数据库主机
DB_PORT=数据库端口
DB_USER=数据库用户名
DB_PASSWORD=数据库密码
DB_NAME=数据库名称
```

3. 通知配置
- 企业微信配置
```
WEWORK_ENABLED=true/false
WEWORK_DEFAULT_BOT=默认机器人名称
WECHAT_BOT1_NAME=机器人名称
WECHAT_BOT1_WEBHOOK=Webhook地址
```

- 云之家配置
```
YUNZHIJIA_ENABLED=true/false
YUNZHIJIA_DEFAULT_BOT=默认机器人名称
YUNZHIJIA_BOT1_NAME=机器人名称
YUNZHIJIA_BOT1_WEBHOOK=Webhook地址
```

- 邮件配置
```
SMTP_ENABLED=true/false
SMTP_SERVER=SMTP服务器
SMTP_PORT=SMTP端口
SMTP_USERNAME=邮箱用户名
SMTP_PASSWORD=邮箱密码
SMTP_FROM=发件人地址
SMTP_TO=收件人地址列表(逗号分隔)
```

## 数据库表结构

### 资源表 (resources)
```sql
字段说明见 sql/create_resources_table.sql
```

### 余额表 (account_balances)
```sql
字段说明见 sql/create_balances_table.sql
```

### 账单表 (account_bills)
```sql
字段说明见 sql/create_bills_table.sql
```

### 储值卡表 (stored_cards)
```sql
字段说明见 sql/create_stored_cards_table.sql
```

## 通知内容

### 资源到期提醒
- 显示即将到期的资源信息
- 包含资源名称、区域、到期时间、剩余天数等
- 按服务类型分组展示

### 余额通知
- 显示所有账号的现金余额
- 显示所有账号的储值卡信息
  - 储值卡名称
  - 储值卡余额
  - 储值卡面值
  - 储值卡有效期

### 账单通知
- 显示所有账号的按需计费账单信息
- 不包含金额为0的记录
- 不包含子客户的账单
- 按账号和项目分组展示
- 包含服务类型、区域和消费金额

## 通知格式
1. 企业微信：使用 markdown 格式，支持标题、加粗等样式
2. 云之家：使用文本格式，使用特殊字符分隔不同部分
3. 邮件：使用 HTML 格式，支持样式和附件

## 运行方式
```bash
python main.py
```

## 注意事项
1. 确保所有必要的环境变量都已正确配置
2. 数据库需要提前创建并授予适当权限
3. 通知机器人的 webhook 地址需要确保有效
4. 建议通过定时任务定期执行脚本
5. 数据库表会自动检查并创建缺失的表

## 数据批次
- 所有数据表都包含 batch_number 字段
- 格式为 YYYYMMDDHHmmss
- 用于追踪同一批次的数据
- 便于数据分析和问题排查

## 告警规则
- 资源到期提醒：默认提前65天告警
- 告警等级：
  - 剩余15天内：高危警告
  - 剩余30天内：中度警告
  - 剩余65天内：提前提醒

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

4. 云之家通知失败
   - 检查webhook地址是否正确
   - 确认机器人是否启用
   - 验证token是否有效

## 更新日志
### v1.2.0 (2024-01-23)
- 添加储值卡信息查询和展示
- 优化余额通知格式
- 添加数据表自动检查和创建功能
- 添加数据批次追踪功能

### v1.1.0 (2024-01-19)
- 添加云之家通知支持
- 优化消息格式
- 支持余额汇总和资源分别通知

### v1.0.0 (2024-01-13)
- 初始版本发布
- 支持多账号监控
- 实现企业微信和邮件通知
- 添加资源和余额历史记录功能 