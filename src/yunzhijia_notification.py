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
        """格式化所有账号的余额信息为文本消息"""
        message = ["华为云账户余额汇总"]
        
        for account_data in accounts_data:
            account_name = account_data['account_name']
            balance = account_data.get('balance')
            stored_cards = account_data.get('stored_cards')
            
            if balance or stored_cards:
                message.extend([
                    "",
                    f"======= {account_name} ======="
                ])
                if balance:
                    message.append(f"现金余额: {balance['total_amount']} {balance['currency']}")
                
                if stored_cards and stored_cards.get('cards'):
                    for card in stored_cards['cards']:
                        message.append(f"- {card['card_name']}")
                        message.append(f"  余额: {card['balance']} CNY")
                        message.append(f"  面值: {card['face_value']} CNY")
                        message.append(f"  有效期至: {card['expire_time'].replace('T', ' ').replace('Z', '')}")
        
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

    def format_bill_message(self, accounts_data):
        """格式化所有账号的账单信息为文本消息"""
        message = ["华为云按需计费账单汇总"]
        
        for account_data in accounts_data:
            account_name = account_data['account_name']
            bills = account_data.get('bills')
            if bills and bills.get('records'):
                message.extend([
                    "",
                    f"======= {account_name} =======",
                    f"总金额: {bills['total_amount']} {bills['currency']}"
                ])
                
                # 按项目分组展示
                projects = {}
                for record in bills['records']:
                    project = record['project_name'] or 'default'
                    if project not in projects:
                        projects[project] = []
                    projects[project].append(record)
                
                for project, records in projects.items():
                    message.append(f"\n项目: {project}")
                    for record in records:
                        record_info = [
                            f"服务类型: {record['service_type']}",
                            f"区域: {record['region']}",
                            f"金额: {record['amount']} {bills['currency']}"
                        ]
                        message.append("\n".join(record_info))
                    message.append("")  # 添加空行分隔不同项目
        
        return "\n".join(message).rstrip()

    def send_bill_notification(self, accounts_data):
        """发送账单信息通知"""
        bill_message = self.format_bill_message(accounts_data)
        if bill_message:
            self.send_message(bill_message) 