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

        # Transcribe the audio chunk
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
            try:
                transcription = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                transcription = ""  # Handle empty chunks gracefully
            except sr.RequestError as e:
                return jsonify({"error": f"SpeechRecognition API error: {e}"}), 500

        # Log transcription
        print(f"Partial transcription: {transcription}")

        # Use AI to extract metrics (only if transcription is meaningful)
        if transcription.strip():
            extracted_data = extract_metrics_from_transcription(transcription)
            print("Extracted Data:", extracted_data)
        else:
            extracted_data = {"item_name": "N/A", "location": "N/A", "cost": "N/A", "selling_price": "N/A"}

        return jsonify({
            "transcription": transcription,
            "extracted_data": extracted_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)