import json


class SystemMessageHandler():
    def __init__(self, language="EN", message_file=None):
        self.system_language = language
        if message_file:
            with open(message_file, "r", encoding="utf-8") as f:
                self.system_messages = json.loads(f.read())
        else:
            self.system_messages = {
                "EN": {
                    "NotCommand": [
                        "<CmdName> is not command.",
                        "Check command spelling and try again."
                    ],
                    "OutOfScope": [
                        "<CmdName> can not use in <WrongScope>.",
                        "It is useable in <TargetScope>."
                    ],
                    "NoPermission": [
                        "You don't have permission to do it.",
                        "Permission: <TargetPermission> is needed."
                    ],
                    "NoTicket": [
                        "You don't have enough tickets to do it.",
                        "<TargetTicket> x<NeedCount> are needed."
                    ],
                    "UseTicket": [
                        "You used <TargetTicket> x<NeedCount>.",
                        "Remaining Tickets: <NewCount>"
                    ]
                },
                "JA": {
                    "NotCommand": [
                        "<CmdName>というコマンドは存在しません"
                    ],
                    "OutOfScope": [
                        "<CmdName>は<WrongScope>では使用できません。",
                        "<TargetScope>でのみ使用できます"
                    ],
                    "NoPermission": [
                        "あなたは<CmdName>を実行する権限がありません。",
                        "権限<TargetPermission>が必要です"
                    ],
                    "NoTicket": [
                        "所持チケットが足りません。",
                        "このコマンドには<TargetTicket> x<NeedCount>が必要です。"
                    ],
                    "UseTicket": [
                        "<TargetTicket>チケットを<NeedCount>枚消費しました。",
                        "<OldCount>枚→<NewCount>枚"
                    ]
                }
            }

    def generateHandlerMessage(self, msg, error_type, data=None):
        system_message = self.system_messages[self.system_language][error_type]
        message_result = []
        for error_msg in system_message:
            error_msg = error_msg.replace("<CmdName>", msg["text"])
            if type == "OutOfScope":
                if msg.toType == 0:
                    error_msg = error_msg.replace("<WrongScope>", "1-1")
                elif msg.toType == 2:
                    error_msg = error_msg.replace("<WrongScope>", "Group")
                error_msg = error_msg.replace("<TargetScope>", str(data))
            elif type == "NoPermission":
                error_msg = error_msg.replace(
                    "<TargetPermission>",
                    " or ".join(data)
                )
            elif type == "NoTicket":
                error_msg = error_msg.replace("<TargetTicket>", str(data[0]))
                error_msg = error_msg.replace("<NeedCount>", str(data[1]))
            elif type == "UseTicket":
                error_msg = error_msg.replace("<TargetTicket>", str(data[0]))
                error_msg = error_msg.replace("<NeedCount>", str(data[1]))
                error_msg = error_msg.replace("<OldCount>", str(data[2]))
                error_msg = error_msg.replace("<NewCount>", str(data[3]))
            message_result.append(error_msg)
        return "\n".join(message_result)
