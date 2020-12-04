from functools import wraps
from ..message import SystemMessageHandler
import traceback
import json


class CmdHooks(object):
    def __init__(self, dbHandler, prefixes, command_funcs, lang, message_file):
        self.db = dbHandler
        self.prefixes = prefixes
        self.command_funcs = command_funcs
        self.supported_cmds = []
        self.buildPossibleCommands()
        self.sys = SystemMessageHandler(lang, message_file)

    def buildPossibleCommands(self):
        # Make Cmd List
        self.supported_cmds = []
        for c in self.command_funcs:
            # Add function name
            if c.usePrefix and c.ignoreCase:
                self.supported_cmds.append(
                    [
                        k + c.__name__.lower().replace("_", " ")
                        for k in self.prefixes
                    ]
                )
            elif c.usePrefix:
                self.supported_cmds.append(
                    [
                        k + c.__name__.replace("_", " ")
                        for k in self.prefixes
                    ]
                )
            elif c.ignoreCase:
                self.supported_cmds.append(
                    [c.__name__.lower().replace("_", " ")]
                )
            else:
                self.supported_cmds.append(
                    [c.__name__.replace("_", " ")]
                )
            # Add alt name
            for a in c.alt:
                if c.usePrefix and c.ignoreCase:
                    self.supported_cmds.append(
                        [
                            k + a.lower().replace("_", " ")
                            for k in self.prefixes
                        ]
                    )
                elif c.usePrefix:
                    self.supported_cmds.append(
                        [
                            k + a.replace("_", " ")
                            for k in self.prefixes
                        ]
                    )
                elif c.ignoreCase:
                    self.supported_cmds.append(
                        [a.lower().replace("_", " ")]
                    )
                else:
                    self.supported_cmds.append(
                        [a.replace("_", " ")]
                    )
        self.supported_cmds = [c for in_p in self.supported_cmds for c in in_p]

    def isCommand(self, msg):
        if any(
            [
                msg["text"].lower() in self.supported_cmds,
                msg["text"] in self.supported_cmds,
                any([
                    msg["text"].startswith(c)
                    for c in self.supported_cmds
                ]),
                any([
                    msg["text"].lower().startswith(c)
                    for c in self.supported_cmds
                ])
            ]
        ):
            return True
        elif self.getPrefix(msg["text"]) != "":
            self.sys.generateHandlerMessage(msg, "NotCommand")
        return False

    def scopeCheck(self, msg, sources):
        '''Check Scope (For Content/Command)'''
        # From Group
        if msg["source"]["type"] == "group":
            # If accept AllGroup or mid in sources
            if "Group" in sources or msg["source"]["groupId"] in sources:
                return True
            # If groupType registered
            chk_ls = [g for g in self.db.getScopeList() if g in sources]
            if chk_ls != []:
                isGroupInScope = [
                    g for g in chk_ls
                    if msg["source"]["groupId"] in self.db.getScopeByName(g)
                ]
                if isGroupInScope:
                    return True
        # From 1-1
        elif msg["source"]["type"] == "user":
            # If accept from ALL or mid in sources
            if "User" in sources or msg["source"]["userId"] in sources:
                return True
            # If userType registered
            chk_ls = [u for u in self.db.getScopeList() if u in sources]
            if chk_ls != []:
                isUserInScope = [
                    g for g in chk_ls
                    if msg["source"]["userId"] in self.db.getScopeByName(g)
                ]
                if isUserInScope:
                    return True
        return False

    def permissionCheck(self, msg, permissions):
        '''Check Permission (For Content/Command)'''
        if permissions in [[], ["ALL"]]:
            return True
        hasPermission = [
            p for p in permissions
            if msg["source"]["userId"] in self.db.getPermissionByName(p)
        ]
        if hasPermission:
            return True
        return False

    def databaseCheck(self, check_method, id_param, kwargs):
        for k in kwargs:
            # a=1
            if type(kwargs[k]).__name__ == "int":
                if check_method(id_param, k) != kwargs[k]:
                    return False
            # a=">1"
            elif ">" in kwargs[k]:
                value = int(kwargs[k][1:])
                if check_method(id_param, k) < value:
                    return False
            elif "<" in kwargs[k]:
                value = int(kwargs[k][1:])
                if check_method(id_param, k) > value:
                    return False
            # a=">=1"
            elif ">=" in kwargs[k]:
                value = int(kwargs[k][2:])
                if check_method(id_param, k) <= value:
                    return False
            elif "<=" in kwargs[k]:
                value = int(kwargs[k][2:])
                if check_method(id_param, k) >= value:
                    return False
            # a="1"
            else:
                value = int(kwargs[k])
                if check_method(id_param, k) != value:
                    return False
            # TODO: ADD String check
        return True

    def userDataCheck(self, msg, **kwargs):
        '''Check UserDatas (For Content/Command)'''
        return self.databaseCheck(
            self.db.getUser,
            msg["source"]["userId"],
            kwargs
        )

    def groupDataCheck(self, msg, **kwargs):
        '''Check GroupDatas (For Content/Command)'''
        return self.databaseCheck(
            self.db.getGroup,
            msg["source"]["userId"],
            kwargs
        )

    def messageCheck(self, msg, func, **kwargs):
        '''Check Message (For Command)'''
        # Check IsCallingThisFunction
        msg_text = msg["message"]["text"]
        msg_text = msg_text.lower() if func.ignoreCase else msg_text
        if func.inpart:
            if not any([msg_text.startswith(c) for c in func.cmds]):
                return False
        else:
            if msg_text not in func.cmds:
                return False
        # Check IsInScope
        if not self.scopeCheck(msg, func.sources):
            self.sys.generateHandlerMessage(
                msg, "OutOfScope",
                func.sources
            )
            return "break"
        # Check HasPermission
        if not self.permissionCheck(msg, func.permissions):
            self.sys.generateHandlerMessage(
                msg, "NoPermission",
                func.permissions
            )
            return "break"
        # Check HasGroupVariable
        if "groupData" in kwargs:
            if not self.groupDataCheck(msg, **kwargs):
                return "break"
        # Check HasUserVariable
        else:
            if not self.userDataCheck(msg, **kwargs):
                return "break"
        return True

    def getArg(self, cmd_names, msg_text, ignoreCase, splitKey=" "):
        # This can't use with mention by whitespace in displayName.
        if ignoreCase:
            msg_text = msg_text.lower()
        for c in cmd_names:
            if c in msg_text:
                s = msg_text.find(c)
                if s != -1:
                    arg = msg_text[len(c)+s+1:].split(splitKey)
                    if arg not in [[''], []]:
                        arg = [a for a in arg if a[0] != "@"]
                    return arg
        return []

    def getPrefix(self, msg_text):
        for x in self.prefixes:
            if msg_text.startswith(x):
                return x
        return ""

    def Event(self, type):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 0

            @wraps(func)
            def __check(self, *args):
                # tracer, tracer.cl,
                if args[0].event["type"] == type:
                    func(self, args[0], args[0].cl, args[1])
                    return True
            return __check
        return __wrapper

    def Content(
        self,
        type,
        sources=["User", "Group"],
        permissions=["ALL"],
        **d_kwargs
    ):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 1
            func.sources = sources
            func.permissions = permissions

            @wraps(func)
            def __check(self, *args):
                if args[0].msg['message']['type'] == type:
                    if not args[0].scopeCheck(args[0].msg, sources):
                        return True
                    if not args[0].permissionCheck(args[0].msg, permissions):
                        return True
                    if args[0].userDataCheck(args[0].msg, **d_kwargs):
                        func(self, args[0], args[0].cl, args[1])
                        return True
            return __check
        return __wrapper

    def Command(
        self,
        alt=[],
        sources=["User", "Group"],
        permissions=["ALL"],
        usePrefix=True,
        inpart=False,
        ignoreCase=False,
        pattern=None,
        **dkwargs
    ):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 2
            func.alt = alt
            func.sources = sources
            func.permissions = permissions
            func.usePrefix = usePrefix
            func.inpart = inpart
            func.ignoreCase = ignoreCase
            func.pattern = pattern
            if usePrefix and ignoreCase:
                cmds = [
                    [
                        f"{p}{name.lower().replace('_', ' ')}"
                        for p in self.prefixes
                    ]
                    for name in alt + [func.__name__]
                ]
                cmds = sum(cmds, [])
            elif usePrefix:
                cmds = [
                    [
                        f"{p}{name.replace('_', ' ')}"
                        for p in self.prefixes
                    ]
                    for name in alt + [func.__name__]
                ]
                cmds = sum(cmds, [])
            elif ignoreCase:
                cmds = [
                    f"{name.lower().replace('_', ' ')}"
                    for name in alt + [func.__name__]
                ]
            else:
                cmds = [
                    f"{name.replace('_', ' ')}"
                    for name in alt + [func.__name__]
                ]
            func.cmds = cmds
            @wraps(func)
            def __check(self, *args, **kwargs):
                chk = args[0].messageCheck(args[1], func, **dkwargs)
                if chk:
                    try:
                        # I DON'T KNOW WHY, BUT THIS WORKS
                        if len(args) == 2:
                            func(self, args[0], args[0].cl, args[1])
                        else:
                            func(self, args[0], args[0].cl, args[2])
                        return True
                    except:
                        args[0].log("[Command] "+traceback.format_exc())
                elif chk == "break":
                    return True
            return __check
        return __wrapper

    def Before(self, type):
        '''
         type:
            0: Operation
            1: Content
            2: Command
        '''
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 5
            func.bfTypeId = type

            @wraps(func)
            def __bf(self, *args, **kwargs):
                func(self, args[0], args[0].cl, args[1])
            return __bf
        return __wrapper

    def After(self, type):
        def __wrapper(func):
            func.tracerControlled = True
            func.traceTypeId = 6
            func.bfTypeId = type

            @wraps(func)
            def __af(self, *args, **kwargs):
                func(self, args[0], args[0].cl, args[1])
            return __af
        return __wrapper


'''
Event = CmdHooks().Event
Content = CmdHooks().Content
Command = CmdHooks().Command
'''
