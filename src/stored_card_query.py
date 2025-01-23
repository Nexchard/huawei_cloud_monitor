from huaweicloudsdkcore.auth.credentials import GlobalCredentials
from huaweicloudsdkbss.v2.region.bss_region import BssRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkbss.v2 import *
from src.logger import logger

def query_stored_cards(ak, sk, account_name):
    """查询华为云账号的储值卡信息"""
    try:
        # 使用AK/SK创建认证凭证
        credentials = GlobalCredentials(ak, sk)
        client = BssClient.new_builder() \
            .with_credentials(credentials) \
            .with_region(BssRegion.value_of("cn-north-1")) \
            .build()

        # 创建请求对象
        request = ListStoredValueCardsRequest()
        request.status = 1  # 只查询可使用的储值卡
        
        # 发送请求
        response = client.list_stored_value_cards(request)
        
        # 处理返回数据
        cards_info = {
            "total_count": response.total_count,
            "cards": []
        }
        
        total_balance = 0
        for card in response.stored_value_cards:
            card_info = {
                "card_id": card.card_id,
                "card_name": card.card_name,
                "face_value": float(card.face_value),
                "balance": float(card.balance),
                "effective_time": card.effective_time,
                "expire_time": card.expire_time
            }
            cards_info["cards"].append(card_info)
            total_balance += float(card.balance)
        
        cards_info["total_balance"] = total_balance
        
        logger.info(f"账号 {account_name} 储值卡查询成功: {len(cards_info['cards'])} 张卡")
        
        return {
            "success": True,
            "data": cards_info,
            "error": None
        }
                
    except exceptions.ClientRequestException as e:
        error_msg = f"账号 {account_name} 储值卡查询失败: 状态码={e.status_code}, 错误码={e.error_code}, 错误信息={e.error_msg}"
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