import os
import time
import random
import cv2
import numpy as np
import pyautogui
import keyboard


TARGET_FOLDER = "targets"

CONFIDENCE = 0.7

# Timing jitter
CLICK_DELAY_MIN = 0.5
CLICK_DELAY_MAX = 1.5

# Random mouse offset
CLICK_OFFSET = 3


# -----------------------------
# Select ROI
# -----------------------------

def select_roi():

    screenshot = pyautogui.screenshot()

    screen = cv2.cvtColor(
        np.array(screenshot),
        cv2.COLOR_RGB2BGR
    )

    print("Select scanning area, then press ENTER")

    roi = cv2.selectROI(
        "Select ROI",
        screen,
        showCrosshair=True
    )

    cv2.destroyWindow("Select ROI")

    x, y, w, h = roi

    if w == 0 or h == 0:
        raise Exception("No ROI selected")

    return x, y, w, h


ROI_X, ROI_Y, ROI_W, ROI_H = select_roi()

print(
    f"Scanning region: "
    f"{ROI_X},{ROI_Y} "
    f"{ROI_W}x{ROI_H}"
)


# -----------------------------
# Load targets
# -----------------------------

targets = []

for filename in sorted(os.listdir(TARGET_FOLDER)):

    if filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):

        path = os.path.join(
            TARGET_FOLDER,
            filename
        )

        img = cv2.imread(
            path,
            cv2.IMREAD_GRAYSCALE
        )

        if img is not None:

            targets.append({
                "name": filename,
                "image": img
            })


print("\nPriority order:")

for t in targets:
    print(t["name"])



# -----------------------------
# Image detection
# -----------------------------

def find_image(target):

    screenshot = pyautogui.screenshot(
        region=(
            ROI_X,
            ROI_Y,
            ROI_W,
            ROI_H
        )
    )

    screenshot = cv2.cvtColor(
        np.array(screenshot),
        cv2.COLOR_RGB2GRAY
    )


    result = cv2.matchTemplate(
        screenshot,
        target["image"],
        cv2.TM_CCOEFF_NORMED
    )


    locations = np.where(
        result >= CONFIDENCE
    )


    if len(locations[0]):

        y, x = (
            locations[0][0],
            locations[1][0]
        )

        h, w = target["image"].shape

        # Convert ROI coordinates back to screen
        center_x = (
            ROI_X +
            x +
            w // 2
        )

        center_y = (
            ROI_Y +
            y +
            h // 2
        )

        return center_x, center_y


    return None



# -----------------------------
# Jitter click
# -----------------------------

def jitter_click(x, y):

    # random delay before click
    time.sleep(
        random.uniform(
            CLICK_DELAY_MIN,
            CLICK_DELAY_MAX
        )
    )


    x += random.randint(
        -CLICK_OFFSET,
        CLICK_OFFSET
    )

    y += random.randint(
        -CLICK_OFFSET,
        CLICK_OFFSET
    )


    pyautogui.click(
        x,
        y
    )


    # random delay after click
    time.sleep(
        random.uniform(
            CLICK_DELAY_MIN,
            CLICK_DELAY_MAX
        )
    )



# -----------------------------
# Main loop
# -----------------------------

print("\nRunning")
print("Press ESC to stop")


while not keyboard.is_pressed("esc"):

    clicked = False


    # filename priority order
    for target in targets:

        pos = find_image(target)

        if pos:

            print(
                "Found:",
                target["name"]
            )

            jitter_click(
                pos[0],
                pos[1]
            )

            clicked = True
            break


    if not clicked:
        time.sleep(0.05)


print("Stopped")
