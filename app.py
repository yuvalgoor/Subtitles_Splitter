import threading
import webbrowser

from flask import Flask, render_template, request, send_file
import os
import tempfile

from main import main

app = Flask(__name__)


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        max_length = int(request.form['max_length'])
        srt_file = request.files['srt_file']
        temp_dir = tempfile.mkdtemp()
        input_file_path = os.path.join(temp_dir, srt_file.filename)
        output_file_path = f"{os.path.splitext(input_file_path)[0]}_split.srt"
        srt_file.save(input_file_path)

        main(input_file_path, max_length)  # Call your processing function

        return send_file(output_file_path, as_attachment=True)
    return render_template('index.html')


if __name__ == '__main__':
    threading.Timer(1.25, open_browser).start()  # Open a web browser after a short delay
    app.run(debug=True)
