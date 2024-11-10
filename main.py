import os
import time
import threading
import numpy as np
from pynput.mouse import Button as pyB, Controller
from pynput.keyboard import Listener, KeyCode
import cv2
import pyautogui

# Define keys and button variables
buttonLeftClick = pyB.left
start_stop_key = '='
exit_key = KeyCode(char='+')
kill_key = KeyCode(char='-')

# Initialize mouse and keyboard controllers
mouse = Controller()

# Load the target image for detection
target_image_path = 'images/minow.png'  # Path to the target image in your directory
target_image = cv2.imread(target_image_path, cv2.IMREAD_GRAYSCALE)
w, h = target_image.shape[::-1]  # Get dimensions of the template image

# Define the minimum y-coordinate threshold for valid matches
y_min = 330  # Only click if y-coordinate is >= 330


# ClickMouse class to handle clicking logic
class ClickMouse(threading.Thread):
    def __init__(self, button):
        super(ClickMouse, self).__init__()
        self.button = button
        self.running = False
        self.program_running = True
        print("Program initialized")

    def start_clicking(self):
        self.running = True
        print("Started Clicking")

    def stop_clicking(self):
        self.running = False
        print("Stopped Clicking")

    def kill_clicking(self):
        print("Killed Clicking")
        os._exit(1)

    def exit(self):
        self.stop_clicking()
        self.program_running = False
        print("Exiting program")

    def find_and_click_image(self):
        # Take a screenshot and convert it to grayscale
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(screenshot, target_image, cv2.TM_CCOEFF_NORMED)

        threshold = 0.8  # Threshold for template matching
        locations = np.where(result >= threshold)

        # Print the number of occurrences found
        print(f"Occurrences found: {len(locations[0])}")

        match_centers = []
        for y, x in zip(*locations):
            match_center = (x + w // 2, y + h // 2)

            # Only allow clicks if the y-coordinate is at or below the threshold
            if match_center[1] >= y_min:
                match_centers.append(match_center)

        # Print valid match centers
        if match_centers:
            print(f"Valid matches found at: {match_centers}")

            # Select the first valid match
            closest_match = match_centers[0]
            print(f"Current mouse position: {mouse.position}")  # Print current mouse position

            # Move the mouse to the closest match and click
            mouse.position = closest_match
            time.sleep(returnFloat(0.6, 0.8))  # Random delay before click
            mouse.click(self.button)
            print(f"Clicked on the target image at {closest_match}")
        else:
            print("No valid matches found within the Y-coordinate restriction.")

    def run(self):
        print("Thread running")
        while self.program_running:
            if self.running:
                print("Looking for image to click...")
                self.find_and_click_image()
                # Small delay to reduce system load and allow responsiveness to stop
                time.sleep(returnFloat(5, 7))
            else:
                # Short sleep when not running to avoid CPU overload
                time.sleep(0.1)


# Instantiate ClickMouse thread
click_thread = ClickMouse(buttonLeftClick)
click_thread.start()


def returnInt(minInt, maxInt):
    num = np.random.randint(minInt, maxInt)
    print(num)
    return num


def returnFloat(minInt, maxInt):
    num = np.random.uniform(minInt, maxInt)
    print(num)
    return num


# Keyboard control functions
def on_press(key):
    try:
        print(f"Key pressed: {key} | Key char: {key.char}")
        if key.char == start_stop_key:
            print("Toggling clicking")
            if click_thread.running:
                click_thread.stop_clicking()
            else:
                click_thread.start_clicking()
        elif key == exit_key:
            click_thread.exit()
            listener.stop()
        elif key == kill_key:
            click_thread.kill_clicking()
            listener.stop()
    except AttributeError:
        print(f"Non-character key pressed: {key}")


# Start keyboard listener
with Listener(on_press=on_press) as listener:
    listener.join()
