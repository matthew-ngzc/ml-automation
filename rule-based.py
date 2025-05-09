# === COORDINATES (from full screen) ===
# minimap: top=0, bottom=341, left=0, right=338
# item suggested: top=110, bottom=188, left=1667, right=1756
# skill 1: top=1002, bottom=1144, left=1380, right=1543
# skill 2: top=788, bottom=947, left=1489, right=1657
# skill 3: top=674, bottom=839, left=1692, right=1857

#Rafaela
# hp bar: top=476, bottom=496, left=886, right=1065
# mana bar: top=495, bottom=505, left=886, right=1066

import os
import cv2
import numpy as np
import mss
import time
from pynput import mouse
import random
import subprocess


# === SCREEN REGION SETTINGS ===
monitor = {
    "top": 0,
    "left": 0,
    "width": 1920,
    "height": 1200
}

# === KEY BINDINGS ===
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

# === RAFAELA HP BAR COORDINATES ===
#no longer hardcoding
# top = 476
# bottom = 496
# left = 886
# right = 1065

# === COLOR RANGE FOR GREEN HP BAR ===
lower_green = np.array([50, 100, 100])
upper_green = np.array([70, 255, 255])

# === Global state ===
last_command = None
last_skill_time = 0

hp_top = hp_bottom = hp_left = hp_right = None
clicks = []

def on_click(x, y, button, pressed):
    if pressed:
        clicks.append((x, y))
        if len(clicks) == 1:
            print(f"Click on the TOP-LEFT corner of the HP bar: ({x}, {y})")
        elif len(clicks) == 2:
            print(f"Click on the BOTTOM-RIGHT corner of the HP bar: ({x}, {y})")
            return False  # Stop listener after second click


def send_command(command: str):
    global last_command
    if command != last_command:
        base_path = os.path.dirname(os.path.abspath(__file__))  # Folder where script is saved
        file_path = os.path.join(base_path, "command.txt")
        with open(file_path, "w") as f:
            f.write(command)
        print(f"[COMMAND] {command} → {file_path}")
        last_command = command


def get_hp_coordinates_from_mouse():
    print("🖱️ You will be prompted to click twice:")
    print("• First: top-left of the HP bar")
    print("• Second: bottom-right of the HP bar")
    print("")

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    (x1, y1), (x2, y2) = clicks
    hp_left = min(x1, x2)
    hp_right = max(x1, x2)
    hp_top = min(y1, y2)
    hp_bottom = max(y1, y2)

    print(f"\n✅ HP bar region confirmed: top={hp_top}, bottom={hp_bottom}, left={hp_left}, right={hp_right}")
    return hp_top, hp_bottom, hp_left, hp_right

# === HP BAR PROCESSING ===
def get_hsv_ranges_from_sample(hsv_pixel, h_tol=10, s_tol=80, v_tol=80):
    h, s, v = map(int, hsv_pixel)  # Convert from np.uint8 to normal Python ints

    h_low = (h - h_tol) % 180
    h_high = (h + h_tol) % 180

    s_low = max(s - s_tol, 0)
    s_high = min(s + s_tol, 255)
    v_low = max(v - v_tol, 0)
    v_high = min(v + v_tol, 255)

    if h_low > h_high:
        return [
            (np.array([0, s_low, v_low]), np.array([h_high, s_high, v_high])),
            (np.array([h_low, s_low, v_low]), np.array([179, s_high, v_high]))
        ]
    else:
        return [(np.array([h_low, s_low, v_low]), np.array([h_high, s_high, v_high]))]



def get_hp_ratio(frame, hp_top, hp_bottom, hp_left, hp_right):
    # Crop the HP bar from screen
    hp_bar = frame[hp_top:hp_bottom, hp_left:hp_right]
    hsv_img = cv2.cvtColor(hp_bar, cv2.COLOR_BGR2HSV)

    # Sample a 4x4 region at the center of the bar
    center_h = (hp_bottom - hp_top) // 2
    center_w = (hp_right - hp_left) // 2
    sample_region = hsv_img[center_h - 2:center_h + 2, center_w - 2:center_w + 2]
    hsv_sample = np.mean(sample_region.reshape(-1, 3), axis=0).astype(np.uint8)

    print(f"Sample HSV value: {hsv_sample}")
    hsv_ranges = get_hsv_ranges_from_sample(hsv_sample)

    # Combine masks from all hue ranges
    combined_mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    for lower, upper in hsv_ranges:
        mask = cv2.inRange(hsv_img, lower, upper)
        combined_mask = cv2.bitwise_or(combined_mask, mask)

    green_pixels = np.sum(combined_mask > 0)
    total_pixels = combined_mask.shape[0] * combined_mask.shape[1]
    ratio = green_pixels / total_pixels if total_pixels else 0

    # Debug windows
    cv2.imshow("HP Region", hp_bar)
    cv2.imshow("Green Mask", combined_mask)
    cv2.waitKey(1)

    print(f"[HP] Ratio: {ratio:.2f}")
    return ratio



