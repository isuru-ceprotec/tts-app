import os
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from gtts import gTTS
import io
import uuid

app = Flask(__name__)

# Create uploads directory
os.makedirs('uploads', exist_ok=True)

LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'hi': 'Hindi',
    'ar': 'Arabic'
}

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>TTS App - Free Text to Speech</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                width: 100%;
                max-width: 800px;
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4a00e0 0%, #8e2de2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 15px;
            }
            
            .header p {
                opacity: 0.9;
                font-size: 1.1rem;
            }
            
            .content {
                padding: 30px;
            }
            
            .input-section {
                margin-bottom: 25px;
            }
            
            textarea {
                width: 100%;
                min-height: 150px;
                padding: 20px;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 16px;
                resize: vertical;
                transition: border-color 0.3s;
            }
            
            textarea:focus {
                outline: none;
                border-color: #4a00e0;
            }
            
            .controls {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            
            .control-group {
                display: flex;
                flex-direction: column;
            }
            
            label {
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            
            select {
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                background: white;
            }
            
            .buttons {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-top: 25px;
            }
            
            button {
                padding: 15px 30px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                flex: 1;
                min-width: 200px;
            }
            
            .btn-convert {
                background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
                color: white;
            }
            
            .btn-save {
                background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
                color: white;
            }
            
            .btn-clear {
                background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
                color: white;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .audio-section {
                margin-top: 30px;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                display: none;
            }
            
            audio {
                width: 100%;
                margin-top: 15px;
            }
            
            .status {
                text-align: center;
                margin: 15px 0;
                font-weight: 500;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
                color: #4a00e0;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #4a00e0;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .error {
                color: #ff416c;
                text-align: center;
                margin: 10px 0;
                display: none;
            }
            
            @media (max-width: 768px) {
                .container {
                    border-radius: 15px;
                }
                
                .header {
                    padding: 20px;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
                
                .content {
                    padding: 20px;
                }
                
                .controls {
                    grid-template-columns: 1fr;
                }
                
                button {
                    min-width: 100%;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔊 Free TTS Converter</h1>
                <p>Convert text to speech online - No installation required</p>
            </div>
            
            <div class="content">
                <div class="input-section">
                    <textarea id="textInput" placeholder="Enter your text here... (Maximum 2000 characters)
                    
Example: Hello! Welcome to our free text-to-speech service. This app can convert any text into natural sounding speech in multiple languages."></textarea>
                </div>
                
                <div class="controls">
                    <div class="control-group">
                        <label for="languageSelect">🌐 Language</label>
                        <select id="languageSelect">
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                            <option value="it">Italian</option>
                            <option value="ja">Japanese</option>
                            <option value="ko">Korean</option>
                            <option value="zh">Chinese</option>
                            <option value="hi">Hindi</option>
                            <option value="ar">Arabic</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="speedSelect">⚡ Speed</label>
                        <select id="speedSelect">
                            <option value="normal">Normal</option>
                            <option value="slow">Slow</option>
                            <option value="fast">Fast</option>
                        </select>
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Converting text to speech...</p>
                </div>
                
                <div class="error" id="error"></div>
                
                <div class="buttons">
                    <button class="btn-convert" onclick="convertText()">
                        🔊 Convert to Speech
                    </button>
                    <button class="btn-save" onclick="saveAudio()" id="saveBtn" disabled>
                        💾 Save as MP3
                    </button>
                    <button class="btn-clear" onclick="clearText()">
                        🗑️ Clear Text
                    </button>
                </div>
                
                <div class="audio-section" id="audioSection">
                    <div class="status" id="audioStatus">Your audio is ready!</div>
                    <audio controls id="audioPlayer"></audio>
                </div>
            </div>
        </div>
        
        <script>
            let currentAudioData = null;
            
            async function convertText() {
                const text = document.getElementById('textInput').value.trim();
                const lang = document.getElementById('languageSelect').value;
                const speed = document.getElementById('speedSelect').value;
                
                if (!text) {
                    showError('Please enter some text');
                    return;
                }
                
                if (text.length > 2000) {
                    showError('Text is too long! Maximum 2000 characters.');
                    return;
                }
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('error').style.display = 'none';
                
                try {
                    const response = await fetch('/convert', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            text: text,
                            lang: lang,
                            speed: speed
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Conversion failed');
                    }
                    
                    // Store audio data
                    currentAudioData = data.audio;
                    
                    // Create audio element
                    const audioPlayer = document.getElementById('audioPlayer');
                    audioPlayer.src = 'data:audio/mp3;base64,' + data.audio;
                    
                    // Show audio section
                    document.getElementById('audioSection').style.display = 'block';
                    document.getElementById('audioStatus').textContent = 
                        `Audio generated successfully! Language: ${data.language}`;
                    
                    // Enable save button
                    document.getElementById('saveBtn').disabled = false;
                    
                    // Play audio automatically
                    audioPlayer.play();
                    
                    showError(''); // Clear any previous errors
                    
                } catch (error) {
                    showError('Error: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }
            
            async function saveAudio() {
                if (!currentAudioData) return;
                
                try {
                    const response = await fetch('/save', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            audio: currentAudioData
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Save failed');
                    }
                    
                    // Trigger download
                    const link = document.createElement('a');
                    link.href = data.url;
                    link.download = data.filename;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    
                    alert('Audio saved successfully!');
                    
                } catch (error) {
                    showError('Save error: ' + error.message);
                }
            }
            
            function clearText() {
                document.getElementById('textInput').value = '';
                document.getElementById('audioSection').style.display = 'none';
                document.getElementById('saveBtn').disabled = true;
                currentAudioData = null;
                showError('');
            }
            
            function showError(message) {
                const errorDiv = document.getElementById('error');
                if (message) {
                    errorDiv.textContent = message;
                    errorDiv.style.display = 'block';
                } else {
                    errorDiv.style.display = 'none';
                }
            }
            
            // Add some sample text on load
            window.onload = function() {
                const textarea = document.getElementById('textInput');
                if (!textarea.value.trim()) {
                    textarea.value = "Hello! Welcome to our free text-to-speech service. " +
                                   "You can convert any text into natural sounding audio. " +
                                   "Try different languages and speeds!";
                }
            };
        </script>
    </body>
    </html>
    '''

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.json
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')
        speed = data.get('speed', 'normal')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        if len(text) > 2000:
            return jsonify({'error': 'Text too long (max 2000 chars)'}), 400
        
        # Set speed
        slow = speed == 'slow'
        
        # Convert text to speech
        tts = gTTS(text=text, lang=lang, slow=slow)
        
        # Save to file
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = os.path.join('uploads', filename)
        tts.save(filepath)
        
        # Read file as base64
        import base64
        with open(filepath, 'rb') as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Clean up
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'language': LANGUAGES.get(lang, 'Unknown'),
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.json
        audio_base64 = data.get('audio')
        
        if not audio_base64:
            return jsonify({'error': 'No audio data'}), 400
        
        import base64
        import time
        
        # Decode audio
        audio_data = base64.b64decode(audio_base64)
        filename = f"tts_{int(time.time())}.mp3"
        filepath = os.path.join('uploads', filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        return jsonify({
            'success': True,
            'url': f'/download/{filename}',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory('uploads', filename, as_attachment=True)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'tts-app'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)