# Array Game
A Python 3 server game

## The Rules

+ The board is a one-dimensional array of 64 tiles. Each tile belongs to a player.
+ Each player controls one robot. Each turn, the robot can perform one of four actions:
    + Do nothing.
    + Move to the tile to the left, or to the tile to the right. The board wraps around – moving off the left of the board will put a robot at the right side.

    + Make the tile underneath the robot belong to the player (i.e. “flip” the tile).

+ Each robot has an amount of energy. If the amount of energy reaches zero, the robot dies and will no longer move around or change tiles. In Sandbox Mode, when a robot dies, it will be restored to health (with energy equal to 50) and moved back to tile 0. The server will be in Sandbox Mode for now.
+ If a robot moves onto a tile that does not belong to it, it loses 1 energy.

+ If a robot moves onto a tile that does belong to it, it gains 1 energy.

+ Flipping a tile – that is, making it belong to the robot – costs 3 energy.

+ Each player has a secret password, which is a pair of words.

+ Each robot gets a turn once per second, non-stop.

+ The maximum energy for a robot is 1000.

+ Every morning, at 8:30, the player with the most tiles is recorded as the winner. The server then resets – all tiles, energy values, and robot positions are reset, but all robot code is preserved (i.e. the most recent version of code uploaded to the robot will automatically start running again).

+ May the best robot win!

# Debugging:
If your program encounters an error, the last error message will be stored. You can request it by calling for the trace:
```py
connection.converse("<passphrase> trace")
```

or if you are using the `shell.py` script we made in class:

```sh
> trace
```
# Checking the board:

While your function will get the board passed to it, that doesn't let you see it.

If you want to see the board, run `shell.py` and type `board` then press enter.

```sh
> board
De50DDDDDd355DDBBBBBBBBBBBBBBBBBBBBBBBb189BBBBBAACAACc77ACAa78ACCCCCCCCCCXXXXBDDD
```

Each upper case character is a tile. The letter points to the player who owns it.
The lower case characters are the players. They are followed by a number which is
their health.

The `b` robot in the above example has `189` health.

# The bot code:

The code you upload must contain a function named `run`

### The most simple bot:
```py
import random

def run(board):
    return random.randint(-1, 2)

```

The run function must return an integer inclusively between -1 and 2.

### Returning a command from your run function:

| Command | Does                                  |
| ------- | ------------------------------------- |
| `-1`    | Moves your bot one tile to the left.  |
| `0`     | Doesn't move your bot at all.         |
| `1`     | Moves your bot one tile to the right. |
| `2`     | Flip the tile (make it yours).        |

# The never ending while loop:

If you think you need to use a while loop, use it with caution. If you program the
logic incorrectly, you could create an infinite loop and freeze the server. To protect
against this, your function will timeout if it runs too long.

# Good luck!


## Todo

1. add more documentation
2. make it esier for others to setup their own servers
