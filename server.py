import qnet3
import time
import database
from database import getUserByPassphrase, formatedBoard, getLastTraceByPassphrase, addUser
import importlib
import botmanager
import schedule
from collections import Counter
from safelist import SafeList
from logger import logger

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
        logger.debug("Received '{}' from [{}:{}]".format(msg, *self.addr))
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
                    logger.debug('Passphrase:', passphrase)
                    logger.debug('Command:', command)
                    if not getattr(HandleAdminCommands, command)(user, self, SafeList(args), msg):
                        self.respond('ok')
                    return
                return self.respond(CommandError)
            return self.respond(PassphraseError)
        return self.respond(RequestError)

def reset(hard=False):
    database.reset(hard)
    botmanager.reset(hard)

def dailyReset():
    logger.debug('Starting 8:30 reset...')
    reset()
    logger.debug('Reset complete.')

# def endMatch():
#     board = getTheBoard()
#     counted = Counter(board)
#     orderedCount = sorted(counted.keys())

schedule.every().day.at("8:30").do(dailyReset)
database.init()
server = None

def main(server):
    while True:
        server.update()
        botmanager.update()
        for bot in botmanager.bots:
            botmanager.execute(bot)
            # logger.debug(bot.__name__, 'MOVED', botmanager.execute(bot))
        schedule.run_pending()
        for _ in range(len(COMMAND_STACK)):
            item = COMMAND_STACK.pop(0)
            if item['cmd'] == 'RESET':
                hard = 'hard' in item['args']
                reset(hard=hard)
        time.sleep(1)



while True:
    while not server:
        try:
            server = qnet3.Server('0.0.0.0', 7777, Connector)
            break
        except OSError as e:
            logger.error(e)
            time.sleep(5)
    try:
        logger.debug('Server listening on port 7777.')
        main(server)
    except KeyboardInterrupt:
        server.sock.close()
        print ("\nHave a good day!")
        exit()
    except:
        logger.exception('The server encountered an internal error. Restarting')
        time.sleep(5)
