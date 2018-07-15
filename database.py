import os
from tinydb import TinyDB, Query, Where
# from tinydb.operations import delete
from functools import partial

db = TinyDB('db.json')
Object = Query()
Users = db.table('users')
join = ''.join

def getNextChar(static=dict(char='A'), reset=False):
    if reset:
        static['char'] = 'A'
    else:
        c = static['char']
        if c == 'Z':
            raise Exception('No more characters can be added to the server at this time.')
        static['char'] = chr(ord(c) + 1)
        if getUserByChar(c):
            return getNextChar()
        return c

def init():
    if not db.contains(Object.type == 'board'): # set defaults
        db.insert({
            'type': 'board',
            'board': ['X'] * 64
        })

    if not Users.contains(Object.admin == True):
        print ('It looks like there are no admins. At least one will be required to run the server.')
        name = input('Name: ')
        passphrase = input('Passphrase: ')
        addUser(name, passphrase, admin=True)


        # # sample data
        # Users.insert({
        #     'passphrase': 'killerkido',
        #     'name': 'Noah',
        #     'char': 'A',
        #     'index': 0,
        #     'health': 50,
        #     'admin': True
        # })
        #
        # Users.insert({
        #     'passphrase': 'blackjack',
        #     'name': 'Nick',
        #     'char': 'B',
        #     'index': 0,
        #     'health': 50,
        #     'admin': False
        # })
        #
        # Users.insert({
        #     'passphrase': 'tensetesla',
        #     'name': 'Chris',
        #     'char': 'C',
        #     'index': 0,
        #     'health': 50,
        #     'admin': False
        # })
        #
        # Users.insert({
        #     'passphrase': 'antman',
        #     'name': 'Anthony',
        #     'char': 'D',
        #     'index': 0,
        #     'health': 50,
        #     'admin': False
        # })
        #
        # Users.insert({
        #     'passphrase': 'madmax',
        #     'name': 'Max',
        #     'char': 'E',
        #     'index': 0,
        #     'health': 50,
        #     'admin': False
        # })


def getTheBoard():
    return db.get(Object.type == 'board')['board']

def setTheBoard(board):
    db.update({
     'board': board
    }, Object.type == 'board')

def getUserBy(key, value):
    return Users.get(Object[key] == value)

getUserByPassphrase = partial(getUserBy, 'passphrase')
getUserByChar = partial(getUserBy, 'char')

def updateUserByPassphrase(passphrase, **kwargs):
    return Users.update(kwargs, Object.passphrase == passphrase)

def getAllUsers():
    return Users.all()

def formatUser(user):
    return f"{user['char'].lower()}{user['health']}"

formatUsers = partial(map, formatUser)

def filterByIndex(users, i):
    return filter(lambda u: u['index'] == i, users)

def formatedBoard():
    filterUsersByIndex = partial(filterByIndex, getAllUsers())
    return join([tile + join(formatUsers(filterUsersByIndex(i))) for (i, tile) in enumerate(getTheBoard())])

def getLastTraceByPassphrase(passphrase):
    filepath = 'traces/' + passphrase + '.traceback'
    if os.path.isfile(filepath):
        with open(filepath, 'r') as f:
            # hide our current path
            return f.read().replace(os.getcwd(), '')
    else:
        return 'none'

def reset(hard=False):
    setTheBoard(['X'] * 64)
    if hard:
        Users.remove(Object.admin != True)
        Users.update({
            'health': 50,
            'index': 0
        }, Object.admin == True)
    else:
        for u in getAllUsers():
            updateUserByPassphrase(u['passphrase'], health=50, index=0)

def addUser(name, passphrase, admin=False):
    Users.insert({
        'name': admin,
        'passphrase': passphrase,
        'char': getNextChar(),
        'index': 0,
        'health': 50,
        'admin': admin
    })

#
# if __name__ == '__main__':
#     print(getNextChar())
#     print(getNextChar())
#     print(getNextChar())
