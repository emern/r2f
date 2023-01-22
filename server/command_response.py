"""
Command response framework
"""

import connection_handler

"""
Generic command response
"""
class cmd_arg_respose:
    def __init__(self, name, func, args):
        self.name = name
        self.func = func
        self.args = args

def cmd_not_implemented(args):
    print("Command not yet implemented")

def end_server():
    print("server shutting down")
    connection_handler.end_connection_handler()
    raise SystemExit(0)

# All valid command responses
CMD_RESPONSE_SHUTDOWN = cmd_arg_respose("shutdown", end_server, None)
CMD_RESPONSE_ENABLE = cmd_arg_respose("enable", connection_handler.start_connection_handler, None)
CMD_RESPONSE_SUSPEND = cmd_arg_respose("suspend", connection_handler.end_connection_handler, None)
CMD_RESPONSE_EXPORT_DB = cmd_arg_respose("export_db", cmd_not_implemented, None)
CMD_RESPONSE_EXPORT_VERBOSE = cmd_arg_respose("verbose", cmd_not_implemented, None)
CMD_RESPONSE_EXPORT_LOG = cmd_arg_respose("log_to_file", cmd_not_implemented, None)

# All commands to be added to command handler
ALL_CMDS = {
                CMD_RESPONSE_SHUTDOWN,
                CMD_RESPONSE_ENABLE,
                CMD_RESPONSE_SUSPEND,
                CMD_RESPONSE_EXPORT_DB,
                CMD_RESPONSE_EXPORT_VERBOSE,
                CMD_RESPONSE_EXPORT_LOG
            }