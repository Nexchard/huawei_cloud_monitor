from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkbss.v2.region.bss_region import BssRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkbss.v2 import *
from src.logger import logger

def query_balance(ak, sk, account_name):
    """查询华为云账号的余额信息"""
    try:
        # 使用AK/SK创建认证凭证
        credentials = GlobalCredentials(ak, sk)
        client = BssClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(BssRegion.value_of("cn-north-1")) \
            .build()

        # 创建请求对象并发送请求
        request = ShowCustomerAccountBalancesRequest()
        response = client.show_customer_account_balances(request)
        
        # 处理返回数据
        balance_info = {
            "total_amount": 0,
            "currency": "CNY",
            "accounts": []
        }
        
        for account in response.account_balances:
            balance_info["accounts"].append({
                "account_id": account.account_id,
                "account_type": account.account_type,
                "amount": account.amount,
                "currency": account.currency,
                "designated_amount": account.designated_amount,
                "credit_amount": account.credit_amount
            })
            if account.account_type == 1:  # 主账号
                balance_info["total_amount"] = account.amount
                balance_info["currency"] = account.currency
        
        logger.info(f"账号 {account_name} 余额查询成功: {balance_info['total_amount']} {balance_info['currency']}")
                
        return {
            "success": True,
            "data": balance_info,
            "error": None
        }
                
    except exceptions.ClientRequestException as e:
        error_msg = f"账号 {account_name} 余额查询失败: 状态码={e.status_code}, 错误码={e.error_code}, 错误信息={e.error_msg}"
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