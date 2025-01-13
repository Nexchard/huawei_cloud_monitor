from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkbss.v2.region.bss_region import BssRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkbss.v2 import *
from collections import defaultdict
from datetime import datetime
from src.logger import logger
import json

def calculate_remaining_days(expire_time):
    """计算资源的剩余天数"""
    expire_date = datetime.strptime(expire_time.split('T')[0], '%Y-%m-%d')
    remaining_days = (expire_date - datetime.now()).days
    return remaining_days

def query_resources(ak, sk, account_name):
    """查询华为云账号下的资源信息"""
    try:
        # 使用AK/SK创建认证凭证
        credentials = GlobalCredentials(ak, sk)
        client = BssClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(BssRegion.value_of("cn-north-1")) \
            .build()

        # 创建请求对象并发送请求
        request = ListPayPerUseCustomerResourcesRequest()
        request.body = QueryResourcesReq(
            limit=100,
            status_list=[2],  # 仅查询有效资源
            only_main_resource=1
        )
        response = client.list_pay_per_use_customer_resources(request)
        
        # 按服务类型分组资源
        services = defaultdict(list)
        resource_count = 0
        for resource in response.data:
            resource_count += 1
            resource_info = {
                "name": resource.resource_name or "未命名",
                "id": resource.resource_id,
                "service_type": resource.service_type_name,
                "project": resource.enterprise_project.name if resource.enterprise_project else "无项目",
                "region": resource.region_code,
                "expire_time": resource.expire_time,
                "remaining_days": calculate_remaining_days(resource.expire_time)
            }
            services[resource.service_type_name].append(resource_info)
        
        logger.info(f"账号 {account_name} 资源查询成功，共 {resource_count} 个资源，{len(services)} 种服务")
        
        logger.debug(f"账号 {account_name} 原始资源数据: {json.dumps(services, indent=2, ensure_ascii=False)}")
        return {
            "success": True,
            "data": services,
            "error": None
        }
                
    except exceptions.ClientRequestException as e:
        error_msg = f"账号 {account_name} 资源查询失败: 状态码={e.status_code}, 错误码={e.error_code}, 错误信息={e.error_msg}"
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
    except Exception as e:
        error_msg = f"账号 {account_name} 资源查询发生未知错误: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "data": None,
            "error": str(e)
        } 