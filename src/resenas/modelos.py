"""Modelos (ADR-02): TF-IDF compartido, regresión logística (referencia) y red densa en PyTorch."""

import numpy as np
import torch
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion
from torch import nn

from resenas import config
from resenas.texto import limpiar


def vectorizador() -> FeatureUnion:
    """Palabras 1–2 y caracteres 3–5 (ayudan con faltas de ortografía). Vocabulario sólo de entrenamiento."""
    return FeatureUnion([
        ("palabras", TfidfVectorizer(preprocessor=limpiar, analyzer="word", ngram_range=(1, 2),
                                     min_df=2, sublinear_tf=True, token_pattern=r"(?u)<\w+>|\b\w+\b")),
        ("caracteres", TfidfVectorizer(preprocessor=limpiar, analyzer="char_wb", ngram_range=(3, 5),
                                       min_df=2, sublinear_tf=True)),
    ])


class Logistica:
    """Referencia: regresión logística sobre TF-IDF. No es el modelo entregado."""

    def __init__(self, C: float = 1.0, semilla: int = config.SEMILLA):
        self.C, self.semilla = C, semilla

    def fit(self, textos, y):
        self.vec = vectorizador()
        X = self.vec.fit_transform(textos)
        self.clf = LogisticRegression(C=self.C, max_iter=2000, random_state=self.semilla).fit(X, y)
        return self

    def predict_proba(self, textos) -> np.ndarray:
        return self.clf.predict_proba(self.vec.transform(textos))[:, 1]


class _Red(nn.Module):
    def __init__(self, entradas: int, ocultas: int, dropout: float):
        super().__init__()
        self.capas = nn.Sequential(nn.Linear(entradas, ocultas), nn.ReLU(), nn.Dropout(dropout), nn.Linear(ocultas, 1))

    def forward(self, x):
        return self.capas(x).squeeze(-1)


def _a_tensor(X) -> torch.Tensor:
    X = X.toarray() if sparse.issparse(X) else np.asarray(X)
    return torch.from_numpy(X.astype(np.float32))


class RedDensa:
    """Modelo entregado: TF-IDF → capa oculta ReLU + dropout → salida sigmoide (PyTorch, CPU)."""

    def __init__(self, ocultas: int = 64, dropout: float = 0.3, weight_decay: float = 1e-4,
                 epocas: int = 40, lr: float = 1e-3, lote: int = 32, semilla: int = config.SEMILLA):
        self.ocultas, self.dropout, self.weight_decay = ocultas, dropout, weight_decay
        self.epocas, self.lr, self.lote, self.semilla = epocas, lr, lote, semilla

    def fit(self, textos, y):
        torch.manual_seed(self.semilla)
        gen = torch.Generator().manual_seed(self.semilla)
        self.vec = vectorizador()
        X = _a_tensor(self.vec.fit_transform(textos))
        t = torch.tensor(np.asarray(y), dtype=torch.float32)
        self.red = _Red(X.shape[1], self.ocultas, self.dropout)
        opt = torch.optim.Adam(self.red.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        perdida = nn.BCEWithLogitsLoss()
        self.red.train()
        for _ in range(self.epocas):
            orden = torch.randperm(len(t), generator=gen)
            for i in range(0, len(t), self.lote):
                idx = orden[i:i + self.lote]
                opt.zero_grad()
                perdida(self.red(X[idx]), t[idx]).backward()
                opt.step()
        self.red.eval()
        return self

    def logits(self, textos) -> np.ndarray:
        with torch.no_grad():
            return self.red(_a_tensor(self.vec.transform(textos))).numpy()

    def predict_proba(self, textos) -> np.ndarray:
        return 1 / (1 + np.exp(-self.logits(textos)))

    def params(self) -> dict:
        return {"ocultas": self.ocultas, "dropout": self.dropout, "weight_decay": self.weight_decay,
                "epocas": self.epocas, "lr": self.lr, "lote": self.lote}
