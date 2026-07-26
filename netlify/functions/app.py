from flask import Flask, request, jsonify
from flask_cors import CORS
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>🌊 अनिकेत नंबर इंफॉर्मेशन</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; background: #f0f2f5; }
        input { padding: 12px; width: 280px; border-radius: 8px; border: 1px solid #ccc; font-size: 16px; }
        button { padding: 12px 30px; background: #0d47a1; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
        .result { margin-top: 20px; background: white; padding: 20px; border-radius: 12px; display: inline-block; text-align: left; }
        h1 { color: #0d47a1; }
    </style>
    </head>
    <body>
        <h1>🌊 अनिकेत नंबर इंफॉर्मेशन</h1>
        <form id="searchForm">
            <input type="text" id="phone" placeholder="+91 98765 43210" required>
            <button type="submit">🔍 खोजें</button>
        </form>
        <div id="result" class="result"></div>
        <script>
            document.getElementById('searchForm').onsubmit = async function(e) {
                e.preventDefault();
                const num = document.getElementById('phone').value;
                const res = await fetch('/.netlify/functions/app/lookup?number=' + encodeURIComponent(num));
                const data = await res.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            };
        </script>
    </body>
    </html>
    '''

@app.route('/lookup')
def lookup():
    number = request.args.get('number')
    if not number:
        return jsonify({'error': 'नंबर डालें'}), 400
    
    try:
        parsed = phonenumbers.parse(number, None)
        result = {
            'international': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'national': phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
            'is_valid': phonenumbers.is_valid_number(parsed),
            'is_possible': phonenumbers.is_possible_number(parsed),
            'country': geocoder.description_for_number(parsed, 'en') or 'Unknown',
            'operator': carrier.name_for_number(parsed, 'en') or 'Unknown',
            'timezone': list(timezone.time_zones_for_number(parsed))
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Netlify Functions के लिए ज़रूरी
def handler(event, context):
    return app(event, context)