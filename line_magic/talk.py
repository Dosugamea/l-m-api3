from .base import BaseClient


class TalkClient(BaseClient):
    def __init__(self, channelAccessToken, endpoint="https://api.line.me/v2"):
        BaseClient.__init__(
            self,
            endpoint,
            {"Authorization": f"Bearer {channelAccessToken}"}
        )

    def setReplyToken(self, token):
        self.replyToken = token

    def replyMessage(self, messages):
        if len(messages) == 0:
            raise Exception("Messages aren't specified.")
        elif len(messages) > 5:
            raise Exception("Too many messages.")
        resp = self.reqPost(
            "/bot/message/reply",
            json={
                "replyToken": self.replyToken,
                "messages": [m.__dict__ for m in messages]
            }
        )
        return self.isOK(resp)

    def sendMessage(self, to, messages):
        if len(messages) == 0:
            raise Exception("Messages aren't specified.")
        elif len(messages) > 5:
            raise Exception("Too many messages.")
        resp = self.reqPost(
            "/bot/message/push",
            json={
                "to": to,
                "messages": [m.__dict__ for m in messages]
            }
        )
        return self.isOK(resp)

    def getProfile(self, user_id):
        resp = self.reqGet(f"/bot/profile/{user_id}")
        if self.isOK(resp):
            return resp.json()

    def leaveGroup(self, group_id):
        resp = self.reqPost(f"/bot/group/{group_id}/leave")
        return self.isOK(resp)

    def leaveRoom(self, room_id):
        resp = self.reqPost(f"/bot/room/{room_id}/leave")
        return self.isOK(resp)
