import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from datasets import load_dataset
import yaml
import logging

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def prepare_dataset():
    dataset = load_dataset('code_search_net', 'python', split='train[:1%]')  # Use 1% for demo
    return dataset

def train_model(config_path='config.yaml'):
    logger = logging.getLogger(__name__)
    config = load_config(config_path)
    
    model_name = config['model']['path']
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)
    dataset = prepare_dataset()
    
    def tokenize_function(examples):
        return tokenizer(examples['func_code'], padding="max_length", truncation=True)
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    training_args = TrainingArguments(
        output_dir=config['training']['output_dir'],
        num_train_epochs=config['training']['epochs'],
        per_device_train_batch_size=config['training']['batch_size'],
        save_strategy="epoch",
        logging_dir=config['training']['logging_dir'],
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )
    
    trainer.train()
    model.save_pretrained(config['model']['save_path'])
    tokenizer.save_pretrained(config['model']['save_path'])
    logger.info(f"Model trained and saved to {config['model']['save_path']}")