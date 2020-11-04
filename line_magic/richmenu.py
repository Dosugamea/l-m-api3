from .base import BaseClient


class RichMenuClient(BaseClient):
    def __init__(self, channelAccessToken, endpoint="https://api.line.me/v2"):
        BaseClient.__init__(
            self,
            endpoint,
            {"Authorization": f"Bearer {channelAccessToken}"}
        )

    def getRichMenu(self, menu_id):
        resp = self.reqGet(f"/bot/richmenu/{menu_id}")
        if self.isOK(resp):
            return resp.json()

    def createRichMenu(self, richmenu_data):
        resp = self.reqPost("/bot/richmenu", json=richmenu_data)
        if self.isOK(resp):
            return resp.json()["richMenuId"]

    def deleteRichMenu(self, menu_id):
        resp = self.reqDel(f"/bot/richmenu/{menu_id}")
        return self.isOK(resp)

    def getRichMenuIdOfUser(self, user_id):
        resp = self.reqGet(f"/bot/user/{user_id}/richmenu")
        if self.isOK(resp):
            return resp.json()["richMenuId"]

    def linkRichMenuToUser(self, user_id, menu_id):
        resp = self.reqPost(
            f"/bot/user/{user_id}/richmenu/{menu_id}"
        )
        return self.isOK(resp)

    def unlinkRichMenuToUser(self, user_id):
        pass
