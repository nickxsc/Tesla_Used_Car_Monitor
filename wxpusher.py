import requests


class WxPusherException(Exception):
    """WxPusher specific base exception."""


class WxPusherNoneTokenException(WxPusherException):
    """Raised when both token and default token are None."""


class WxPusher:
  # 此处需要修改你自己的wxpusher信息
    APP_TOKEN = "AT_yNxPLLdHgg7ttv8QG9bXjRlRHwNlAq7f"
    UIDS = ["UID_4qbNgiZ9iptI5A7rVUNHV0RNjuQC", ]

    def __init__(self, app_token=APP_TOKEN, uids=None, topic_ids=None, verify_pay=False, url='', content_type=1):
        if topic_ids is None:
            topic_ids = ['', ]
        if uids is None:
            uids = self.UIDS
        self.app_token = app_token
        self.uids = uids
        self.topic_ids = topic_ids
        self.verify_pay = verify_pay
        self.content_type = content_type  # 内容类型 1表示文字  2表示html(只发送body标签内部的数据即可，不包括body标签) 3表示markdown
        self.BASE_URL = 'http://wxpusher.zjiecode.com/api'

    def send_message(self, summary='消息摘要', content='消息内容', url=''):
        """发送消息"""
        payload = {
            'appToken': self.app_token,
            'content': content,
            'summary': summary,
            'contentType': self.content_type,
            'topicIds': self.topic_ids,
            'uids': self.uids,
            'verifyPay': self.verify_pay,
            'url': url,
        }
        send_url = f'{self.BASE_URL}/send/message'
        return requests.post(send_url, json=payload).json()

    def query_message(self, send_id):
        """查询状态"""
        query_url = f'{self.BASE_URL}/send/query/status?sendRecordId={send_id}'
        return requests.get(query_url).json()


if __name__ == '__main__':
    my_pusher = WxPusher()
    response = my_pusher.send_message(summary='一条测试消息', content='2023年6月2O日，已完成日常备份')
    print(response)
