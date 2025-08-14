# src/services/moderation/torch_model.py
from __future__ import annotations
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import Tuple

class TorchModerator:
    """
    Lädt ein HF-Textklassifikationsmodell (binary oder multi-class) und gibt (score,label) zurück.
    score ∈ [0,1] ~ Wahrscheinlichkeit für "toxic".
    """
    def __init__(self, model_path: str, label_toxic: str | None = None) -> None:
        if not model_path or not os.path.exists(model_path):
            raise RuntimeError(f"Moderationsmodell nicht gefunden: {model_path}")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device).eval()

        cfg = getattr(self.model, "config", None)
        self.id2label = getattr(cfg, "id2label", None) or {}
        self.label2id = {v: int(k) for k, v in (getattr(cfg, "label2id", None) or {}).items()}
        self.toxic_label = label_toxic or ("toxic" if "toxic" in self.label2id else None)

    @torch.inference_mode()
    def score(self, text: str) -> Tuple[float, str]:
        if not text:
            return 0.0, "ok"
        enc = self.tokenizer(text[:2048], truncation=True, max_length=512, return_tensors="pt")
        enc = {k: v.to(self.device) for k, v in enc.items()}
        out = self.model(**enc)
        logits = out.logits
        if logits.shape[-1] == 1:
            prob = torch.sigmoid(logits).item()
            label = "toxic" if prob >= 0.5 else "ok"
            return float(prob), label
        probs = torch.softmax(logits, dim=-1).squeeze(0)
        if self.toxic_label and self.toxic_label in self.label2id:
            idx = self.label2id[self.toxic_label]
            prob = probs[idx].item()
            return float(prob), self.toxic_label
        idx = int(torch.argmax(probs).item())
        prob = probs[idx].item()
        label = self.id2label.get(idx, f"label_{idx}")
        return float(prob), label
