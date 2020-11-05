from .base import BaseClient


class ContentClient(BaseClient):
    def __init__(self, channelAccessToken, endpoint="https://api-data.line.me/v2"):
        BaseClient.__init__(
            self,
            endpoint,
            {"Authorization": f"Bearer {channelAccessToken}"}
        )

    def getContent(self, message_id):
        print(self.endpoint)
        resp = self.reqGet(f"/bot/message/{message_id}/content")
        if self.isOK(resp):
            return resp.content
