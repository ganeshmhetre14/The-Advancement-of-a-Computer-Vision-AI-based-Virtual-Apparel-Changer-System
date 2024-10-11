import os
import cv2
from cvzone.PoseModule import PoseDetector
import cvzone
import tkinter as tk
from tkinter import ttk, messagebox

# Initialize webcam capture
cap = cv2.VideoCapture(0)

# Initialize PoseDetector
detector = PoseDetector()

# Constants and variables
fixedRatio = 262 / 190  # widthOfShirt/widthOfPoint11to12
shirtRatioHeightWidth = 581 / 440
imageNumber = 0

# Function to handle selection of gender
def select_gender():
    global shirtFolderPath
    gender = var.get()
    if gender == "Male":
        shirtFolderPath = os.path.join("Gender", "Men")
    elif gender == "Female":
        shirtFolderPath = os.path.join("Gender", "Women")
    else:
        messagebox.showerror("Error", "Please select a gender.")
        return
    root.destroy()

# Create Tkinter GUI window
root = tk.Tk()
root.title("T-Shirt Selection")
root.geometry("300x150")
root.configure(bg="#f0f0f0")

# Create radio buttons for gender selection
var = tk.StringVar()
var.set(None)  # Initially no selection
style = ttk.Style()
style.configure("TRadiobutton", background="#f0f0f0", foreground="#333", font=("Helvetica", 14))

frame = ttk.Frame(root, padding="10")
frame.pack()

label = ttk.Label(frame, text="Select Gender", font=("Helvetica", 16))
label.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

rb_male = ttk.Radiobutton(frame, text="Male", variable=var, value="Male")
rb_male.grid(row=1, column=0, padx=5, pady=5)

rb_female = ttk.Radiobutton(frame, text="Female", variable=var, value="Female")
rb_female.grid(row=1, column=1, padx=5, pady=5)

# Button to confirm selection
btn_confirm = ttk.Button(root, text="Confirm", command=select_gender)
btn_confirm.pack(pady=10)

# Label for message
message_label = tk.Label(root, text="Move Right or Left to change T-shirt", font=("Helvetica", 12), fg="#210386")
message_label.pack()

# Display GUI and wait for user input
root.mainloop()

# Set the size of the output window
cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Folder containing shirt images
script_dir = os.path.dirname(__file__)
gender_folder = os.path.join(script_dir, "Gender")
listShirts = os.listdir(shirtFolderPath)

# Define variables for hand positions
prev_lm11 = [0, 0]

while True:
    success, img = cap.read()
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

    if lmList:
        lm11 = lmList[11][1:3]
        lm12 = lmList[12][1:3]
        imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[imageNumber]), cv2.IMREAD_UNCHANGED)

        widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)
        if widthOfShirt > 0:  # Add validity check
            imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))
            currentScale = (lm11[0] - lm12[0]) / 190
            offset = int(44 * currentScale), int(48 * currentScale)

            try:
                img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            except Exception as e:
                print("Error:", e)
        else:
            print("Invalid shirt width")

        # Check hand movement direction
        if prev_lm11[0] != 0:
            if lm11[0] > prev_lm11[0] + 20:  # Move hand to the right
                # Increment image number to change T-shirt
                if imageNumber < len(listShirts) - 1:
                    imageNumber += 1
            elif lm11[0] < prev_lm11[0] - 20:  # Move hand to the left
                # Decrement image number to change T-shirt
                if imageNumber > 0:
                    imageNumber -= 1

        prev_lm11 = lm11

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('q'):  # Quit if 'q' is pressed
        break

# Release the capture and close all windows
cap.release()
cv2.destroyAllWindows()
