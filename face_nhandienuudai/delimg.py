import os
import glob
import sqlite3

def reset_data():
    # 1. Xóa ảnh trong thư mục dataSet
    dataset_path = 'dataSet'  # chỉnh tên cho đúng với thư mục của bạn
    files = glob.glob(os.path.join(dataset_path, '*.jpg'))
    for f in files:
        os.remove(f)
    print(f"Đã xóa {len(files)} ảnh trong thư mục {dataset_path}")

    # 2. Xóa dữ liệu trong bảng SQLite
    db_path = 'faceid.db'  # file DB của bạn
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Giả sử bảng chứa thông tin khách tên là 'users' (bạn đổi lại tên bảng nếu khác)
    cursor.execute("DELETE FROM people")  
    
    conn.commit()
    conn.close()
    print("Đã xóa dữ liệu trong bảng users")

if __name__ == '__main__':
    reset_data()

