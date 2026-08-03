from .model import CodeUnderstandingModel
import torch
import logging

def resolve_device(requested=None):
    """Pick a torch device, falling back to CPU when CUDA is not available.

    config.yaml ships `device: cuda`, so on any machine without a GPU the model
    landed on CPU while the inputs were sent to CUDA, and inference died on a
    device mismatch. Asking for cuda without cuda now warns and uses the CPU.
    """
    if requested in (None, 'auto'):
        return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if str(requested).startswith('cuda') and not torch.cuda.is_available():
        logging.warning("device=%s requested but CUDA is unavailable; using CPU", requested)
        return torch.device('cpu')
    return torch.device(requested)


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