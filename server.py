import qnet3
import time
import database
from database import getUserByPassphrase, formatedBoard, getLastTraceByPassphrase, addUser
from nonblocking import input
import importlib
import botmanager
import schedule
from collections import Counter
from safelist import SafeList

CommandError = 'CommandError'
PassphraseError = 'PassphraseError'
RequestError = 'RequestError'

COMMAND_STACK = []

class HandleCommands(object):
    """docstring for HandleCommand."""

    @staticmethod
    def trace(user, conn, args, raw):
        conn.respond(
            getLastTraceByPassphrase(user['passphrase'])
        )
        return True


    @staticmethod
    def board(user, conn, args, raw):
        conn.respond(
            formatedBoard()
        )
        return True


    @staticmethod
    def upload(user, conn, args, raw):
        parts = raw.split('\n', 1)
        if len(parts) == 2:
            file = parts[1]
            with open('bots/' + user['passphrase'] + '.py', 'w') as f:
                f.write(file)
        else:
            conn.respond(CommandError)
            return True

class HandleAdminCommands(HandleCommands):
    @staticmethod
    def reset(user, conn, args, raw):
        COMMAND_STACK.append({
            'cmd'   : 'RESET',
            'args'  : args
        })

    @staticmethod
    def add(user, conn, args, raw):
        if args.get(0) == 'user' and len(args) >= 3:
            addUser(args[1], args[2], bool(args.get(3)))
        else:
            conn.respond(CommandError)
            return True


commands        = list(filter(lambda m: '__' not in m, dir(HandleCommands)))
adminsCommands  = list(filter(lambda m: '__' not in m, dir(HandleAdminCommands)))

def isValidCommand(command, isAdmin): # checks if the command is valid for the user
    return (isAdmin and command in adminsCommands) or command in commands

class Connector(qnet3.Connector):
    """docstring for Connector"""
    def message (self, msg):
        print("Received '{}' from [{}:{}]".format(msg, *self.addr))
        args = msg.split()
        if len(args) == 1:
            arg = args[0]
            if arg == 'who':
                return self.respond('Array Game III')
            elif arg == 'motd':
                return self.respond('If I had time I would implement a MOTD.')
            elif arg == 'help':
                return self.respond('Private Commands:\n\t<passphrase> ' + '\n\t<passphrase> '.join(commands))
        elif len(args) >= 2:
            passphrase = args.pop(0)
            command = args.pop(0)
            user = getUserByPassphrase(passphrase)
            if user:
                if isValidCommand(command, user['admin']):
                    print ('Passphrase:', passphrase)
                    print ('Command:', command)
                    if not getattr(HandleAdminCommands, command)(user, self, SafeList(args), msg):
                        self.respond('ok')
                    return
                return self.respond(CommandError)
            return self.respond(PassphraseError)
        return self.respond(RequestError)

while True:
    try:
        server = qnet3.Server('0.0.0.0', 7777, Connector)
        break
    except OSError as e:
        print (e)
        time.sleep(1)

def reset(hard=False):
    database.reset(hard)
    botmanager.reset(hard)

# def endMatch():
#     board = getTheBoard()
#     counted = Counter(board)
#     orderedCount = sorted(counted.keys())


schedule.every().day.at("8:30").do(reset)
database.init()

while True:
    server.update()
    botmanager.update()
    for bot in botmanager.bots:
        print(bot.__name__, 'MOVED', botmanager.execute(bot))
    schedule.run_pending()
    for _ in range(len(COMMAND_STACK)):
        item = COMMAND_STACK.pop(0)
        print (item)
        if item['cmd'] == 'RESET':
            hard = 'hard' in item['args']
            print('hard:', hard)
            reset(hard=hard)

    time.sleep(1)
