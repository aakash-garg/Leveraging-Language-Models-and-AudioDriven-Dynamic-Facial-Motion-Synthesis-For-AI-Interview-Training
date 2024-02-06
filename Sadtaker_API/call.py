import requests

# Specify the local path to your file
file_path = 'audio.wav'

# Specify the URL of your API
url = 'http://127.0.0.1:4500/process_audio'

# Open the file in binary mode
with open(file_path, 'rb') as f:
    # Send the file to the API
    response = requests.post(url, files={'file': f})

# Check if the request was successful
if response.status_code == 200:
    # Save the video data to a file
    with open('output.mp4', 'wb') as f:
        f.write(response.content)
else:
    print('Error:', response.status_code, response.text)
