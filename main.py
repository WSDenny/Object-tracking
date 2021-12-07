import cv2 as cv
import argparse
import time
import imutils
from imutils.video import VideoStream


def main():
    # Arguments from console, later can be switched to getting arguments from GUI
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", type=str, help="Path to input video file (optional)")
    ap.add_argument("-t", "--tracker", type=str, default="boosting", help="OpenCV object tracker type")
    ap.add_argument("--trail", action="store_true", help="Display movement history on screen")
    args = vars(ap.parse_args())

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

    # Init tracker
    tracker = list_of_trackers[args["tracker"]]()

    # Init bounding box and FPS
    bounding_box = None

    # Init object trail tracking
    trail = args["trail"]
    if trail:
        point_history = []

    # Get reference to the webcam and start streaming
    if not args.get("video", False):
        vs = VideoStream(src=0).start()
        time.sleep(1.0)

    # Or get reference to video file
    else:
        vs = cv.VideoCapture(args["video"])

    loop_over_frames = True

    while loop_over_frames:
        # Get next frame from video
        frame = vs.read()
        frame = frame[1] if args.get("video", False) else frame

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
                if trail:
                    # Save current location
                    point_history.append((x + (w // 2), y + (h // 2)))

                    # We need to draw the full history each frame
                    try:
                        idx = 0
                        while True:
                            cv.line(frame, point_history[idx], point_history[idx+1], (255, 0, 0), 2)
                            idx += 1
                    except IndexError:
                        pass
                    
                    # Remove the oldest element after x frames to avoid cluttering the display
                    # Could be optimized later if necessary - maybe use a linked list?
                    # + track len as var
                    if len(point_history) > 100:
                        point_history.pop(0)

            # Define information to display on frame
            info_top = [f'Tracker: {args["tracker"]}']
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
            if trail:
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
            tracker = list_of_trackers[args["tracker"]]()
            if trail:
                point_history = []

        # Key "Q" ends running the program
        elif key == ord("q"):
            loop_over_frames = False

    # Release webcam pointer
    if not args.get("video", False):
        vs.stop()
    # Release file pointer
    else:
        vs.release()

    # Destroy windows
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()

