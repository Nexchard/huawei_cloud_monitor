import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from src.config import Config
from src.logger import logger

load_dotenv()


class WeworkBot:
    def __init__(self, name, webhook_url=None, enabled=True):
        self.name = name
        self.webhook_url = webhook_url or Config.WECHAT_BOT1_WEBHOOK
        self.enabled = enabled

    def send_message(self, message, message_type='通知', **kwargs):
        """发送消息到企业微信机器人"""
        if not self.enabled:
            return False

        try:
            response = requests.post(
                self.webhook_url,
                json={"msgtype": "markdown", "markdown": {"content": message}}
            )
            if response.status_code == 200:
                logger.info(f"企业微信{message_type}消息发送成功 (机器人: {self.name})")
                return True
            else:
                logger.error(f"企业微信{message_type}消息发送失败 (机器人: {self.name}): {response.text}")
                return False
        except Exception as e:
            logger.error(f"企业微信{message_type}消息发送异常 (机器人: {self.name}): {str(e)}")
            return False


class WeworkNotification:
    def __init__(self):
        self.enabled = Config.WEWORK_ENABLED
        self.send_to_all = Config.WEWORK_SEND_TO_ALL
        self.default_bot = Config.WEWORK_DEFAULT_BOT
        self.alert_days = Config.RESOURCE_ALERT_DAYS
        
        # 初始化机器人
        self.bots = {}
        if Config.WEWORK_BOT1_ENABLED:
            self.bots[Config.WECHAT_BOT1_NAME] = WeworkBot(
                name=Config.WECHAT_BOT1_NAME,
                webhook_url=Config.WECHAT_BOT1_WEBHOOK,
                enabled=True
            )

    def send_message(self, message, bot_name=None):
        """发送消息到企业微信"""
        if not self.enabled:
            logger.info("企业微信通知未启用")
            return False

        if not self.bots:
            logger.warning("没有可用的企业微信机器人")
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
            try:
                response = requests.post(
                    bot.webhook_url,
                    json={"msgtype": "markdown", "markdown": {"content": message}}
                )
                if response.status_code == 200:
                    logger.info(f"企业微信消息发送成功 (机器人: {bot.name})")
                    success = True
                else:
                    logger.error(f"企业微信消息发送失败 (机器人: {bot.name}): {response.text}")
            except Exception as e:
                logger.error(f"企业微信消息发送异常 (机器人: {bot.name}): {str(e)}")

        return success

    def format_balance_message(self, accounts_data):
        """格式化所有账号的余额信息为markdown消息"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = [
            f"## 💰 华为云账户余额汇总",
            f"生成时间：{current_time}\n"
        ]
        
        for account_data in accounts_data:
            account_name = account_data['account_name']
            balance = account_data.get('balance')
            if balance:
                message.append(f"### 账号：{account_name}")
                message.append(f"> **当前余额**：{balance['total_amount']} {balance['currency']}\n")
        
        return "\n".join(message) 

    def format_resource_message(self, account_name, services):
        """格式化单个账号的资源信息为markdown消息"""
        message = [
            f"## 📢 华为云资源到期提醒",
            f"### 账号：<font color='info'>{account_name}</font>"
        ]
        
        has_alert = False
        for service_type, resources in services.items():
            service_resources = []
            for resource in resources:
                expire_time = resource['expire_time'].replace('T', ' ').replace('Z', '')
                remaining_days = resource['remaining_days']
                
                if remaining_days <= self.alert_days:
                    has_alert = True
                    if remaining_days <= 15:
                        days_color = "warning"  # 橙红色
                    elif remaining_days <= 30:
                        days_color = "info"  # 绿色
                    else:
                        days_color = "comment"    # 灰色
                           
                    resource_info = [
                        f"**名称**：{resource['name']}",
                        f"**区域**：{resource['region']}",
                        f"**到期时间**：{expire_time}",
                        f"**剩余天数**：<font color='{days_color}'>{remaining_days}天</font>"
                    ]
                    
                    if resource['project']:
                        resource_info.append(f"**企业项目**：{resource['project']}")
                        
                    service_resources.append("> " + "\n> ".join(resource_info) + "\n")
            
            if service_resources:
                message.append(f"### {service_type}")
                message.extend(service_resources)
        
        if not has_alert:
            message.append(f"\n> 没有 {self.alert_days} 天内到期的资源")
            return None
        
        return "\n".join(message) 

    def send_long_message(self, content, account_index=None, max_length=4096):
        """将长消息分段发送"""
        if not self.enabled:
            print("企业微信通知未启用")
            return False

        if not content:
            return False

        # 分段发送消息
        parts = [content[i:i+max_length] for i in range(0, len(content), max_length)]
        for part in parts:
            self.send_message(part, account_index) 

    def send_balance_notification(self, accounts_data):
        """发送余额信息通知"""
        balance_message = self.format_balance_message(accounts_data)
        if balance_message:
            for bot in self.bots.values():
                bot.send_message(balance_message, message_type='余额')

    def send_resource_notification(self, account_name, resources):
        """发送资源信息通知"""
        resource_message = self.format_resource_message(account_name, resources)
        if resource_message:
            for bot in self.bots.values():
                bot.send_message(resource_message, message_type='资源') 