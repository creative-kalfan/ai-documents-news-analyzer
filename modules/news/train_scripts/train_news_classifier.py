import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
)
import numpy as np
from sklearn.metrics import accuracy_score, f1_score


MODEL_NAME = "distilbert-base-uncased"
SAVE_DIR = "models/fake_news/distilbert_news"


def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    return {
        "accuracy": accuracy_score(labels, preds),
        "f1": f1_score(labels, preds, average="weighted"),
    }


def main():
    dataset = load_dataset("liar")  # sample dataset
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def preprocess(batch):
        return tokenizer(batch["statement"], truncation=True, padding="max_length", max_length=256)

    dataset = dataset.map(preprocess, batched=True)
    dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

    args = TrainingArguments(
        output_dir=SAVE_DIR,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        evaluation_strategy="steps",
        learning_rate=2e-5,
        num_train_epochs=2,
        logging_steps=200,
        eval_steps=500,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(SAVE_DIR)


if __name__ == "__main__":
    main()
