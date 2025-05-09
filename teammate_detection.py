import time
import cv2
import mss
import numpy as np

def get_hsv_mask(image_bgr, lower_bound, upper_bound):
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    return mask

import cv2
import numpy as np

def detect_self_on_minimap(minimap_bgr, debug=False):
    lower_green = np.array([50, 100, 100])
    upper_green = np.array([70, 255, 255])
    hsv = cv2.cvtColor(minimap_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_match = None
    lowest_solidity = 1.0  # looking for hollow rings

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 10 or area > 300:
            continue

        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            continue

        solidity = area / hull_area
        if solidity < lowest_solidity and solidity < 0.85:
            # Fit enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            ring_center = np.array([x, y])

            # Get bounding box center (estimates icon face center)
            x_, y_, w, h = cv2.boundingRect(cnt)
            bbox_center = np.array([x_ + w / 2, y_ + h / 2])

            # Shift toward face center
            direction = bbox_center - ring_center
            adjusted_center = ring_center + 0.25 * direction
            cx, cy = tuple(map(int, adjusted_center))

            best_match = (cx, cy)
            lowest_solidity = solidity

            # Optional debug drawing
            if debug:
                cv2.circle(minimap_bgr, (int(x), int(y)), 2, (0, 255, 255), -1)  # raw ring center
                cv2.circle(minimap_bgr, best_match, 2, (0, 255, 0), -1)          # adjusted center
                cv2.rectangle(minimap_bgr, (x_, y_), (x_ + w, y_ + h), (255, 255, 0), 1)  # bounding box

    return best_match


# def detect_self_on_minimap(minimap_bgr):
#     lower_green = np.array([50, 100, 100])
#     upper_green = np.array([70, 255, 255])
#     hsv = cv2.cvtColor(minimap_bgr, cv2.COLOR_BGR2HSV)
#     mask = cv2.inRange(hsv, lower_green, upper_green)

#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#     best_match = None
#     lowest_solidity = 1.0  # lower = better (less filled)

#     for cnt in contours:
#         area = cv2.contourArea(cnt)
#         if area < 20 or area > 300:
#             continue

#         hull = cv2.convexHull(cnt)
#         hull_area = cv2.contourArea(hull)
#         if hull_area == 0:
#             continue

#         solidity = area / hull_area

#         # Look for contours that are less filled (like a ring)
#         if solidity < lowest_solidity and solidity < 0.85:
#             (x, y), radius = cv2.minEnclosingCircle(cnt)
#             # Raw center (yellow)
#             cv2.circle(minimap_bgr, (int(x), int(y)), 3, (0, 255, 255), -1)
#             #best_match = (int(x), int(y))

#             # Shift toward center by 20% of radius
#             ring_center = np.array([x, y])
#             minimap_center = np.array([mask.shape[1] // 2, mask.shape[0] // 2])
#             center_direction = ring_center - minimap_center
#             center_direction = center_direction / (np.linalg.norm(center_direction) + 1e-5)
#             adjusted_center = ring_center - 0.2 * radius * center_direction
#             cx, cy = tuple(map(int, adjusted_center))
#             cv2.circle(minimap_bgr, (cx, cy), 3, (0, 255, 0), -1)

#             best_match = (cx, cy)
#             lowest_solidity = solidity

#     return best_match



def detect_allied_heroes(minimap_bgr, debug=False):
    lower_blue = np.array([90, 100, 100])
    upper_blue = np.array([130, 255, 255])
    hsv = cv2.cvtColor(minimap_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    teammates = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 10 or area > 300:
            continue

        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            continue
        solidity = area / hull_area
        if solidity > 0.85:
            continue  # likely filled — not a ring

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue
        circularity = 4 * np.pi * area / (perimeter ** 2)

        if circularity < 0.2 or circularity > 0.85:
            continue

        (x, y), radius = cv2.minEnclosingCircle(cnt)
        cx, cy = int(x), int(y)
        hp_ratio = min(max(circularity, 0), 1.0)

        teammates.append((cx, cy, hp_ratio))

        if debug:
            cv2.circle(minimap_bgr, (cx, cy), 5, (255, 0, 0), 1)
            cv2.putText(minimap_bgr, f"{int(hp_ratio*100)}%", (cx + 5, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    return teammates



def detect_allied_turrets(minimap_bgr):
    lower_blue = np.array([90, 100, 100])
    upper_blue = np.array([130, 255, 255])
    mask = get_hsv_mask(minimap_bgr, lower_blue, upper_blue)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    turrets = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 300 < area < 1000:
            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter != 0 else 0
            if circularity < 0.5:  # generally more filled shapes
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    turrets.append((cx, cy))

    return turrets


def draw_minimap_debug(minimap_bgr, self_pos, heroes, turrets):
    debug_img = minimap_bgr.copy()

    # Draw self
    if self_pos:
        cv2.circle(debug_img, self_pos, 6, (0, 255, 0), 2)
        cv2.putText(debug_img, "YOU", (self_pos[0]+5, self_pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    # Draw teammates
    for (x, y, hp) in heroes:
        cv2.circle(debug_img, (x, y), 5, (255, 0, 0), 1)
        cv2.putText(debug_img, f"{int(hp*100)}%", (x+6, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # Draw turrets
    for (x, y) in turrets:
        cv2.rectangle(debug_img, (x-6, y-6), (x+6, y+6), (255, 255, 0), 1)
        cv2.putText(debug_img, "T", (x-4, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)

    return debug_img

def main():
    print("⏳ Waiting 3 seconds... switch to game window.")
    time.sleep(3)

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    # Crop the minimap
    minimap = frame[0:341, 0:338]

    # Detect self (green ring)
    self_pos = detect_self_on_minimap(minimap, debug=True)
    teammates = detect_allied_heroes(minimap, debug=True)

    # Draw the result
    debug_img = minimap.copy()
    if self_pos:
        cv2.circle(debug_img, self_pos, 6, (0, 255, 0), 2)
        cv2.putText(debug_img, "YOU", (self_pos[0]+5, self_pos[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    else:
        print("❌ Could not detect self on minimap.")

    # Draw teammates
    for i, (x, y, hp_ratio) in enumerate(teammates):
        cv2.circle(debug_img, (x, y), 5, (255, 0, 0), 1)
        cv2.putText(debug_img, f"teammate {i}:{int(hp_ratio * 100)}%", (x+6, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)


    # Show result
    cv2.imshow("Minimap - Self and Teammates", debug_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
