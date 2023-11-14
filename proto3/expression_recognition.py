import cv2
from deepface import DeepFace

# Initialize the camera
cap = cv2.VideoCapture(0) # 0 is typically the default camera

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
            result = DeepFace.analyze(frame, actions=['emotion'])
            print("DeepFace Result:", result)  # Print the entire result

            # Assuming the result is a dictionary and contains 'emotion'
            if 'emotion' in result:
                emotion = max(result['emotion'], key=result['emotion'].get)  # Get the dominant emotion
                print("Emotion:", emotion)  # Print detected emotion

                # Displaying the result
                cv2.putText(frame, emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_4)
            else:
                print("No emotion data in result")
        except Exception as e:
            print("DeepFace Error:", e)
            continue  # Skip to the next frame

    # Display the frame
    cv2.imshow('Camera Feed', frame)

    # Break the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close any open windows
cap.release()
cv2.destroyAllWindows()
