from src.model import CodeUnderstandingModel
import torch
import logging

class CodeAnalyzer:
    def __init__(self, model_path, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = CodeUnderstandingModel(model_path)
        self.device = device
        self.labels = ['sorting_algorithm', 'rest_api', 'other']
        logging.info("Initialized CodeAnalyzer")

    def analyze(self, processed_code):
        logger = logging.getLogger(__name__)
        
    
        inputs = self.model.tokenizer(
            processed_code['code'],
            return_tensors='pt',
            padding=True,
            truncation=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
    
       
        with torch.no_grad():
            logits = self.model(**inputs)
            probs = torch.softmax(logits, dim=-1)
            pred_idx = torch.argmax(probs, dim=-1).item()
        
        results = {
            'semantic_class': self.labels[pred_idx],
            'confidence': probs[0][pred_idx].item(),
            'metadata': processed_code['metadata']
        }
        
        logger.info(f"Analysis complete: {results['semantic_class']} (confidence: {results['confidence']:.2f})")
        return results