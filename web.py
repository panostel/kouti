from flask import Flask, request, jsonify, render_template
import json
import os
import glob
from werkzeug.utils import secure_filename

app = Flask(__name__)

TAGS_FILE = os.path.join(os.path.dirname(__file__), 'tags.json')
AUDIO_DIR = '/home/pte/pi-rfid'
REGISTER_MODE_FILE = '/tmp/register_mode'
PENDING_UID_FILE = '/tmp/pending_uid'


def load_tags():
    with open(TAGS_FILE, 'r') as f:
        return json.load(f)


def save_tags(data):
    with open(TAGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/tags', methods=['GET'])
def get_tags():
    return jsonify(load_tags())


@app.route('/api/tags', methods=['POST'])
def add_tag():
    body = request.get_json()
    uid = body.get('uid')
    file = body.get('file')
    if not uid or not file:
        return jsonify({'error': 'uid and file required'}), 400
    data = load_tags()
    data['tags'][uid] = file
    save_tags(data)
    return jsonify({'ok': True})


@app.route('/api/tags/<path:uid>', methods=['DELETE'])
def delete_tag(uid):
    data = load_tags()
    if uid not in data['tags']:
        return jsonify({'error': 'not found'}), 404
    del data['tags'][uid]
    save_tags(data)
    return jsonify({'ok': True})


@app.route('/api/register/start', methods=['POST'])
def register_start():
    # Clear any previous pending UID
    try:
        os.remove(PENDING_UID_FILE)
    except FileNotFoundError:
        pass
    open(REGISTER_MODE_FILE, 'w').close()
    return jsonify({'ok': True})


@app.route('/api/register/poll', methods=['GET'])
def register_poll():
    if os.path.exists(PENDING_UID_FILE):
        with open(PENDING_UID_FILE, 'r') as f:
            uid = f.read().strip()
        return jsonify({'uid': uid})
    return jsonify({'uid': None})


@app.route('/api/register/cancel', methods=['POST'])
def register_cancel():
    try:
        os.remove(REGISTER_MODE_FILE)
    except FileNotFoundError:
        pass
    try:
        os.remove(PENDING_UID_FILE)
    except FileNotFoundError:
        pass
    return jsonify({'ok': True})


@app.route('/api/files', methods=['GET'])
def list_files():
    files = sorted(glob.glob(os.path.join(AUDIO_DIR, '*.mp3')))
    return jsonify(files)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    f = request.files['file']
    if not f.filename.lower().endswith('.mp3'):
        return jsonify({'error': 'only .mp3 files allowed'}), 400
    filename = secure_filename(f.filename)
    dest = os.path.join(AUDIO_DIR, filename)
    f.save(dest)
    return jsonify({'ok': True, 'path': dest})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
