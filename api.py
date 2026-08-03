from flask import Flask, request, jsonify
from src.preprocess import preprocess_code
from src.inference import CodeAnalyzer
import yaml
import logging

app = Flask(__name__)

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config('config.yaml')
analyzer = CodeAnalyzer(config['model']['path'])

@app.route('/analyze', methods=['POST'])
def analyze_code():
    logger = logging.getLogger(__name__)
    try:
        data = request.json
        code = data.get('code', '')
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        processed_code = preprocess_code(code)
        results = analyzer.analyze(processed_code)
        logger.info(f"API request processed: {results['semantic_class']}")
        return jsonify(results)
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)