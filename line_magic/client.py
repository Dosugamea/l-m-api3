from .talk import TalkClient
from .richmenu import RichMenuClient


class MessagingClient(TalkClient, RichMenuClient):
    def __init__(self, channelAccessToken, endpoint="https://api.line.me/v2"):
        TalkClient.__init__(self, channelAccessToken, endpoint)
        RichMenuClient.__init__(self, channelAccessToken, endpoint)
