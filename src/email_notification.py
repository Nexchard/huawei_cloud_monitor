import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()

class EmailNotification:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', '465'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_from = os.getenv('SMTP_FROM')
        self.smtp_to = os.getenv('SMTP_TO', '').split(',')
        self.enabled = os.getenv('SMTP_ENABLED', 'false').lower() == 'true'
        self.alert_days = int(os.getenv('RESOURCE_ALERT_DAYS', '65'))

    def format_all_accounts_message(self, accounts_data):
        """格式化所有账号的资源和余额信息为HTML邮件内容"""
        
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #1a73e8;
                    border-bottom: 2px solid #1a73e8;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #202124;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #1a73e8;
                    margin-top: 20px;
                }}
                .account {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .balance {{
                    background: #e8f0fe;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }}
                .balance h3 {{
                    margin-top: 0;
                }}
                .service {{
                    margin-bottom: 20px;
                }}
                .resource {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid #1a73e8;
                }}
                .resource p {{
                    margin: 5px 0;
                }}
                .warning {{
                    border-left: 4px solid #f44336;
                }}
                .warning .days {{
                    color: #f44336;
                    font-weight: bold;
                }}
                .medium .days {{
                    color: #fb8c00;
                    font-weight: bold;
                }}
                .info {{
                    color: #1a73e8;
                    font-weight: bold;
                }}
                .meta-info {{
                    color: #5f6368;
                    font-size: 0.9em;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>华为云资源和余额监控报告</h1>
        """
        
        # 添加所有账号的余额信息
        html += "<div class='balance'>"
        html += "<h3>账户余额汇总</h3>"
        for account_data in accounts_data:
            account_name = account_data['account_name']
            balance = account_data.get('balance')
            if balance:
                html += f"<p><strong>账号：</strong>{account_name} - <span class='info'>{balance['total_amount']} {balance['currency']}</span></p>"
        html += "</div>"
        
        has_alert = False
        # 遍历所有账号，检查是否有需要告警的资源
        for account_data in accounts_data:
            account_name = account_data['account_name']
            account_has_alert = False
            account_html = f"<div class='account'>"
            account_html += f"<h2>账号：{account_name}</h2>"
            
            # 添加资源信息
            if account_data.get('resources'):
                account_html += "<h3>资源信息</h3>"
                resources_html = ""
                
                for service_type, resources in account_data['resources'].items():
                    service_html = f"<div class='service'>"
                    service_html += f"<h4>{service_type}</h4>"
                    service_has_resources = False
                    
                    for resource in resources:
                        expire_time = resource['expire_time'].replace('T', ' ').replace('Z', '')
                        remaining_days = resource['remaining_days']
                        
                        if remaining_days <= self.alert_days:
                            has_alert = True
                            account_has_alert = True
                            service_has_resources = True
                            
                            if remaining_days <= 15:
                                resource_class = "warning"
                            elif remaining_days <= 30:
                                resource_class = "info"
                            else:
                                resource_class = "medium"
                                
                            service_html += f"""
                            <div class='resource {resource_class}'>
                                <p><strong>名称：</strong>{resource['name']}</p>
                                <p><strong>区域：</strong>{resource['region']}</p>
                                <p><strong>到期时间：</strong>{expire_time}</p>
                                <p><strong>剩余天数：</strong><span class='days'>{remaining_days}天</span></p>
                            """
                            if resource['project']:
                                service_html += f"<p><strong>企业项目：</strong>{resource['project']}</p>"
                            service_html += "</div>"
                    
                    service_html += "</div>"
                    if service_has_resources:
                        resources_html += service_html
                
                # 只有当账号有告警资源时才添加到HTML中
                if account_has_alert:
                    account_html += resources_html
                    html += account_html + "</div>"
        
        html += """
            </body>
        </html>
        """
        
        return html if has_alert else None

    def send_email(self, subject, html_content):
        """发送HTML格式的邮件"""
        if not self.enabled:
            logger.info("邮件通知未启用")
            return False
            
        if not all([self.smtp_server, self.smtp_username, self.smtp_password, self.smtp_from, self.smtp_to]):
            logger.warning("邮件配置不完整")
            return False
            
        if not html_content:
            logger.info("没有需要告警的内容")
            return False
            
        try:
            logger.info(f"正在发送邮件到 {', '.join(self.smtp_to)}...")
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_from
            msg['To'] = ', '.join(self.smtp_to)
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info("邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False 