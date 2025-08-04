import cv2
import numpy as np
import os
import sys
import queryDB as db

# Nhận thông tin khách hàng từ tham số dòng lệnh
if len(sys.argv) < 3:
    print("⚠️ LỖI: Thiếu thông tin khách hàng! Cần nhập số điện thoại & tên.")
    sys.exit(1)

id = sys.argv[1]  # Số điện thoại làm ID
name = sys.argv[2]

# Lưu khách hàng vào DB nếu chưa có
if not db.insertOrUpdate(id, name):
    print(f"⚠️ Không thể lưu khách hàng {name} vào DB!")
    sys.exit(1)

# Khởi tạo webcam
cam = cv2.VideoCapture(0,cv2.CAP_V4L2)
if not cam.isOpened():
    print("🚨 Không thể mở camera! Kiểm tra thiết bị.")
    sys.exit(1)

cam.set(3, 1280)
cam.set(4, 720)

# Bộ nhận diện khuôn mặt
detector = cv2.CascadeClassifier("./libs/haarcascade_frontalface_default.xml")

sampleNum = 0
max_samples = 30   # Giảm số lượng ảnh thu thập để nhanh hơn
dataset_path = "dataset"  # Sửa lại để đồng bộ với `traningData.py`

if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

print(f"📸 Đang thu thập dữ liệu cho {name}...")

while True:
    ret, img = cam.read()
    if not ret:
        print("🚨 LỖI: Không thể đọc từ camera!")
        break
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

        sampleNum += 1
        filename = f"{dataset_path}/User.{id}.{sampleNum}.jpg"
        cv2.imwrite(filename, gray[y:y+h, x:x+w])

        print(f"📸 Đã lưu: {filename} ({sampleNum}/{max_samples})")
        cv2.imshow('frame', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif sampleNum >= max_samples:
        break

cam.release()
cv2.destroyAllWindows()

if sampleNum > 0:
    print(f"✅ Dữ liệu hình ảnh của {name} đã được thu thập thành công!")
else:
    print("⚠️ Không có ảnh nào được lưu! Kiểm tra camera.")

