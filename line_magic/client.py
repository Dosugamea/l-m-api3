from .talk import TalkClient
from .richmenu import RichMenuClient
from .content import ContentClient


class MessagingClient(TalkClient, RichMenuClient, ContentClient):
    def __init__(self, channelAccessToken, endpoint="https://api.line.me/v2"):
        TalkClient.__init__(self, channelAccessToken, endpoint)
        RichMenuClient.__init__(self, channelAccessToken, endpoint)
        ContentClient.__init__(self, channelAccessToken)
