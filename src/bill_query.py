from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkbss.v2.region.bss_region import BssRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkbss.v2 import *
from datetime import datetime
from src.logger import logger

def query_bills(ak, sk, account_name):
    """查询华为云账号的按需计费账单信息"""
    try:
        # 使用AK/SK创建认证凭证
        credentials = GlobalCredentials(ak, sk)
        client = BssClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(BssRegion.value_of("cn-north-1")) \
            .build()

        # 创建请求对象
        request = ListCustomerselfResourceRecordDetailsRequest()
        
        # 获取当前月份
        current_month = datetime.now().strftime('%Y-%m')
        
        # 设置请求体
        request.body = QueryResRecordsDetailReq(
            cycle=current_month,
            charge_mode=3,  # 按需计费
            include_zero_record=False,  # 不包含金额为0的记录
            method="oneself",  # 只查询自己的账单，不包含子客户
            limit=1000,  # 设置较大的limit以获取所有记录
            offset=0
        )

        # 发送请求
        response = client.list_customerself_resource_record_details(request)
        
        # 处理返回数据
        bills_info = {
            "records": [],
            "total_amount": 0,
            "currency": response.currency
        }
        
        for record in response.monthly_records:
            # 只保留需要的字段
            bill_record = {
                "account_name": account_name,
                "project_name": record.enterprise_project_name,
                "service_type": record.cloud_service_type_name,
                "resource_name": record.resource_name or record.product_spec_desc,
                "region": record.region_name,
                "amount": record.consume_amount
            }
            bills_info["records"].append(bill_record)
            bills_info["total_amount"] += record.consume_amount
        
        logger.info(f"账号 {account_name} 账单查询成功: {len(bills_info['records'])} 条记录")
        
        return {
            "success": True,
            "data": bills_info,
            "error": None
        }
                
    except exceptions.ClientRequestException as e:
        error_msg = f"账号 {account_name} 账单查询失败: 状态码={e.status_code}, 错误码={e.error_code}, 错误信息={e.error_msg}"
        logger.error(error_msg)
        return {
            "success": False,
            "data": None,
            "error": {
                "status_code": e.status_code,
                "request_id": e.request_id,
                "error_code": e.error_code,
                "error_msg": e.error_msg
            }
        } 