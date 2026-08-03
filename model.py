import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging

class CodeUnderstandingModel(torch.nn.Module):
    def __init__(self, model_path, num_labels=3):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path, num_labels=num_labels)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        logging.info(f"Loaded CodeBERT model from {model_path} on {self.device}")

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.logits