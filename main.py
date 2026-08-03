import argparse
import yaml
from src.preprocess import preprocess_code
from src.inference import CodeAnalyzer
from src.utils import setup_logging
import logging

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Multi-Modal Code Intelligence System")
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--code_file', type=str, help='Path to code file for analysis')
    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting Code Intelligence System")

    # Load configuration
    config = load_config(args.config)
    logger.info(f"Loaded config from {args.config}")

    # Initialize analyzer
    analyzer = CodeAnalyzer(config['model']['path'], config['model']['device'])

    # Process input code
    if args.code_file:
        with open(args.code_file, 'r') as f:
            code = f.read()
        processed_code = preprocess_code(code)
        
        # Perform analysis
        results = analyzer.analyze(processed_code)
        logger.info("Analysis Results:")
        for key, value in results.items():
            print(f"{key}: {value}")
    else:
        logger.error("No code file provided. Use --code_file argument.")

if __name__ == "__main__":
    main()