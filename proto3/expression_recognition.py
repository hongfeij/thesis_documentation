import cv2
from deepface import DeepFace

# Initialize the camera
cap = cv2.VideoCapture(0) # 0 is typically the default camera

while True:
    ret, frame = cap.read() # Capture frame-by-frame
    if ret:
        try:
            # Analyzing the facial expression
            result = DeepFace.analyze(frame, actions=['emotion'])

            # Displaying the result
            emotion = result["dominant_emotion"]
            cv2.putText(frame, emotion, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_4)
            cv2.imshow('Frame', frame)

        except Exception as e:
            print("Error:", e)
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cap.release()
cv2.destroyAllWindows()
