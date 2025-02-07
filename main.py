import logging
import os
from src.config import Config
from src.resource_query import query_resources
from src.balance_query import query_balance
from src.notification import WeworkNotification
from src.email_notification import EmailNotification
from src.db import Database
from src.logger import logger
from dotenv import load_dotenv
from src.yunzhijia_notification import YunzhijiaNotification
from src.bill_query import query_bills
from datetime import datetime
from src.stored_card_query import query_stored_cards
from src.certificate_query import query_certificates

# 加载环境变量
load_dotenv()

def main():
    # 检查是否启用数据库
    enable_database = os.getenv('ENABLE_DATABASE', 'false').lower() == 'true'
    
    if enable_database:
        db = Database()
        logger.info("数据库功能已启用")
    else:
        db = None
        logger.info("数据库功能未启用")
    
    # 初始化通知系统
    wework = WeworkNotification()
    email = EmailNotification()
    yunzhijia = YunzhijiaNotification()
    
    # 记录通知系统状态
    logger.info(f"企业微信通知状态: {'启用' if wework.enabled else '未启用'}")
    logger.info(f"邮件通知状态: {'启用' if email.enabled else '未启用'}")
    logger.info(f"云之家通知状态: {'启用' if yunzhijia.enabled else '未启用'}")
    
    # 获取所有华为云账号配置
    accounts = []
    index = 1
    while True:
        account_name = os.getenv(f'ACCOUNT{index}_NAME')
        ak = os.getenv(f'ACCOUNT{index}_AK')
        sk = os.getenv(f'ACCOUNT{index}_SK')
        
        if not account_name or not ak or not sk:
            break
        
        accounts.append({"name": account_name, "ak": ak, "sk": sk})
        index += 1
    
    logger.info(f"共发现 {len(accounts)} 个华为云账号配置")
    all_account_data = []
    
    # 在主函数中添加批次号生成
    batch_number = datetime.now().strftime('%Y%m%d%H%M%S')
    
    for account in accounts:
        account_name = account["name"]
        ak = account["ak"]
        sk = account["sk"]
        
        logger.info(f"开始处理账号: {account_name}")
        
        # 查询资源、余额、账单、储值卡和证书信息
        resource_result = query_resources(ak, sk, account_name)
        balance_result = query_balance(ak, sk, account_name)
        bill_result = query_bills(ak, sk, account_name)
        stored_cards_result = query_stored_cards(ak, sk, account_name)
        certificates_result = query_certificates(ak, sk, account_name)
        
        resources = resource_result["data"] if resource_result["success"] else None
        balance = balance_result["data"] if balance_result["success"] else None
        bills = bill_result["data"] if bill_result["success"] else None
        stored_cards = stored_cards_result["data"] if stored_cards_result["success"] else None
        certificates = certificates_result["data"] if certificates_result["success"] else None
        
        # 保存到数据库
        if db and resources:
            for service_type, resource_list in resources.items():
                for resource in resource_list:
                    try:
                        if 'project' not in resource or not resource['project']:
                            resource['project'] = 'default'
                        db.save_resource(account_name, resource, batch_number)
                    except Exception as e:
                        logger.error(f"保存资源失败: {account_name} - {resource.get('name', '')}")
        
        if db and balance:
            db.save_balance(account_name, balance, batch_number)
        
        if db and bills:
            current_month = datetime.now().strftime('%Y-%m')
            for record in bills['records']:
                try:
                    db.save_bill(account_name, record, current_month, batch_number)
                except Exception as e:
                    logger.error(f"保存账单失败: {account_name} - {record.get('service_type', '')}")
        
        if db and stored_cards:
            for card in stored_cards['cards']:
                try:
                    db.save_stored_card(account_name, card, batch_number)
                except Exception as e:
                    logger.error(f"保存储值卡失败: {account_name} - {card.get('card_name', '')}")
        
        if db and certificates:
            for cert in certificates:
                try:
                    db.save_resource(account_name, cert, batch_number)
                except Exception as e:
                    logger.error(f"保存证书失败: {account_name} - {cert.get('name', '')}")
        
        # 收集账号数据
        all_account_data.append({
            "account_name": account_name,
            "resources": resources,
            "balance": balance,
            "bills": bills,
            "stored_cards": stored_cards
        })
    
    # 发送通知
    if wework.enabled:
        logger.info("开始发送企业微信通知...")
        wework.send_balance_notification(all_account_data)
        wework.send_bill_notification(all_account_data)
        for account_data in all_account_data:
            if account_data.get('resources'):
                wework.send_resource_notification(
                    account_data['account_name'],
                    account_data['resources']
                )
    
    if email.enabled:
        logger.info("开始发送邮件通知...")
        email_content = email.format_all_accounts_message(all_account_data)
        if email_content:
            if email.send_email(None, email_content):
                logger.info("邮件通知发送成功")
            else:
                logger.error("邮件通知发送失败")
    
    if yunzhijia.enabled:
        logger.info("开始发送云之家通知...")
        yunzhijia.send_balance_notification(all_account_data)
        yunzhijia.send_bill_notification(all_account_data)
        for account_data in all_account_data:
            if account_data.get('resources'):
                yunzhijia.send_resource_notification(
                    account_data['account_name'],
                    account_data['resources']
                )

def process_resources(client, account_name):
    """处理单个账号的资源信息"""
    try:
        resources = client.get_resources()
        logger.info(f"账号 {account_name} 资源查询成功，共 {len(resources)} 个资源，{len(set(r['service_type'] for r in resources))} 种服务")
        
        for resource in resources:
            # 确保资源数据包含所有必要字段
            resource_data = {
                'name': resource.get('resource_name', ''),
                'id': resource.get('resource_id', ''),  # 资源ID
                'service_type': resource.get('service_type_name', ''),  # 服务类型
                'region': resource.get('region_code', ''),
                'expire_time': resource.get('expire_time', ''),
                'project': resource.get('enterprise_project_name', ''),
                'remaining_days': resource.get('remaining_days', 0)
            }
            db.save_resource(account_name, resource_data)
            
        return resources
    except Exception as e:
        logger.error(f"处理账号 {account_name} 资源时出错: {str(e)}")
        return None

if __name__ == "__main__":
    main() 