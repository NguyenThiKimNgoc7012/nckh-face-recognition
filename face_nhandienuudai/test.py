import cv2

# Mở camera
cap = cv2.VideoCapture(0)

# Kiểm tra nếu camera mở thành công
if not cap.isOpened():
    print("Không thể mở camera")
    exit()

while True:
    # Đọc một frame từ camera
    ret, frame = cap.read()

    # Nếu không thể đọc được frame, thoát vòng lặp
    if not ret:
        print("Không thể nhận dữ liệu từ camera")
        break

    # Hiển thị frame trong một cửa sổ
    cv2.imshow('Camera Frame', frame)

    # Nhấn 'q' để thoát khỏi vòng lặp
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng camera và đóng tất cả cửa sổ
cap.release()
cv2.destroyAllWindows()

