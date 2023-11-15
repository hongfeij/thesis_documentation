import time
import cv2
from deepface import DeepFace
import json
import threading

# Initialize a lock for file writing
file_lock = threading.Lock()

# Initialize the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera not accessible")
    exit()

frame_count = 0
n_frame_process = 5  # Process every 5th frame

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame (stream end?). Exiting ...")
        break

    frame_count += 1
    if frame_count % n_frame_process == 0:
        try:
            # Analyzing the facial expression
            results = DeepFace.analyze(frame, actions=['emotion'])

            # Check if results is a list and has at least one element
            if isinstance(results, list) and len(results) > 0:
                first_result = results[0]
                emotion_data = first_result.get('emotion', {})
                dominant_emotion = first_result.get('dominant_emotion', '')

                # Writing to file
                with file_lock:
                    with open("emotion_data.json", "w") as file:
                        data_to_write = {
                            "timestamp": time.time(),
                            "emotion_data": emotion_data
                        }
                        json.dump(data_to_write, file)

                if dominant_emotion:
                    cv2.putText(frame, dominant_emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_4)
            else:
                print("No valid results from DeepFace")

        except Exception as e:
            print("Error occurred during DeepFace analysis:", e)

    cv2.imshow('Camera Feed', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
