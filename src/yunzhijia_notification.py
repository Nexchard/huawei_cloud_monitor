import os
import requests
from src.config import Config
from src.logger import logger
from datetime import datetime

class YunzhijiaBot:
    def __init__(self, name, webhook_url=None, enabled=True):
        self.name = name
        self.webhook_url = webhook_url
        self.enabled = enabled

    def send_message(self, message, message_type='通知'):
        """发送消息到云之家机器人"""
        if not self.enabled:
            return False

        try:
            # 云之家只支持文本消息
            payload = {
                "content": message
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"云之家{message_type}消息发送成功 (机器人: {self.name})")
                return True
            else:
                logger.error(f"云之家{message_type}消息发送失败 (机器人: {self.name}): {response.text}")
                return False
        except Exception as e:
            logger.error(f"云之家{message_type}消息发送异常 (机器人: {self.name}): {str(e)}")
            return False

class YunzhijiaNotification:
    def __init__(self):
        self.enabled = Config.YUNZHIJIA_ENABLED
        self.send_to_all = Config.YUNZHIJIA_SEND_TO_ALL
        self.default_bot = Config.YUNZHIJIA_DEFAULT_BOT
        self.alert_days = Config.RESOURCE_ALERT_DAYS
        
        # 初始化机器人
        self.bots = {}
        if Config.YUNZHIJIA_BOT1_ENABLED:
            self.bots[Config.YUNZHIJIA_BOT1_NAME] = YunzhijiaBot(
                name=Config.YUNZHIJIA_BOT1_NAME,
                webhook_url=Config.YUNZHIJIA_BOT1_WEBHOOK,
                enabled=True
            )

    def send_message(self, message, bot_name=None):
        """发送消息到云之家"""
        if not self.enabled:
            logger.info("云之家通知未启用")
            return False

        if not self.bots:
            logger.warning("没有可用的云之家机器人")
            return False

        # 确定要使用的机器人
        if bot_name and bot_name in self.bots:
            bots_to_use = [self.bots[bot_name]]
        elif self.send_to_all:
            bots_to_use = list(self.bots.values())
        elif self.default_bot in self.bots:
            bots_to_use = [self.bots[self.default_bot]]
        else:
            bots_to_use = [next(iter(self.bots.values()))]

        success = False
        for bot in bots_to_use:
            if bot.send_message(message):
                success = True

        return success

    def format_balance_message(self, accounts_data):
        """格式化所有账号的余额信息为一条汇总消息"""
        message = ["华为云账户余额汇总"]
        
        for account_data in accounts_data:
            account_name = account_data['account_name']
            balance = account_data.get('balance')
            if balance:
                account_message = [
                    f"======= {account_name} =======",
                    f"当前余额: {balance['total_amount']}{balance['currency']}"
                ]
                message.extend(account_message)
        
        return "\n".join(message)

    def format_resource_message(self, account_name, services):
        """格式化单个账号的资源信息为文本消息"""
        message = [f"华为云 {account_name} 资源到期提醒"]
        
        has_alert = False
        first_service = True
        for service_type, resources in services.items():
            service_resources = []
            for resource in resources:
                remaining_days = resource['remaining_days']
                
                if remaining_days <= self.alert_days:
                    has_alert = True
                    if not service_resources:  # 只在该服务类型的第一个资源前添加标题
                        if first_service:
                            service_resources.append(f"\n======= {service_type} =======")
                            first_service = False
                        else:
                            service_resources.append(f"======= {service_type} =======")
                    
                    expire_time = resource['expire_time'].replace('T', ' ').replace('Z', '')
                    resource_info = [
                        f"名称: {resource['name']}",
                        f"区域: {resource['region']}",
                        f"到期时间: {expire_time}",
                        f"剩余天数: {remaining_days}天"
                    ]
                    
                    if resource['project'] and resource['project'] != '无项目':
                        resource_info.append(f"企业项目: {resource['project']}")
                    
                    service_resources.append("\n".join(resource_info))
            
            if service_resources:
                message.extend(service_resources)
                if service_type != list(services.keys())[-1]:  # 如果不是最后一个服务类型，添加空行
                    message.append("")
        
        if not has_alert:
            return None
        
        return "\n".join(message).rstrip()  # 移除最后的空行

    def send_balance_notification(self, accounts_data):
        """发送汇总的余额信息通知"""
        balance_message = self.format_balance_message(accounts_data)
        if balance_message:
            self.send_message(balance_message)  # 只发送一条汇总消息

    def send_resource_notification(self, account_name, resources):
        """每个账号单独发送资源信息通知"""
        resource_message = self.format_resource_message(account_name, resources)
        if resource_message:
            self.send_message(resource_message)  # 每个账号发送一条消息 