# === MOVEMENT DECISION LOGIC ===
def decide_movement(hp_ratio):
    if hp_ratio < 0.3:
        print("[LOGIC] Retreating (down + left)")
        send_command("move_down_left")
    elif hp_ratio < 0.6:
        action = random.choice([
            "move_down",
            "move_left",
            "move_down_left", "move_down_right",
            "stand_still"
        ])
        print(f"[LOGIC] Dodging: {action}")
        send_command(action)
    else:
        action = random.choice([
            "move_up", "move_down",
            "move_left", "move_right",
            "move_up_left", "move_up_right",
            "move_down_left", "move_down_right",
            "stand_still"
        ])
        print(f"[LOGIC] Advancing phase: random action → {action}")

        if action == "stand_still":
            send_command("")  # No key press
        else:
            send_command(action)

def move_toward_target(bot_pos, target_pos, coordinate_space="minimap"):
    dx = target_pos[0] - bot_pos[0]
    dy = target_pos[1] - bot_pos[1]

    threshold = 5 if coordinate_space == "minimap" else 20  # screen pixels are larger scale

    if abs(dx) < threshold and abs(dy) < threshold:
        return  # already close enough

    if dx > 0 and dy > 0:
        send_command("move_down_right")
    elif dx > 0 and dy < 0:
        send_command("move_up_right")
    elif dx < 0 and dy > 0:
        send_command("move_down_left")
    elif dx < 0 and dy < 0:
        send_command("move_up_left")
    elif abs(dx) > abs(dy):
        send_command("move_right" if dx > 0 else "move_left")
    else:
        send_command("move_down" if dy > 0 else "move_up")


# def detect_teammates_on_minimap(minimap_bgr):
#     minimap_hsv = cv2.cvtColor(minimap_bgr, cv2.COLOR_BGR2HSV)

#     # Teammate ring appears blue; let's use a blue range
#     lower_blue = np.array([90, 80, 80])
#     upper_blue = np.array([130, 255, 255])

#     mask = cv2.inRange(minimap_hsv, lower_blue, upper_blue)

#     # Find contours of blue rings
#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     teammate_positions = []
#     for cnt in contours:
#         area = cv2.contourArea(cnt)
#         if 20 < area < 200:  # filter out tiny noise and giant blobs
#             M = cv2.moments(cnt)
#             if M["m00"] != 0:
#                 cx = int(M["m10"] / M["m00"])
#                 cy = int(M["m01"] / M["m00"])
#                 teammate_positions.append((cx, cy))

#     return teammate_positions

# def detect_teammates_on_screen(frame):
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
#     # Blue glow/HP arc detection around allies
#     lower_blue = np.array([90, 80, 80])
#     upper_blue = np.array([130, 255, 255])

#     mask = cv2.inRange(hsv, lower_blue, upper_blue)
#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     positions = []
#     for cnt in contours:
#         area = cv2.contourArea(cnt)
#         if 100 < area < 1000:
#             M = cv2.moments(cnt)
#             if M["m00"] != 0:
#                 cx = int(M["m10"] / M["m00"])
#                 cy = int(M["m01"] / M["m00"])
#                 positions.append((cx, cy))
#     return positions


# === MAIN LOOP ===
def main():
    global last_skill_time

    # Prompt for HP coordinates
    hp_top, hp_bottom, hp_left, hp_right = get_hp_coordinates_from_mouse()


    print("⏳ Switch to the game window. Starting in 5 seconds...")
    
    # === Clear command.txt ===
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        command_file = os.path.join(base_path, "command.txt")
        with open(command_file, "w") as f:
            f.write("")
        print("✅ Cleared command.txt")
    except Exception as e:
        print(f"❌ Failed to clear command.txt: {e}")

    # === Launch AHK .exe ===
    try:
        ahk_exe_path = os.path.join(base_path, "mobilelegends_ai.exe")
        subprocess.Popen([ahk_exe_path])
        print("✅ Started mobilelegends_ai.exe")
    except Exception as e:
        print(f"❌ Failed to launch mobilelegends_ai.exe: {e}")
    time.sleep(5)

    with mss.mss() as sct:
        while True:
            screenshot = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            hp_ratio = get_hp_ratio(frame, hp_top, hp_bottom, hp_left, hp_right)
            decide_movement(hp_ratio)

            current_time = time.time()
            if current_time - last_skill_time >= 1.0:
                send_command("spam_skills")
                last_skill_time = current_time

            time.sleep(0.2)  # adjust as needed for responsiveness

if __name__ == "__main__":
    main()
