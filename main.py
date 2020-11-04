from flask import Flask, request
from line_magic import LineMessagingClient, LineMessagingTracer
from line_magic import TextMessage, StickerMessage

cl = LineMessagingClient(channelAccessToken="")
tracer = LineMessagingTracer(cl, prefix=["!", "?", "#", "."])


class Operations(object):
    @tracer.Before("Operation")
    def set_Token(self, cl, op):
        if "replyToken" in op:
            cl.setReplyToken(op["replyToken"])

    @tracer.Operation("message")
    def got_message(self, cl, msg):
        print(msg)
        self.trace(msg, "Content")

    @tracer.Operation("follow")
    def got_follow(self, cl, msg):
        print("FOLLOW")
        msgs = [TextMessage("Thanks for add me!")]
        cl.replyMessage(msgs)

    @tracer.Operation("unfollow")
    def got_unfollow(self, cl, msg):
        print("UNFOLLOW")

    @tracer.Operation("join")
    def got_join(self, cl, msg):
        print("JOIN")
        msgs = [TextMessage("Thanks for invite me!")]
        cl.replyMessage(msgs)

    @tracer.Operation("leave")
    def got_leave(self, cl, msg):
        print("LEAVE")
        print(msg)

    @tracer.Operation("postback")
    def got_postback(self, cl, msg):
        print("POSTBACK")
        print(msg)


class Contents(object):
    @tracer.Content("text")
    def got_text(self, cl, msg):
        self.trace(msg, "Command")

    @tracer.Content("image")
    def got_image(self, cl, msg):
        msgs = [TextMessage("Kawaii!")]
        cl.replyMessage(msgs)

    @tracer.Content("video")
    def got_video(self, cl, msg):
        msgs = [TextMessage("Nice video!")]
        cl.replyMessage(msgs)

    @tracer.Content("audio")
    def got_audio(self, cl, msg):
        msgs = [TextMessage("Nice audio!")]
        cl.replyMessage(msgs)

    @tracer.Content("file")
    def got_file(self, cl, msg):
        msgs = [TextMessage("Nice file!")]
        cl.replyMessage(msgs)

    @tracer.Content("location")
    def got_location(self, cl, msg):
        msgs = [TextMessage("Nice location!")]
        cl.replyMessage(msgs)

    @tracer.Content("sticker")
    def got_sticker(self, cl, msg):
        msgs = [StickerMessage(1, 2)]
        cl.replyMessage(msgs)


class Commands(object):
    @tracer.Command(alt=["ハロー", "hello"])
    def hi(self, cl, msg):
        '''Check the bot Alive'''
        msgs = [TextMessage("Hi too!")]
        cl.replyMessage(msgs)

    @tracer.Command()
    def help(self, cl, msg):
        '''Display this help message'''
        msgs = [TextMessage(self.genHelp())]
        cl.replyMessage(msgs)


def app_callback():
    try:
        if request.method == "POST":
            data = request.get_json()
            for d in data["events"]:
                tracer.trace(d, "Operation")
        return "OK"
    except:
        return "Error"


def createApp():
    app = Flask(__name__)
    app.add_url_rule('/callback', 'callback', app_callback, methods=["GET", "POST"])
    tracer.addClass(Operations())
    tracer.addClass(Contents())
    tracer.addClass(Commands())
    tracer.startup()
    return app


if __name__ == "__main__":
    app = createApp()
    app.run(host="localhost", port=8080, debug=True)
