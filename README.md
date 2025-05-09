# ml-automation
autoplayer for mobile legends on PC

# Key bindings. Set accordingly
key_bindings = {
    "skill_1": "1",
    "skill_2": "2",
    "skill_3": "3",
    "move_up": "w",
    "move_down": "s",
    "move_left": "a",
    "move_right": "d",
    "attack_basic": "c",
    "attack_minion": "v",
    "attack_turret": "x",
    "upgrade_skill_1": "F1",
    "upgrade_skill_2": "F2",
    "upgrade_skill_3": "F3",
    "spell": "q",
    "regen": "e",
    "recall": "b",
    "buy": "space",
}

## rule-based.py
### Current functionality:
- movement : random movement at above 80% hp, when it drops to below 60% it moves randomly in a retreating way, below 30% is full retreat. This movement is purely based on move_down_left ..., not moving to a target coordinate, so retreating doesn't go to base in the quickest way

- HP calculation based on the bar is accurate

- Skills : spamming skills 1 and 2

### How to use:
0. (Optional) If you want to modify how the code interacts with the actual pressing of keys, modify mobilelegends_ai.ahk, then use the ahk2exe app to convert to a .exe. 
1. run rule-based.py. This will ask for 2 clicks to determine where the hp bar is. 1st click is top left of hp bar, 2nd click is bottom right.
2. once the 2 clicks are done, it will clear command.txt (so that left over commands from the past iteration are not used) and start mobilelegends_ai.exe
3. The player will start to move automatically. Stop mobilelegends_ai.exe using "esc" key or through task manager -> stop process
4. switch to the IDE and do ctrl + c to stop the code from running. Auto stopping has not been implemented

### Future development
- make a specific AI for supports, where they just follow a player of choice
    - if there is a nearby player on screen, follow that player, sticking to their south-west so that the healer is always in a safe spot.
    - if there isnt one, path to the nearest teammate based on the minimap
    - path to the teammate, then copy their movement so that the bot is always on their south-west
- recalling
    - mana detection, not just hp
    - tower, enemy detection
    - definition of "safe to recall" - near allied tower, no nearby enemies
- 
- once a rule-based version is more or less working, explore reinforcement learning

## teammate_detection.py
### Current functionality:
- self detection works, correctly identifies the bot on the minimap even with low hp, although the coordinates are not dead center. Unsure why, this code is mostly AI-ed so I dont rly understand it
- detection of teammates does not work. Sometimes identifies minions as teammates, sometimes even random spots in the jungle
