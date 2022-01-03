import os
from tkinter import filedialog

import cv2 as cv
import time
import imutils
from imutils.video import VideoStream
import tkinter as tk
from tkinter import *

# List of available trackers from OpenCV
list_of_trackers = {
    "csrt": cv.TrackerCSRT_create,
    "kcf": cv.TrackerKCF_create,
    "boosting": cv.TrackerBoosting_create,
    "mil": cv.TrackerMIL_create,
    "tld": cv.TrackerTLD_create,
    "medianflow": cv.TrackerMedianFlow_create,
    "mosse": cv.TrackerMOSSE_create
}

window = tk.Tk()
window.title('Setup')
window.geometry("800x350")
filepath = 'C:/'
trackerType = StringVar(window, "csrt")
isTrail = BooleanVar()
isStream = BooleanVar()


def open_file():
   file = filedialog.askopenfile(mode='r', filetypes=[('Video files', '*.*')])
   if file:
      filepath = os.path.abspath(file.name)
      Label(window, text="File path: " + str(filepath), font=('Aerial 11')).place(x = 5, y = 175)


def setup_gui():
    label_tracker = tk.Label(text='Select tracker type:')
    label_tracker.place(x=5, y=10)
    tracker_select = OptionMenu(window, trackerType, *list_of_trackers)
    tracker_select.place(x=200, y=5)

    label_options = tk.Label(text='Other options:')
    label_options.place(x=5, y=50)
    is_trail_checkbox = Checkbutton(window, text="Trail", variable=isTrail)
    is_stream_checkbox = Checkbutton(window, text="Camera Stream", variable=isStream)
    is_trail_checkbox.place(x=200, y=50)
    is_stream_checkbox.place(x=200, y=75)

    label_browse = tk.Label(text='Optionally browse video file:')
    label_browse.place(x=5, y=125)
    tk.Button(window, text="Browse", command=open_file).place(x=200, y=125)
    label_warning = tk.Label(text='Video playback from file works only when "Camera Stream" option is unchecked.')
    label_warning.place(x=5, y=225)

    close_button = Button(window, text="Proceed", command=window.destroy)
    close_button.place(x=375, y=300)
    window.mainloop()


def main():
    # Start setup
    setup_gui()

    # Init tracker
    tracker = list_of_trackers[trackerType.get()]()

    # Init bounding box and FPS
    bounding_box = None

    # Init object trail tracking
    if isTrail:
        point_history = []

    # Get reference to the webcam and start streaming
    if isStream.get():
        vs = VideoStream(src=0).start()
        time.sleep(1.0)

    # Or get reference to video file
    else:
        vs = cv.VideoCapture(filepath)

    loop_over_frames = True

    while loop_over_frames:
        # Get next frame from video
        frame = vs.read()
        frame = frame[1] if not isStream.get() else frame

        # If video is over, break the loop
        if frame is None:
            loop_over_frames = False

        # Resize frame in order to process it faster, then save current frame dimensions
        frame = imutils.resize(frame, width=500)
        (H, W) = frame.shape[:2]

        if bounding_box is not None:
            # Get bounding box f item is selected
            (success, box) = tracker.update(frame)

            if success:
                # Save bounding box dimensions
                (x, y, w, h) = [int(v) for v in box]

                # Mark current bounding box on the frame
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # Draw the trail
                if isTrail:
                  
                    # Save current location
                    point_history.append((x + (w // 2), y + (h // 2)))

                    # We need to draw the full history each frame
                    try:
                        idx = 0
                        while True:
                            cv.line(frame, point_history[idx], point_history[idx + 1], (255, 0, 0), 2)
                            idx += 1
                    except IndexError:
                        pass
        
                    # Remove the oldest element after x frames to avoid cluttering the display
                    # Could be optimized later if necessary - maybe use a linked list?
                    # + track len as var
                    if len(point_history) > 100:
                        point_history.pop(0)

            # Define information to display on frame
            info_top = [f'Tracker: {trackerType.get()}']
            info_bottom = ["Press N if you want to select new object.", "Press Q if you want to quit."]

            i = 1
            for text in info_top:
                cv.putText(frame, text, (5, H - (i * 20) + 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                i += 1

            i = 1
            for item in info_bottom:
                cv.putText(frame, item, (5, H - (H - (i * 20))), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                i += 1

        elif bounding_box is None:
            # Define information to display on frame
            info = ["Press S if you want to select bounding box.", "Press Q if you want to quit."]

            i = 1
            for item in info:
                cv.putText(frame, item, (5, H - (H - (i * 20))), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                i += 1

            # Clear point history when no object is being tracked
            if isTrail:
                point_history = []

        # Show current output frame
        cv.imshow("Frame", frame)

        # Get key deciding on further action
        key = cv.waitKey(1) & 0xFF

        # Key "S" means defining new bounding box
        if key == ord("s"):
            # Define information to display on frame
            info = "Press ENTER if you want to confirm BB."
            cv.putText(frame, info, (5, H - (H - (3 * 20))), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Select object on current frame
            bounding_box = cv.selectROI("Frame", frame, fromCenter=False, showCrosshair=True)

            # Init object tracker using selected bounding box coordinates
            tracker.init(frame, bounding_box)

        # Key "N" enables a new bounding box selection
        elif key == ord("n"):
            # Reset critical variables
            bounding_box = None
            tracker = list_of_trackers[trackerType.get()]()
            if isTrail:
                point_history = []

        # Key "Q" ends running the program
        elif key == ord("q"):
            loop_over_frames = False

    # Release webcam pointer
    if isStream.get():
        vs.stop()
    # Release file pointer
    else:
        vs.release()

    # Destroy windows
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()