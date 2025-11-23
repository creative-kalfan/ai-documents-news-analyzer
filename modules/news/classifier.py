from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np


class NewsClassifier:
    def __init__(self, model_path="distilbert-base-uncased", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()

    def predict(self, texts):
        inputs = self.tokenizer(texts, truncation=True, padding=True, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()

        results = []
        for p in probs:
            label_id = int(np.argmax(p))
            results.append({
                "label_id": label_id,
                "confidence": float(max(p)),
                "probabilities": p.tolist()
            })

        return results
