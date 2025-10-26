# server.py
from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import pty
import subprocess
import select
import os
import threading
import requests
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Giữ alive (nếu dùng free plan)
def keep_alive():
    url = os.environ.get('RENDER_EXTERNAL_URL')
    if url:
        def ping():
            while True:
                try:
                    requests.get(url, timeout=5)
                except:
                    pass
                time.sleep(300)
        threading.Thread(target=ping, daemon=True).start()

# HTML Terminal
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>CTOOL Terminal 24/24</title>
    <meta charset="utf-8">
    <style>
        body, html { margin:0; padding:0; height:100%; background:#000; color:#0f0; font-family:'Courier New'; overflow:hidden; }
        #term { width:100%; height:100%; padding:10px; box-sizing:border-box; }
    </style>
</head>
<body>
    <div id="term"></div>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script>
        const socket = io();
        const term = document.getElementById('term');
        let buffer = '';

        const write = (text) => {
            const div = document.createElement('div');
            div.innerHTML = text.replace(/\\n/g, '<br>').replace(/ /g, '&nbsp;');
            term.appendChild(div);
            window.scrollTo(0, document.body.scrollHeight);
        };

        socket.on('output', write);

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                write('> ' + buffer);
                socket.emit('input', buffer + '\\n');
                buffer = '';
            } else if (e.key === 'Backspace') {
                buffer = buffer.slice(0, -1);
            } else if (e.key.length === 1) {
                buffer += e.key;
            }
            socket.emit('input', e.key);
            e.preventDefault();
        });

        socket.on('connect', () => write('\\nChào mừng đến CTOOL Terminal!\\n'));
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@socketio.on('input')
def handle_input(data):
    if hasattr(handle_input, 'master_fd'):
        try:
            os.write(handle_input.master_fd, data.encode())
        except:
            pass

def start_tool():
    master_fd, slave_fd = pty.openpty()
    handle_input.master_fd = master_fd

    proc = subprocess.Popen(
        ['python', 'tool.py'],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        bufsize=0,
        cwd='.'
    )

    def read():
        while True:
            try:
                r, _, _ = select.select([master_fd], [], [], 1)
                if r:
                    out = os.read(master_fd, 1024).decode(errors='ignore')
                    if out:
                        socketio.emit('output', out)
            except:
                break
        proc.wait()

    threading.Thread(target=read, daemon=True).start()

@socketio.on('connect')
def connect():
    if not hasattr(handle_input, 'master_fd'):
        threading.Thread(target=start_tool).start()
    emit('output', '\\nĐang tải và chạy CTOOL.py...\\n')

if __name__ == '__main__':
    keep_alive()
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
