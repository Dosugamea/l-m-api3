from functools import wraps
from ..message import SystemMessageHandler
import inspect


class TicketHooks(object):
    def __init__(self, dbHandler, language="EN", messageFile=None):
        self.sys = SystemMessageHandler(language, messageFile)
        self.db = dbHandler

    def Ticket(self, name, cnt):
        def __wrapper(func):
            func.Ticket = True
            func.name = name
            func.cnt = cnt

            @wraps(func)
            def __check(self, *args, **kwargs):
                # Check is it calling this
                if func.inpart:
                    has_prefix = any(
                        [args[1].text.startswith(c) for c in func.cmds]
                    )
                    if not has_prefix:
                        return False
                else:
                    if args[1].text not in func.cmds:
                        return False
                if args[0].checkTicket(args[0].msg, name, cnt):
                    # I DON'T KNOW WHY, BUT THIS WORKS
                    func(args[0], args[0], args[0].cl, args[1])
                    return True
            return __check
        return __wrapper

    def checkGroupTicket(self, msg, name, cnt):
        tickets = self.db.getGroup(msg.to, name)
        if tickets is None:
            self.sys.generateHandlerMessage(
                msg, "NoTicket",
                [name, cnt]
            )
            return False
        if tickets >= cnt:
            self.sys.generateHandlerMessage(
                msg, "UseTicket",
                [name, cnt, tickets, tickets - cnt]
            )
            tickets -= cnt
            self.db.postGroup(msg.to, name, tickets)
            return True
        else:
            self.sys.generateHandlerMessage(
                msg, "NoTicket",
                [name, cnt]
            )

    def checkTicket(self, msg, name, cnt):
        tickets = self.db.getUser(msg._from, name)
        if tickets is None:
            self.sys.generateHandlerMessage(
                msg, "NoTicket",
                [name, cnt]
            )
            return False
        if tickets >= cnt:
            self.sys.generateHandlerMessage(
                msg, "UseTicket",
                [name, cnt, tickets, tickets - cnt]
            )
            tickets -= cnt
            self.db.postUser(msg._from, name, tickets)
            return True
        else:
            self.sys.generateHandlerMessage(
                msg, "NoTicket",
                [name, cnt]
            )
