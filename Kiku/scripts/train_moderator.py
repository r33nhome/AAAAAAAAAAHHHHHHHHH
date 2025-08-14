# scripts/train_moderator.py
from __future__ import annotations
import argparse, os
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np
from sklearn.metrics import f1_score, accuracy_score

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="Pfad zu CSV mit Spalten: text,label (ok|toxic)")
    ap.add_argument("--out", required=True, help="Zielordner für gespeichertes Modell")
    ap.add_argument("--base", default="distilroberta-base", help="HF-Base-Modell")
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--bsz", type=int, default=16)
    args = ap.parse_args()

    ds = load_dataset("csv", data_files={"train": args.data, "validation": args.data}, split=None)
    label_list = ["ok", "toxic"]
    label2id = {l:i for i,l in enumerate(label_list)}
    id2label = {i:l for l,i in label2id.items()}

    tok = AutoTokenizer.from_pretrained(args.base, use_fast=True)
    def tok_fn(ex):
        out = tok(ex["text"], truncation=True, max_length=512)
        out["labels"] = [label2id.get(l, 0) for l in ex["label"]]
        return out

    ds = {k: v.map(tok_fn, batched=True) for k,v in ds.items()}

    model = AutoModelForSequenceClassification.from_pretrained(
        args.base, num_labels=len(label_list), id2label=id2label, label2id=label2id
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {
            "acc": accuracy_score(labels, preds),
            "f1": f1_score(labels, preds)
        }

    training_args = TrainingArguments(
        output_dir=args.out,
        learning_rate=5e-5,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.bsz,
        per_device_eval_batch_size=args.bsz,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        logging_steps=50,
        load_best_model_at_end=True,
        fp16=True if os.getenv("USE_FP16","0")=="1" else False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        tokenizer=tok,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(args.out)
    tok.save_pretrained(args.out)
    print("saved to", args.out)

if __name__ == "__main__":
    main()
