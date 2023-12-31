from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import requests

currentname = "unknown"
encodingsP = "encodings.pickle"
cascade = "haarcascade_frontalface_default.xml"

def send_message(name):
    return requests.post(
        "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages",
        auth=("api", "YOUR_API_KEY"),
        files = [("attachment", ("image.jpg", open("image.jpg", "rb").read()))],
        data={"from": 'suryagowda000143@gmail.com',
            "to": ["YOUR_MAILGUN_EMAIL_ADDRESS"],
            "subject": "A Child is detected",
            "html": "<html>" + name + " is found.  </html>"})

print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

fps = FPS().start()

while True:
	frame = vs.read()
	frame = imutils.resize(frame, width=500)
	
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30),
		flags=cv2.CASCADE_SCALE_IMAGE)

	boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	for encoding in encodings:
		matches = face_recognition.compare_faces(data["encodings"],
			encoding)
		name = "Unknown"

		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			name = max(counts, key=counts.get)
			
			if currentname != name:
				currentname = name
				print(currentname)
				img_name = "image.jpg"
				cv2.imwrite(img_name, frame)
				print('Taking a picture.')
				
				request = send_message(name)
				print ('Status Code: '+format(request.status_code)) #200 status code means email sent successfully
				
		names.append(name)

	for ((top, right, bottom, left), name) in zip(boxes, names):
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 225), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
			.8, (0, 255, 255), 2)

	cv2.imshow("Facial Recognition is Running", frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

	fps.update()

fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()
