import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
from plyer import notification
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
from sklearn import neighbors
import pickle
from dotenv import load_dotenv


load_dotenv()


path = r"C:\Users\rasin\OneDrive\Documents\Custom Office Templates\Desktop\EEN\Face-Recognition-Attendance-Projects-main\Training_images"
attendance_path = r"C:\Users\rasin\OneDrive\Documents\Custom Office Templates\Desktop\EEN\Face-Recognition-Attendance-Projects-main\Attendance.csv"


EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))

name_to_email = {
    '568': 'sravyaa43@gmail.com',
    '573': 'meghanabolleddu20@gmail.com',
    '592': 'kammadanamshirisha7@gmail.com',
    '595': 'lavudivenusri004@gmail.com',
    '5A1': 'vineelareddymandadi1922@gmail.com',
    '5A4': 'n.vijaysimhareddy123@gmail.com',
    '5A6': 'susannajoyce21@gmail.com',
    '5A9': 'prashanthpotta722@gmail.com',
    '5B4': 'rasinenicharishma22@gmail.com',
    '5C0': 'srikeshshekapuram0711@gmail.com',
    '5C6': 'vallakatlachaitanya2003@gmail.com',
    '5C8': 'rishithaveeramalla18731@gmail.com',
    'Deepika Mam': 'deepikarani543@gmail.com',
    
    
}


images = []
classNames = []
myList = os.listdir(path)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    if curImg is None:
        print(f"Warning: Image {cl} could not be read.")
        continue
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

def findEncodings(images, classNames):
    encodeList = []
    validClassNames = []
    for img, name in zip(images, classNames):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img)
        if encodes:
            encodeList.append(encodes[0])
            validClassNames.append(name)
        else:
            print(f"No faces found in the image {name}.")
    return encodeList, validClassNames

def markAttendance(name):
    attendance_file_exists = os.path.isfile(attendance_path)
    with open(attendance_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not attendance_file_exists:
            writer.writerow(['Name', 'Date', 'Time'])
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        writer.writerow([name, date_str, time_str])
        send_notification(name, f'{date_str} {time_str}')

def send_notification(name, timestamp):
    notification.notify(
        title='Attendance Notification',
        message=f'{name} marked present at {timestamp}',
        timeout=10
    )

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"Connecting to SMTP server: {SMTP_SERVER} on port: {SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print(f"Logging in as: {EMAIL_ADDRESS}")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = msg.as_string()
            print(f"Sending email to: {to_email}")
            server.sendmail(EMAIL_ADDRESS, to_email, text)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_absentees(validClassNames, detected_names):
    for name in validClassNames:
        if name.upper() not in detected_names:
            send_absent_notification(name)

def send_absent_notification(name):
    if name in name_to_email:
        to_email = name_to_email[name]
        subject = 'Attendance Alert'
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        body = f'{name} is marked absent at {timestamp}'
        send_email(to_email, subject, body)
    else:
        print(f"No email address found for {name}")


encodeListKnown, validClassNames = findEncodings(images, classNames)
knn_clf = neighbors.KNeighborsClassifier(n_neighbors=2, algorithm='ball_tree', weights='distance')
knn_clf.fit(encodeListKnown, validClassNames)

cap = cv2.VideoCapture(0)

start_time = datetime.now()

detected_names = set()


font = cv2.FONT_HERSHEY_DUPLEX
font_scale = 1
font_color = (0, 0, 0)  # Black color for the text
font_thickness = 2
rect_color = (173, 216, 230)  # Light blue color for the rectangle


attendance_intervals = [1, 5, 15, 30, 45]
next_attendance_times = [start_time + timedelta(minutes=interval) for interval in attendance_intervals]

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        closest_distances = knn_clf.kneighbors([encodeFace], n_neighbors=1)
        match = closest_distances[0][0] <= 0.6

        if match:
            name = knn_clf.predict([encodeFace])[0].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), rect_color, 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), rect_color, cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), font, font_scale, font_color, font_thickness)
        
            detected_names.add(name)
 
            detected_names.add(name)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    current_time = datetime.now()
    if next_attendance_times and current_time >= next_attendance_times[0]:
        for name in detected_names:
            markAttendance(name)
        check_absentees(validClassNames, detected_names)  # Check for absentees and send notifications
        detected_names.clear()
        next_attendance_times.pop(0)
        
        if not next_attendance_times:
            next_attendance_times = [current_time + timedelta(minutes=interval) for interval in attendance_intervals]

cap.release()
cv2.destroyAllWindows()

# Separate test script to test email sending functionality
def send_test_email():
    to_email = "vineelareddymandadi1922@gmail.com"
    subject = "Test Email"
    body = "This is a test email to verify the email sending functionality."

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        print(f"Connecting to SMTP server: {SMTP_SERVER} on port: {SMTP_PORT}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            print(f"Logging in as: {EMAIL_ADDRESS}")
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = msg.as_string()
            print(f"Sending email to: {to_email}")
            server.sendmail(EMAIL_ADDRESS, to_email, text)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

send_test_email()
