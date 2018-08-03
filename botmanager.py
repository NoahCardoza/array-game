import os
import sys
from glob import glob
import importlib
import hashlib
from functools import partial
from database import getTheBoard, setTheBoard, getUserByPassphrase, formatedBoard, updateUserByPassphrase
import traceback
import logging

from logger import logger

import signal

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

sandbox = True
bots = []

class BotReturnException(Exception):
    pass

def saveTraceByPassphrase(passphrase):
    logger.error('HandledException ({}): {}'.format(passphrase, sys.exc_info()[1]))
    with open('traces/' + passphrase + '.traceback', 'w') as f:
        traceback.print_exc(file=f)

def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

def wi(i): # wrap index
    i %= 64
    if i < 0:
        i += 64
    return i

def getBotPassphrase(bot):
    return bot.__name__.split('.')[1]

def execute(bot):
    move = None
    board = getTheBoard()
    passphrase = getBotPassphrase(bot)
    user = getUserByPassphrase(passphrase)
    if user and user['health']:
        try:
            with timeout(seconds=0.5):
                move = bot.run(formatedBoard())
        except:
            bot.__timeouts__ += 1
            saveTraceByPassphrase(passphrase)
        else:
            try:
                if type(move) == int:
                    if move == 0:
                        pass
                    elif move == 1:
                        user['index'] = wi(user['index'] + 1)
                    elif move == -1:
                        user['index'] = wi(user['index'] - 1)
                    elif move == 2:
                        if board[user['index']] != user['char']: # can take the tile
                            board[user['index']] = user['char']
                            user['health'] -= 4 # because we will add one at the end
                        else:
                            raise BotReturnException("TileIsYours")
                    else:
                        raise BotReturnException("InvalidReturnInt")
                else:
                    raise BotReturnException("ReturnValueNotInt")
                hpChange = (board[user['index']] == user['char']) or -1
                # print ('User:', user['char'], 'is on a', board[user['index']], 'tile. Health +=', hpChange)
                newHealth = user['health'] + hpChange
                if newHealth <= 0: # dead
                    # print ('Robot {} died.'.format(user['char']))
                    if sandbox:
                        # print ('Sandbox mode active. Reviving now.')
                        board = ['X' if tile == user['char'] else tile for tile in board]
                        newHealth = 50
                        user['index'] = 0
                    else:
                        user['health'] = 0
                user['health'] = newHealth if newHealth <= 1000 else 1000
                setTheBoard(board)
                updateUserByPassphrase(**user)
            except BotReturnException:
                saveTraceByPassphrase(passphrase)
            except:
                logger.exception('botmanager.execute encountered an internal error')

    return move

class brokenBot(object):
    def run(self, board):
        return 0

def importBot(name, useBroken=False):
    pwd = os.getcwd()
    try:
        if useBroken:
            # A hack to skip the except block. Used for replacing bots that
            # violate timeout restrictions too often
            raise Exception('Use brokenBot instance.')
        if sys.modules.get('bots.' + name): raise BaseException('AlreadyImported')
        module = importlib.import_module('bots.' + name)
        module.__broken__ = False
    except:
        # this means that there was an error reloadeing and we sould fill it's
        # place with a brokenBot instance
        logger.debug('Initiating Broken Bot')
        module = brokenBot()
        module.__broken__ = True
        module.__name__ = 'bots.' + name
        module.__file__ = pwd + '/bots/' + name + '.py'
    module.__timeouts__ = 0
    return module

def update():
    global bots
    pwd = os.getcwd()
    files = set([pwd + '/' + f for f in glob('bots/*.py')])
    filesInUse = set([bot.__file__ for bot in bots])
    toBeLoaded = files - filesInUse
    botsInUse = bots.copy()
    # print ('toBeLoaded:', toBeLoaded)
    for path in toBeLoaded:
        hash = md5sum(path)
        filename = path.rsplit('/', 1)[1]
        name = filename.split('.')[0]
        module = importBot(name)
        logger.debug('Bot Loaded: ' + str(module))
        module.__hash__ = hash
        bots.append(module)

    for h, m in zip(map(md5sum, filesInUse), botsInUse):
        if h != m.__hash__:
            m.__hash__ = h
            try:
                if (m.__broken__):
                    module = importBot(getBotPassphrase(m))
                    module.__hash__ = h
                    bots[bots.index(m)] = module
                else:
                    logger.debug('Bot Reloaded: ' + str(importlib.reload(m)))
            except:
                passphrase = getBotPassphrase(m)
                module = importBot(passphrase)
                module.__hash__ = h
                bots[bots.index(m)] = module
                saveTraceByPassphrase(passphrase)
        elif m.__timeouts__ > 5:
            logger.debug('Reoccurring timeout error detected.')
            passphrase = getBotPassphrase(m)
            module = importBot(passphrase)
            module.__hash__ = h
            bots[bots.index(m)] = module
            with open('traces/' + passphrase + '.traceback', 'a') as f:
                f.write('\n\nYour bot has been suspended because of too many timeouts.')


def reset(hard=False):
    if hard:
        [os.remove(f) for f in glob('bots/*.py')]
    [os.remove(f) for f in glob('traces/*')]
    for _ in range(len(bots)):
        bot = bots.pop(0)
        if not bot.__broken__: # if is isn't a real module, you can't remove it from sys.modules
            del sys.modules[bot.__name__]
