from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import subprocess
import os
import glob

app = Flask(__name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'wav', 'mp3'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        process = subprocess.Popen(['bash', 'inference_bash.sh', filename], stdout=subprocess.PIPE)
        output, error = process.communicate()
        if error:
            return 'Error in processing'
        else:
            # Get the only file in the results directory
            result_files = glob.glob('results/*.mp4')
            print(result_files)
            if len(result_files) != 1:
                return 'Error: Expected one result file, but found {}'.format(len(result_files))
            result_file = result_files[0]

            # Send the result file
            # with open(result_file, 'rb') as f:
            #     video_data = f.read()
            # response = send_file(video_data, mimetype='video/mp4')

            print(result_file)
            
            response = send_file(result_file, mimetype='video/mp4')


            # Delete all files in the results directory
            # for f in result_files:
            #     os.remove(f)

            return response

if __name__ == '__main__':
    app.run(debug=True)
