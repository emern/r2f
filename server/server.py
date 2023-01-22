"""This is a server - basic test"""

import command_response

if __name__ == '__main__':

    while 1:
        user_in = input("> ")

        valid_response = False
        for cmd in command_response.ALL_CMDS:
            if (user_in == cmd.name):
                cmd.func()
                valid_response = True

        if valid_response == False:
            print("Invalid command")