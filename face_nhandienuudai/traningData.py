import cv2
import os
import numpy as np
from PIL import Image

# tạo ra một đối tượng nhận dạng khuôn mặt bằng thuật toán LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
path = 'dataset'  # Sửa lại để khớp với `getData.py`

def getImagesAndLabels(path):
    if not os.path.exists(path):
        print(f"⚠️ Không tìm thấy thư mục dữ liệu: {path}")
        return [], []
    
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".jpg")]
    faces = []
    IDs = []
    
    if len(imagePaths) == 0:
        print("⚠️ Không có ảnh nào để train!")
        return [], []

    for imagePath in imagePaths:
        faceImg = Image.open(imagePath).convert('L')
        faceNp = np.array(faceImg, 'uint8')
        ID = int(os.path.split(imagePath)[-1].split('.')[1])
        faces.append(faceNp)
        IDs.append(ID)

    return IDs, faces

def trainData():
    Ids, faces = getImagesAndLabels(path)

    if len(Ids) == 0:
        print("⚠️ Không có dữ liệu để train! Kiểm tra lại dataset.")
        return

    recognizer.train(faces, np.array(Ids))
    recognizer.save('recognizer/trainningData.yml')
    print('✅ Train thành công!')

trainData()
cv2.destroyAllWindows()
