# 导入需要的库
from flask import Flask, request, send_from_directory, render_template_string
import os
import socket

# 1. 初始化程序
app = Flask(__name__)
# 设置文件保存的文件夹（自动创建，不用手动建）
UPLOAD_FOLDER = '手机电脑互传文件'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 2. 网页模板（极简界面，手机电脑都适配）
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>手机电脑互传文件</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 20px auto; padding: 0 20px; }
        .box { border: 2px solid #42b983; padding: 20px; border-radius: 10px; margin: 20px 0; }
        button { background: #42b983; color: white; padding: 8px 15px; border: none; border-radius: 5px; cursor: pointer; }
        input { margin: 10px 0; }
        a { color: #42b983; text-decoration: none; margin: 5px 0; display: block; }
    </style>
</head>
<body>
    <h1>📱手机💻电脑互传文件</h1>
    <div class="box">
        <h3>✅ 上传文件到电脑</h3>
        <form method=post enctype=multipart/form-data>
            <input type=file name=file multiple>
            <button type=submit>开始上传</button>
        </form>
    </div>
    <div class="box">
        <h3>📂 已传文件（点击下载）</h3>
        {% for file in files %}
        <a href="/download/{{ file }}">{{ file }}</a>
        {% endfor %}
    </div>
</body>
</html>
'''

# 3. 首页：展示上传+文件列表
@app.route('/', methods=['GET', 'POST'])
def index():
    # 处理文件上传
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
    # 获取已传文件列表
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(HTML_PAGE, files=files)

# 4. 下载文件接口
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# 5. 获取电脑局域网IP（自动获取，不用手动查）
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 6. 启动程序
if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 8080
    print(f"✅ 程序启动成功！")
    print(f"👉 手机/电脑浏览器访问：http://{local_ip}:{port}")
    print(f"📂 电脑文件保存路径：{os.path.abspath(UPLOAD_FOLDER)}")
    app.run(host='0.0.0.0', port=port, debug=False)
