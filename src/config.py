import os
from dotenv import load_dotenv
from src.logger import logger

# 加载环境变量
load_dotenv()

class Config:
    # 数据库配置
    ENABLE_DATABASE = os.getenv('ENABLE_DATABASE', 'false').lower() == 'true'
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'huaweicloud_monitor')

    # 企业微信配置
    WEWORK_ENABLED = os.getenv('WEWORK_ENABLED', 'false').lower() == 'true'
    WEWORK_SEND_TO_ALL = os.getenv('WEWORK_SEND_TO_ALL', 'false').lower() == 'true'
    WEWORK_DEFAULT_BOT = os.getenv('WEWORK_DEFAULT_BOT', '')
    
    # 企业微信机器人配置
    WECHAT_BOT1_NAME = os.getenv('WECHAT_BOT1_NAME', '')
    WECHAT_BOT1_WEBHOOK = os.getenv('WECHAT_BOT1_WEBHOOK', '')
    WEWORK_BOT1_ENABLED = os.getenv('WEWORK_BOT1_ENABLED', 'false').lower() == 'true'

    # 邮件配置
    SMTP_ENABLED = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
    SMTP_SERVER = os.getenv('SMTP_SERVER', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', '')
    SMTP_TO = os.getenv('SMTP_TO', '').split(',')
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'true').lower() == 'true'

    # 资源告警配置
    RESOURCE_ALERT_DAYS = int(os.getenv('RESOURCE_ALERT_DAYS', '65'))

    # 云之家配置
    YUNZHIJIA_ENABLED = os.getenv('YUNZHIJIA_ENABLED', 'false').lower() == 'true'
    YUNZHIJIA_SEND_TO_ALL = os.getenv('YUNZHIJIA_SEND_TO_ALL', 'false').lower() == 'true'
    YUNZHIJIA_DEFAULT_BOT = os.getenv('YUNZHIJIA_DEFAULT_BOT', '')
    
    # 云之家机器人配置
    YUNZHIJIA_BOT1_NAME = os.getenv('YUNZHIJIA_BOT1_NAME', '')
    YUNZHIJIA_BOT1_WEBHOOK = os.getenv('YUNZHIJIA_BOT1_WEBHOOK', '')
    YUNZHIJIA_BOT1_ENABLED = os.getenv('YUNZHIJIA_BOT1_ENABLED', 'false').lower() == 'true'

    @classmethod
    def log_config(cls):
        """输出配置信息到日志"""
        logger.info("=== 配置信息 ===")
        
        # 数据库配置日志
        if cls.ENABLE_DATABASE:
            logger.info(f"数据库连接信息: {cls.DB_HOST}:{cls.DB_PORT}")
            logger.info(f"数据库名称: {cls.DB_NAME}")
        else:
            logger.info("数据库功能未启用")

        # 企业微信配置日志
        if cls.WEWORK_ENABLED:
            logger.info("企业微信通知已启用")
            logger.info(f"默认机器人: {cls.WEWORK_DEFAULT_BOT}")
            if cls.WEWORK_SEND_TO_ALL:
                logger.info("发送给所有机器人: 是")
        else:
            logger.info("企业微信通知未启用")

        # 邮件配置日志
        if cls.SMTP_ENABLED:
            logger.info("邮件通知已启用")
            logger.info(f"SMTP服务器: {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
            logger.info(f"发件人: {cls.SMTP_FROM}")
            logger.info(f"收件人: {', '.join(cls.SMTP_TO)}")
        else:
            logger.info("邮件通知未启用")

        # 告警配置日志
        logger.info(f"资源告警天数: {cls.RESOURCE_ALERT_DAYS}")

        # 云之家配置日志
        if cls.YUNZHIJIA_ENABLED:
            logger.info("云之家通知已启用")
            logger.info(f"默认机器人: {cls.YUNZHIJIA_DEFAULT_BOT}")
            if cls.YUNZHIJIA_SEND_TO_ALL:
                logger.info("发送给所有机器人: 是")
        else:
            logger.info("云之家通知未启用")

        logger.info("===============")

    @classmethod
    def validate_config(cls):
        """验证配置的有效性"""
        if cls.ENABLE_DATABASE:
            if not all([cls.DB_HOST, cls.DB_USER, cls.DB_PASSWORD, cls.DB_NAME]):
                logger.error("数据库配置不完整")
                return False

        if cls.WEWORK_ENABLED:
            if not cls.WECHAT_BOT1_WEBHOOK:
                logger.error("企业微信机器人webhook未配置")
                return False

        if cls.SMTP_ENABLED:
            if not all([cls.SMTP_SERVER, cls.SMTP_USERNAME, cls.SMTP_PASSWORD, 
                       cls.SMTP_FROM, cls.SMTP_TO]):
                logger.error("邮件配置不完整")
                return False

        return True 