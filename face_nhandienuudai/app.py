from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2
import queryDB as db
import numpy as np
import os
from playsound import playsound  # Sử dụng playsound để phát âm thanh
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Khởi tạo webcam
def initialize_camera():
    cam = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cam.isOpened():
        print("❌ Không thể mở webcam!")
        raise Exception("Không thể mở webcam")
    return cam

# Khởi tạo webcam
try:
    cam = initialize_camera()
except Exception as e:
    cam = None
    print(f"❌ Lỗi khi khởi tạo webcam: {str(e)}")

# Khởi tạo đối tượng nhận diện khuôn mặt
face_cascade = cv2.CascadeClassifier("libs/haarcascade_frontalface_default.xml")
if face_cascade.empty():
    raise Exception("❌ Không tải được file nhận diện khuôn mặt: libs/haarcascade_frontalface_default.xml")

recognizer = cv2.face.LBPHFaceRecognizer_create()
if not os.path.exists('recognizer/trainningData.yml'):
    raise Exception("❌ Không tìm thấy file training data: recognizer/trainningData.yml")
recognizer.read('recognizer/trainningData.yml')

# Hàm phát âm thanh
def play_audio(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file âm thanh: {file_path}")
        return

    try:
        playsound(file_path)
        print(f"✅ Phát âm thanh: {file_path}")
    except Exception as e:
        print(f"❌ Lỗi khi phát âm thanh: {str(e)}")

# Phát nhạc tự động lúc 12 giờ trưa
def auto_background_music():
    while True:
        now = datetime.now()
        if now.hour == 12 and now.minute == 0:  # Kiểm tra nếu là 12:00 trưa
            print("🎵 Phát nhạc tự động lúc 12:00...")
            play_audio('static/audio/TungLaCover.mp3')
            time.sleep(60)  # Chờ 1 phút trước khi kiểm tra lại
        time.sleep(1)

# Chạy luồng phát nhạc tự động
threading.Thread(target=auto_background_music, daemon=True).start()

# Phát nhạc thử qua API
@app.route('/play_test_music', methods=['POST'])
def play_test_music():
    try:
        play_audio('static/audio/TungLaCover.mp3')
        return jsonify({"success": True, "message": "🎵 Đã phát nhạc thử nghiệm."})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Lỗi: {str(e)}"})

# Phục vụ video từ webcam
def gen_frames():
    global cam
    if cam is None:
        cam = initialize_camera()

    try:
        while True:
            success, frame = cam.read()
            if not success:
                print("❌ Không nhận được khung hình từ webcam.")
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    except GeneratorExit:
        pass

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Trang chính
@app.route('/')
def index():
    return render_template('trangchinh.html')

# Nhận diện khuôn mặt
@app.route('/capture_and_identify', methods=['POST'])
def capture_and_identify():
    global cam
    if cam is None:
        cam = initialize_camera()

    ret, frame = cam.read()
    if not ret:
        return jsonify({"success": False, "message": "❌ Không thể chụp khung hình từ webcam."})

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray)

    if len(faces) == 0:
        return jsonify({"redirect_url": url_for('new_customer')})

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        id, confidence = recognizer.predict(roi_gray)

        # Phát âm thanh "Xin chào" khi nhận diện
        play_audio('static/sounds/xinchao.mp3')

        if confidence < 40:  # Nhận diện thành công
            profile = db.getProfile(id)
            if profile:
                name, total_in_count = profile[1], profile[2]
                level = db.get_level(total_in_count)

                # Cập nhật total_in_count
                db.insertOrUpdate(id, name)

                # Tính toán ưu đãi
                discount = {"- Gold": 15, "- Silver": 10}.get(level, 5)

                print(f"✅ Nhận diện thành công: {name} - Hạng: {level} - Ưu đãi: {discount}%")
                return jsonify({"redirect_url": url_for('uudai', name=name, level=level, discount=discount)})
            else:
                return jsonify({"success": False, "message": "❌ Không nhận diện được khách hàng."})
        else:
            return jsonify({"redirect_url": url_for('new_customer')})

    return jsonify({"success": False, "message": "❌ Lỗi khi nhận diện."})

# Trang thêm khách hàng mới
@app.route('/new_customer')
def new_customer():
    return render_template('nhapttkhachhangmoi.html')

# Lưu khách hàng mới và huấn luyện lại mô hình
@app.route('/capture_and_save_new_customer', methods=['POST'])
def capture_and_save_new_customer():
    global cam
    if cam:
        cam.release()

    try:
        data = request.get_json()
        name = data.get('fullname')
        phone = data.get('phone')

        if not name or not phone:
            return jsonify({"success": False, "message": "❌ Thiếu thông tin khách hàng!"}), 400

        print(f"🚀 Bắt đầu thu thập dữ liệu cho: {name} - {phone}")

        # Lưu vào DB
        db.insertOrUpdate(phone, name)

        # Chạy lệnh thêm dữ liệu và huấn luyện lại
        os.system(f"python getData.py {phone} {name}")
        os.system("python traningData.py")

        return jsonify({"success": True, "message": "✅ Dữ liệu đã được thu thập và mô hình đã được huấn luyện lại!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"❌ Lỗi: {str(e)}"}), 500

# Trang ưu đãi
@app.route('/uudai')
def uudai():
    name = request.args.get("name", "Khách hàng")
    level = request.args.get("level", "Chưa có hạng")
    discount = request.args.get("discount", "0")

    # Phát âm thanh "Cảm ơn" khi mở trang
    play_audio('static/sounds/thankyou.mp3')

    print(f"✅ Ưu đãi: Name={name}, Level={level}, Discount={discount}%")
    return render_template('uudai.html', name=name, level=level, discount=discount)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)