# import cv2
# import numpy as np
# import queryDB as db
# import time
# import os

# cam = cv2.VideoCapture(0)
# cam.set(3, 732)
# cam.set(4, 720)

# face_cascade = cv2.CascadeClassifier("libs/haarcascade_frontalface_default.xml")
# recognizer = cv2.face.LBPHFaceRecognizer_create()
# recognizer.read('recognizer/trainningData.yml')

# fontface = cv2.FONT_HERSHEY_SIMPLEX

# while True:
#     ret, frame = cam.read()

#     if not ret:
#         print("Không thể lấy khung hình từ webcam.")
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = face_cascade.detectMultiScale(gray)

#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 
import cv2
import numpy as np
import queryDB as db
import time
import os

# Khởi tạo webcam và đặt độ phân giải của nó
cam = cv2.VideoCapture(0,cv2.CAP_V4L2)
cam.set(3, 732)  # Kích thước chiều rộng
cam.set(4, 720)  # Kích thước chiều cao

# Khởi tạo một đối tượng CascadeClassifier trong thư viện OpenCV với tệp tin XML chứa thông tin về mô hình Cascade để phát hiện khuôn mặt trên hình ảnh đầu vào
face_cascade = cv2.CascadeClassifier("libs/haarcascade_frontalface_default.xml")

# Tạo ra một đối tượng nhận dạng khuôn mặt bằng thuật toán LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('recognizer/trainningData.yml')

fontface = cv2.FONT_HERSHEY_SIMPLEX

# Thư mục hình ảnh thông báo check-in thành công
img_checkout = cv2.imread('image/checkOut.png')  # Hình ảnh thông báo check-in thành công

# Vòng lặp vô hạn để lấy liên tục hình ảnh từ camera.
while True:
    ret, frame = cam.read()

    if not ret:  # Kiểm tra nếu không lấy được khung hình
        print("Không thể lấy khung hình từ webcam.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray)

    if len(faces) > 0:
        for (x, y, w, h) in faces:
            # Vẽ khung bao quanh khuôn mặt
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Cắt khuôn mặt ra khỏi ảnh và chuyển đổi thành ảnh xám để nhận diện
            roi_gray = gray[y:y + h, x:x + w]
            id, confidence = recognizer.predict(roi_gray)

            # Nếu nhận diện thành công (confidence thấp hơn 40)
            if confidence < 40:
                profile = db.getProfile(id)
                print(profile)
                if profile != None:
                    # Hiển thị tên người nhận diện
                    cv2.putText(frame, f"{str(profile[1])} {db.get_level(profile[2])}", (x + 10, y + h + 30), fontface, 1, (0, 255, 0), 2)

                    # Chờ 2 giây để xác nhận đã nhận diện thành công
                    current_time = time.time()
                    while time.time() - current_time < 3:  # Chờ 2 giây
                        cv2.imshow("nhan dien", frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                    # Kiểm tra người đã tồn qtại trong cơ sở dữ liệu
                    check = db.insertOrUpdate(profile[0], profile[1]) 
                    print(check)
                    if check:
                        height, width = frame.shape[:2]
                        img_checkout_resized = cv2.resize( frame, (width, height))
 
                    # Chèn hình ảnh check-in vào webcam
                        img_with_checkout = frame.copy()  # Tạo bản sao của frame gốc
                        img_with_checkout[0:img_checkout_resized.shape[0], 0:img_checkout_resized.shape[1]] = img_checkout_resized  # Chèn hình ảnh check-in vào webcam

                    # Hiển thị thông báo trong 5 giây
                        cv2.imshow("Check-in Thanh Cong", img_with_checkout)
                        cv2.waitKey(5000)  # Chờ 5 giây (5000 ms)       
                        
                        # Sau khi 5 giây, quay lại trạng thái nhận diện khuôn mặt tiếp theo
                    else:
                        print(f"{profile[1]} da ton tai.")
                        cv2.putText(frame, "da check-in truocc do", (x + 10, y + h + 60), fontface, 1, (0, 0, 255), 2)
                        # Đợi một chút rồi tiếp tục nhận diện
                        time.sleep(3)

            else:
                cv2.putText(frame, "Unknown", (x + 10, y + h + 30), fontface, 1, (0, 0, 255), 2)

    # Hiển thị hình ảnh nhận diện khuôn mặt từ webcam
    cv2.imshow("nhan dien", frame)

    # Nếu nhấn 'q', thoát khỏi chương trình
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng webcam và đóng tất cả cửa sổ
cam.release()
cv2.destroyAllWindows()
