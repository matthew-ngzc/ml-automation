# ml-automation
autoplayer for mobile legends on PC. 

I have no idea if this works on linux or mac. Try at your own risk
# Setup (for non-tech users, follow all steps. For tech users skip to step 5)
1. Download VScode (a code editor to run the python code in) from [https://code.visualstudio.com/download](https://code.visualstudio.com/download) and run the installer
2. Download Python (language needed to run python script) from [https://www.python.org/downloads/](https://www.python.org/downloads/) and run the installer
   - make sure to check the option "add Python to environment variables" 
3. Create a new folder and open this folder in vscode. right click on this folder in the left bar and click on open integrated terminal. If dk how use chatgpt
4. run this command to install the needed dependencies
   - `pip install mss pynput opencv-python`, if it says pip unknown or something then search how to install pip
6. Place these 2 files inside the folder (download from this github by clicking onto the files and then the download icon (download raw file) )
    1. mobilelegends_ai.exe (this will give a warning, press "keep" if u trust me lol)
    2. rule-based.py
7. Download the mobile legends game on PC (through the google play store beta, or emulators)
8. Set keybindings accordingly in your emulator / mobile legends app
    <details>
    <summary>Click to view key bindings (can also be found in the .ahk script)</summary>
    
    ```py
    key_bindings = {
        "skill_1": ["k"],
        "skill_2": ["l"],
        "skill_3": [";"],
        "skill_4": ["'"],
        "upgrade_skill_1": ["l"],
        "upgrade_skill_2": ["o"],
        "upgrade_skill_3": ["p"],
        "upgrade_skill_4": ["["],
        "skill_1_extra": ["i"],
        "skill_2_extra": ["o"],
        "skill_3_extra": ["p"],
        "skill_4_extra": ["["],
        "move_up": ["w"],
        "move_down": ["s"],
        "move_left": ["a"],
        "move_right": ["d"],
        "move_up_right": ["w", "d"],
        "move_up_left": ["w", "a"],
        "move_down_right": ["s", "d"],
        "move_down_left": ["s", "a"],
        "attack_basic": ["j"],
        "attack_minion": ["n"],
        "attack_turret": ["u"],
        "spell": ["h"],
        "regen": ["g"],
        "recall": ["b"],
        "buy": ["Space"],
        "chat": ["Enter"],
        "skill_item": ["f"]
    }
    </details>
    ```
9. Set the in-game minimap to maximum size, flushed to the top left side of the screen
10. Turn on auto-buy, and auto-upgrade skills, timers to 0 because I don't intend to implement those
11. Make sure the build is configured correctly since it autobuys
  

## rule-based.py
### Current functionality:
- movement : random movement at above 80% hp, when it drops to below 60% it moves randomly in a retreating way, below 30% is full retreat. This movement is purely based on move_down_left ..., not moving to a target coordinate, so retreating doesn't go to base in the quickest way

- HP calculation based on the bar is accurate

- Skills : spamming skills 1 and 2

### How to use:
0. (Optional) If you want to modify how the code interacts with the actual pressing of keys, modify `mobilelegends_ai.ahk`, then use the ahk2exe app to convert to a .exe. Download ahk from https://www.autohotkey.com/
1. run `rule-based.py`. This will ask for 2 clicks to determine where the hp bar is. 1st click is top left of hp bar, 2nd click is bottom right.
2. once the 2 clicks are done, it will clear `command.txt` (so that left over commands from the past iteration are not used) and start mobilelegends_ai.exe
3. The player will start to move automatically. Stop mobilelegends_ai.exe using `Esc` key or through task manager -> stop process
4. switch to the IDE and do `ctrl + c` to stop the code from running. Auto stopping has not been implemented (TODO: detect based on computer vision of the screen, lookout for the tap to continue, or some other UI since it is fixed)

### Future development
- make a slightly smarter AI, such that it moves until unsafe location, and hovers (dodge) around the unsafe location
    - can define unsafe as a place where they took damage?
    - or an unsafe location is at the outermost alive turret? 
- make a specific AI for supports, where they just follow a player of choice
    - if there is a nearby player on screen, follow that player, sticking to their south-west so that the healer is always in a safe spot.
    - if there isnt one, path to the nearest teammate based on the minimap
    - path to the teammate, then copy their movement so that the bot is always on their south-west
- recalling
    - mana detection, not just hp. For below 30% hp go to safety and recall
      - mana is just offset from the hp bar , not sure if need to click to determine the mana box as well. Have a boolean for heroes with no mana
    - tower, enemy detection (nextime, for now just do path to tower)
    - definition of "safe to recall" - near allied tower, no nearby enemies
        - path to the nearest alive allied tower (hardcode the coordinates or the ally towers and the base on the minimap, use computer vision to check if the tower is alive -> check for blue pigment)
        - if cannot hardcode then do the same strat, just click on all the towers or something
- once a rule-based version is more or less working, explore reinforcement learning

## teammate_detection.py
### Current functionality:
- self detection works, correctly identifies the bot on the minimap even with low hp, although the coordinates are not dead center. Unsure why, this code is mostly AI-ed so I dont rly understand it
- detection of teammates does not work. Sometimes identifies minions as teammates, sometimes even random spots in the jungle
- turret detection not tested, code is AI-ed
