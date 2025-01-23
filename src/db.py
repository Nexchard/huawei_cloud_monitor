import mysql.connector
from mysql.connector import pooling
from src.config import Config
from datetime import datetime
from src.logger import logger

class Database:
    def __init__(self):
        # 创建数据库连接池
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        self.create_database()
        self.import_sql_files()

    def get_connection(self):
        """获取数据库连接"""
        connection = self.connection_pool.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"USE {Config.DB_NAME}")  # 每次获取连接时选择数据库
        cursor.close()
        return connection

    def create_database(self):
        """创建数据库如果不存在"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            logger.info(f"Database {Config.DB_NAME} checked/created.")
        except Exception as e:
            logger.error(f"创建数据库失败: {str(e)}")
        finally:
            cursor.close()
            connection.close()

    def import_sql_files(self):
        """导入SQL文件以创建表，检查表是否存在并自动导入缺失的表"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(f"USE {Config.DB_NAME};")
            
            # 定义所有需要的表及其对应的SQL文件
            required_tables = {
                'resources': 'sql/create_resources_table.sql',
                'account_balances': 'sql/create_balances_table.sql',
                'account_bills': 'sql/create_bills_table.sql',
                'stored_cards': 'sql/create_stored_cards_table.sql'
            }
            
            # 获取当前数据库中存在的表
            cursor.execute("SHOW TABLES")
            existing_tables = {table[0] for table in cursor.fetchall()}
            
            # 检查并创建缺失的表
            for table_name, sql_file in required_tables.items():
                if table_name not in existing_tables:
                    logger.info(f"检测到缺失表: {table_name}，正在创建...")
                    try:
                        with open(sql_file, 'r', encoding='utf-8') as file:
                            sql_script = file.read()
                            for statement in sql_script.split(';'):
                                if statement.strip():
                                    cursor.execute(statement)
                            logger.info(f"表 {table_name} 创建成功")
                    except Exception as e:
                        logger.error(f"创建表 {table_name} 失败: {str(e)}")
                        raise
                else:
                    logger.info(f"表 {table_name} 已存在")
            
            connection.commit()
            logger.info("数据库表检查和导入完成")
            
        except Exception as e:
            logger.error(f"数据库表检查和导入失败: {str(e)}")
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def save_resource(self, account_name, resource, batch_number):
        """保存资源信息到数据库，保留历史记录"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            # 先检查数据完整性
            required_fields = ['name', 'id', 'service_type', 'region', 'expire_time', 'project', 'remaining_days']
            missing_fields = [field for field in required_fields if field not in resource or resource[field] is None]
            if missing_fields:
                raise ValueError(f"资源数据缺少必要字段: {missing_fields}")

            sql = """INSERT INTO resources 
                    (account_name, resource_name, resource_id, service_type, 
                    region, expire_time, project_name, remaining_days, batch_number) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = (
                account_name,
                resource['name'],
                resource['id'],
                resource['service_type'],
                resource['region'],
                resource['expire_time'].replace('T', ' ').replace('Z', ''),
                resource['project'],
                resource['remaining_days'],
                batch_number
            )
            
            cursor.execute(sql, values)
            connection.commit()
            logger.info(f"保存资源信息成功: {account_name} - {resource['name']}")
        except Exception as e:
            logger.error(f"保存资源信息失败: {str(e)}")
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def save_balance(self, account_name, balance, batch_number):
        """保存余额信息到数据库，保留历史记录"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            sql = """INSERT INTO account_balances 
                    (account_name, total_amount, currency, batch_number) 
                    VALUES (%s, %s, %s, %s)"""
            
            values = (
                account_name,
                balance.get('total_amount', 0),
                balance.get('currency', 'CNY'),
                batch_number
            )
            
            cursor.execute(sql, values)
            connection.commit()
            logger.info(f"保存余额信息成功: {account_name} - {balance.get('total_amount', 0)} {balance.get('currency', 'CNY')}")
        except Exception as e:
            logger.error(f"保存余额信息失败: {str(e)}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def save_bill(self, account_name, bill_record, cycle, batch_number):
        """保存账单信息到数据库"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            sql = """INSERT INTO account_bills 
                    (account_name, project_name, service_type, region, amount, currency, cycle, batch_number) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = (
                account_name,
                bill_record['project_name'],
                bill_record['service_type'],
                bill_record['region'],
                bill_record['amount'],
                bill_record.get('currency', 'CNY'),
                cycle,
                batch_number
            )
            
            cursor.execute(sql, values)
            connection.commit()
            logger.info(f"保存账单信息成功: {account_name} - {bill_record['service_type']}")
        except Exception as e:
            logger.error(f"保存账单信息失败: {str(e)}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def save_stored_card(self, account_name, card, batch_number):
        """保存储值卡信息到数据库"""
        connection = self.get_connection()
        cursor = connection.cursor()
        try:
            sql = """INSERT INTO stored_cards 
                    (account_name, card_id, card_name, face_value, balance, 
                    effective_time, expire_time, batch_number) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            
            values = (
                account_name,
                card['card_id'],
                card['card_name'],
                card['face_value'],
                card['balance'],
                card['effective_time'].replace('T', ' ').replace('Z', ''),
                card['expire_time'].replace('T', ' ').replace('Z', ''),
                batch_number
            )
            
            cursor.execute(sql, values)
            connection.commit()
            logger.info(f"保存储值卡信息成功: {account_name} - {card['card_name']}")
        except Exception as e:
            logger.error(f"保存储值卡信息失败: {str(e)}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def close(self):
        """关闭数据库连接池"""
        try:
            self.connection_pool._remove_connections()
            logger.info("数据库连接池已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接池失败: {str(e)}") 