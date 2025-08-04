from playsound import playsound
import os

# Hàm phát âm thanh
def play_audio(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file âm thanh: {file_path}")
        return

    try:
        playsound(file_path)
        print("✅ Phát âm thanh thành công.")
    except Exception as e:
        print(f"❌ Lỗi khi phát âm thanh: {str(e)}")

# Phát thử âm thanh
play_audio('static/sounds/xinchao.mp3')