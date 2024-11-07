from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, auth, initialize_app
import requests
import os
from functools import wraps
from urllib.parse import urlparse
from dotenv import load_dotenv
import urllib.request
import json
load_dotenv()

# Load environment variables
ENRICHMENT_API_KEY = os.getenv('ENRICHMENT_API_KEY')



url = os.getenv('FIREBASE_CREDENTIALS2')

with urllib.request.urlopen(url) as response:
    content = response.read().decode('utf-8')  # Read and decode the content

FIREBASE_CREDENTIALS2 = json.loads(content)

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin

cred = credentials.Certificate(FIREBASE_CREDENTIALS2)
initialize_app(cred)


def validate_url(url):
    try:
        result = urlparse(url)
        print(result)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_domain_name(url):
    return urlparse(url).netloc

@app.route('/')
def index():
    return jsonify({'message': 'Hello, world!'})


@app.route('/api/enrich', methods=['POST'])
def enrich_lead():
    data = request.get_json()
    print(data)
    # Validate input
    if not data.get('companyName') or not data.get('website'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if not validate_url(data['website']):
        return jsonify({'error': 'Invalid website URL'}), 400

    try:

        
        response = requests.get(
            f"https://companyenrichment.abstractapi.com/v2?api_key={ENRICHMENT_API_KEY}&domain={get_domain_name(data['website'])}",
        )
        
        if response.status_code == 200:
            enriched_data = response.json()
            
            return jsonify(enriched_data)
        else:
            # Fallback to basic data if enrichment fails
            return jsonify({
                'name': data['companyName'],
                'domain': urlparse(data['website']).netloc,
                'status': 'Basic information only - enrichment failed'
            })

    except Exception as e:
        return jsonify({'error': f'exception throw: {str(e)}'}), 500

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'production':
        app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        app.run(debug=True)