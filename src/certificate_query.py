from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkscm.v3.region.scm_region import ScmRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkscm.v3 import *
from datetime import datetime
from src.logger import logger

def query_certificates(ak, sk, account_name):
    """查询华为云账号的SSL证书信息"""
    try:
        # 使用AK/SK创建认证凭证
        credentials = GlobalCredentials(ak, sk)
        client = ScmClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(ScmRegion.value_of("cn-north-4")) \
            .build()

        # 创建请求对象并发送请求
        request = ListCertificatesRequest()
        response = client.list_certificates(request)
        
        # 处理返回数据
        certificates = []
        for cert in response.certificates:
            # 只处理有过期时间且状态不是EXPIRED的证书
            if cert.expire_time and cert.status != 'EXPIRED':
                try:
                    # 计算剩余天数
                    expire_time = datetime.strptime(cert.expire_time.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    remaining_days = (expire_time - datetime.now()).days
                    
                    cert_info = {
                        'name': cert.name,
                        'id': cert.id,
                        'service_type': 'SSL证书',
                        'region': 'cn-north-4',  # SSL证书是全局资源
                        'expire_time': expire_time.strftime('%Y-%m-%dT%H:%M:%SZ'),  # 转换为标准格式
                        'project': cert.enterprise_project_id or 'default',
                        'remaining_days': remaining_days
                    }
                    certificates.append(cert_info)
                except Exception as e:
                    logger.error(f"处理证书 {cert.name} 时出错: {str(e)}")
                    continue
        
        logger.info(f"账号 {account_name} SSL证书查询成功: {len(certificates)} 个有效证书")
        
        return {
            "success": True,
            "data": certificates,
            "error": None
        }
                
    except exceptions.ClientRequestException as e:
        error_msg = f"账号 {account_name} SSL证书查询失败: 状态码={e.status_code}, 错误码={e.error_code}, 错误信息={e.error_msg}"
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