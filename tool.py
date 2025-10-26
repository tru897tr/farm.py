# tool.py
import os
import subprocess
import sys
import time

def download():
    print("Đang tải CTOOL.py từ GitHub...")
    url = "https://raw.githubusercontent.com/C-Dev7929/Tools/refs/heads/main/main-xw.py"
    result = subprocess.run(['curl', '-s', '-L', '-o', 'CTOOL.py', url], capture_output=True, text=True)
    if result.returncode == 0:
        print("Tải thành công!")
    else:
        print("Lỗi tải:", result.stderr)
        sys.exit(1)

def run():
    if not os.path.exists('CTOOL.py'):
        download()
    
    print("Khởi động CTOOL.py...")
    print("— Nhập key, config, lệnh như bình thường —\n")
    
    subprocess.run(['python', 'CTOOL.py'])

if __name__ == '__main__':
    run()
