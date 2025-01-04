from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from ai_transcription import extract_metrics_from_transcription

app = Flask(__name__)

# Initialize the database
DATABASE = 'inventory.db'

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                cost REAL NOT NULL,
                price REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add-item', methods=['POST'])
def add_item():
    data = request.json
    name = data.get('name')
    location = data.get('location')
    cost = data.get('cost')
    price = data.get('price')

    if not all([name, location, cost, price]):
        return jsonify({'error': 'Missing data fields'}), 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventory (name, location, cost, price)
        VALUES (?, ?, ?, ?)
    ''', (name, location, float(cost), float(price)))
    conn.commit()
    conn.close()

    return jsonify({'message': f"Item '{name}' added successfully!"})

@app.route('/process-voice', methods=['POST'])
def process_voice():
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded!"}), 400

    audio_file = request.files['file']
    recognizer = sr.Recognizer()

    try:
        # Convert .webm to .wav
        audio = AudioSegment.from_file(audio_file, format="webm")
        wav_file = BytesIO()
        audio.export(wav_file, format="wav")
        wav_file.seek(0)

        # Use SpeechRecognition to transcribe
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)

        # Use AI to extract metrics
        extracted_data = extract_metrics_from_transcription(transcription)
        if not extracted_data:
            return jsonify({"error": "Failed to extract data using AI"}), 500

        # Placeholder for Google Sheets integration
        print("Extracted Data:", extracted_data)  # For debugging
        # Later: Push this data to Google Sheets

        return jsonify({
            "transcription": transcription,
            "extracted_data": extracted_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)