from concurrent.futures import ThreadPoolExecutor
from .database import DatabaseHandler
from .hooks.command import CmdHooks
from .hooks.plan import ScheduleHooks
from .hooks.ticket import TicketHooks
from .trace_type import TraceType
from datetime import datetime
import inspect
import traceback
import types
import glob


class HooksTracer(CmdHooks, ScheduleHooks, TicketHooks):
    def __init__(
        self,
        messaging_client,
        db_connection,
        prefixes=["?"],
        maxThreads=50,
        lang="JA",
        message_file=None
    ):
        self.cl = messaging_client
        self.db = DatabaseHandler(db_connection)
        self.pool = ThreadPoolExecutor(maxThreads)
        self.prefixes = prefixes
        self.lang = lang
        self.message_file = message_file
        self.event_funcs = {
            "before": [],
            "main": [],
            "after": []
        }
        self.content_funcs = {
            "before": [],
            "main": [],
            "after": []
        }
        self.command_funcs = {
            "before": [],
            "main": [],
            "after": []
        }
        self.schedule_funcs = {
            "main": []
        }
        self.targetDict = {
            TraceType.EVENT: self.event_funcs,
            TraceType.CONTENT: self.content_funcs,
            TraceType.COMMAND: self.command_funcs,
            TraceType.SCHEDULE: self.schedule_funcs,
            TraceType.NATIVE: [],
            TraceType.BEFORE: [],
            TraceType.AFTER: []
        }

    def startup(self):
        '''Startup this hook'''
        self.log("Initialize Hook...")
        CmdHooks.__init__(
            self,
            self.db,
            self.prefixes,
            self.command_funcs["main"],
            self.lang,
            self.message_file
        )
        self.log("Initialize Schedule...")
        ScheduleHooks.__init__(
            self,
            self.schedule_funcs["main"]
        )
        self.pool.submit(self.schedule_thread)
        self.log("Start Trace")

    def trace_thread(self, data, traceTypeId):
        '''Call functions in tracer'''
        if traceTypeId not in self.targetDict.keys():
            raise ValueError("Invalid traceTypeId")
        if traceTypeId == TraceType.EVENT:
            self.event = data
        elif traceTypeId == TraceType.CONTENT:
            self.msg = data
        else:
            self.msg = data["message"]
            if not self.isCommand(data["message"]):
                return
        for f in self.targetDict[traceTypeId]["before"]:
            if f(self, data):
                break
        for f in self.targetDict[traceTypeId]["main"]:
            try:
                if f(self, data):
                    break
            except:
                self.log(f"[{traceTypeId}] {traceback.format_exc()}")
        for f in self.targetDict[traceTypeId]["after"]:
            if f(self, data):
                break

    def trace(self, data, traceTypeId):
        '''Trace with HookTracer'''
        self.pool.submit(self.trace_thread, data, traceTypeId)

    def log(self, text):
        '''Create log with HookTracer'''
        print("[{}] {}".format(str(datetime.now()), text))

    def addFunc(self, func, traceTypeId, bfTypeId=None):
        '''Add Function to HookTracer'''
        if traceTypeId not in self.targetDict.keys():
            raise ValueError("Invalid traceTypeId")
        # normal function
        if traceTypeId < 4:
            self.targetDict[traceTypeId]["main"].append(func)
        # native function
        elif traceTypeId == 4:
            exec(f"self.{func.__name__} = types.MethodType(func, self)")
        # before/after function
        elif traceTypeId > 4 and traceTypeId < 7:
            if bfTypeId not in self.targetDict.keys():
                raise ValueError("Invalid bfTypeId")
            if traceTypeId == 5:
                self.targetDict[bfTypeId]["before"].append(func)
            else:
                self.targetDict[bfTypeId]["after"].append(func)

    def addClass(self, _class):
        '''Add Class to HookTracer'''
        real_functions = [
            x[1]
            for x in inspect.getmembers(_class, predicate=inspect.ismethod)
        ]
        for func in real_functions:
            if hasattr(func, "tracerControlled"):
                if not hasattr(func, "bfTypeId"):
                    self.addFunc(func, func.traceTypeId)
                else:
                    self.addFunc(func, func.traceTypeId, func.bfTypeId)
            else:
                exec("self."+func.__name__+" = types.MethodType(func, self)")

    def genHelp(self, getAsList=False, prefixNum=0):
        '''Generate help message from command functions'''
        # Make CmdList
        cmds = [
            [
                self.prefixes[prefixNum] + cmd.__name__ if cmd.prefix
                else cmd.__name__,
                cmd.__doc__
            ]
            for cmd in self.command_funcs["main"]
            if cmd.__doc__ is not None
        ]
        cmds = [[cmd[0].replace("_", " "), cmd[1]] for cmd in cmds]
        # Return as list
        if getAsList:
            return cmds
        # Return as text
        txt = "[Command List]\n"
        txt += "\n".join([f"{c[0]} : {c[1]}" for c in cmds])
        return txt
