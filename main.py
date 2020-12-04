from flask import Flask, request
from line_magic import (
    LineMessagingClient, LineMessagingTracer,
    TextMessage, StickerMessage,
    TraceType
)
import sqlite3

cl = LineMessagingClient(channelAccessToken="")
db = sqlite3.connect("test.db")
tracer = LineMessagingTracer(cl, db, ["!", "?", "#", "."])


class Events(object):
    @tracer.Before(TraceType.EVENT)
    def set_Token(self, ctx, cl, op):
        if "replyToken" in op:
            cl.setReplyToken(op["replyToken"])

    @tracer.Event("message")
    def got_message(self, ctx, cl, msg):
        ctx.trace(msg, TraceType.CONTENT)

    @tracer.Event("follow")
    def got_follow(self, ctx, cl, msg):
        print("FOLLOW")
        msgs = [TextMessage("Thanks for add me!")]
        cl.replyMessage(msgs)

    @tracer.Event("unfollow")
    def got_unfollow(self, ctx, cl, msg):
        print("UNFOLLOW")

    @tracer.Event("join")
    def got_join(self, ctx, cl, msg):
        print("JOIN")
        msgs = [TextMessage("Thanks for invite me!")]
        cl.replyMessage(msgs)

    @tracer.Event("leave")
    def got_leave(self, ctx, cl, msg):
        print("LEAVE")
        print(msg)

    @tracer.Event("postback")
    def got_postback(self, ctx, cl, msg):
        print("POSTBACK")
        print(msg)


class Contents(object):
    @tracer.Content("text")
    def got_text(self, ctx, cl, msg):
        ctx.trace(msg, TraceType.COMMAND)

    @tracer.Content("image")
    def got_image(self, ctx, cl, msg):
        msgs = [TextMessage("Kawaii!")]
        cl.replyMessage(msgs)

    @tracer.Content("video")
    def got_video(self, ctx, cl, msg):
        msgs = [TextMessage("Nice video!")]
        cl.replyMessage(msgs)

    @tracer.Content("audio")
    def got_audio(self, ctx, cl, msg):
        msgs = [TextMessage("Nice audio!")]
        cl.replyMessage(msgs)

    @tracer.Content("file")
    def got_file(self, ctx, cl, msg):
        msgs = [TextMessage("Nice file!")]
        cl.replyMessage(msgs)

    @tracer.Content("location")
    def got_location(self, ctx, cl, msg):
        msgs = [TextMessage("Nice location!")]
        cl.replyMessage(msgs)

    @tracer.Content("sticker")
    def got_sticker(self, ctx, cl, msg):
        msgs = [StickerMessage(1, 2)]
        cl.replyMessage(msgs)


class Commands(object):
    @tracer.Command(usePrefix=False, alt=["ハロー", "hello"])
    def hi(self, ctx, cl, msg):
        '''Check the bot Alive'''
        msgs = [TextMessage("Hi too!")]
        cl.replyMessage(msgs)

    @tracer.Command()
    def help(self, ctx, cl, msg):
        '''Display this help message'''
        msgs = [TextMessage(ctx.genHelp())]
        cl.replyMessage(msgs)


def app_callback():
    try:
        if request.method == "POST":
            data = request.get_json()
            for d in data["events"]:
                tracer.trace(d, TraceType.EVENT)
        return "OK"
    except:
        return "Error"


def createApp():
    app = Flask(__name__)
    app.add_url_rule('/callback', 'callback', app_callback, methods=["GET", "POST"])
    tracer.addClass(Events())
    tracer.addClass(Contents())
    tracer.addClass(Commands())
    tracer.startup()
    return app


if __name__ == "__main__":
    app = createApp()
    app.run(host="localhost", port=8080, debug=True)
