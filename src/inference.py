from .model import CodeUnderstandingModel
# Device selection lives in utils: it is ordinary logic, and importing this
# module pulls in transformers, which nothing about choosing a device needs.
from .utils import resolve_device  # noqa: F401  (re-exported)
import torch
import logging

class CodeAnalyzer:
    def __init__(self, model_path, device=None):
        self.device = resolve_device(device)
        self.model = CodeUnderstandingModel(model_path, device=self.device)
        self.labels = ['sorting_algorithm', 'rest_api', 'other']
        logging.info("Initialized CodeAnalyzer on %s", self.device)

    def analyze(self, processed_code):
        logger = logging.getLogger(__name__)
        
    
        inputs = self.model.tokenizer(
            processed_code['code'],
            return_tensors='pt',
            padding=True,
            truncation=True
        )
        # Only pass what forward() accepts. BERT-family tokenizers also return
        # token_type_ids, which would be an unexpected keyword argument.
        inputs = {k: v.to(self.device) for k, v in inputs.items()
                  if k in ('input_ids', 'attention_mask')}

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