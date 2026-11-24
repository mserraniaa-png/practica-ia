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

    def vocabulario_palabras(self) -> list:
        return list(self.vec.transformer_list[0][1].vocabulary_)

    def guardar(self, carpeta) -> list:
        """Escribe vectorizador.joblib y red.pt; devuelve los archivos escritos."""
        import joblib
        for _, v in self.vec.transformer_list:
            # Privacidad: stop_words_ guarda todos los n-gramas raros (frases y nombres) y no se usa
            # para transformar; vocabulary_ se reordena alfabéticamente para que no conserve el orden
            # del texto. Cada término mantiene su índice, así que el modelo no cambia.
            if hasattr(v, "stop_words_"):
                del v.stop_words_
            v.vocabulary_ = dict(sorted(v.vocabulary_.items()))
        joblib.dump(self.vec, carpeta / "vectorizador.joblib")
        torch.save({"estado": self.red.state_dict(), "entradas": self.red.capas[0].in_features,
                    "params": self.params()}, carpeta / "red.pt")
        return ["vectorizador.joblib", "red.pt"]

    @classmethod
    def cargar(cls, carpeta) -> "RedDensa":
        import joblib
        d = torch.load(carpeta / "red.pt", weights_only=True)
        m = cls(**d["params"])
        m.vec = joblib.load(carpeta / "vectorizador.joblib")
        m.red = _Red(d["entradas"], m.ocultas, m.dropout)
        m.red.load_state_dict(d["estado"])
        m.red.eval()
        return m


_TOKEN = __import__("re").compile(r"<\w+>|\w+|[^\w\s]")


def tokenizar(texto) -> list:
    return _TOKEN.findall(limpiar(texto))


class _RedLSTM(nn.Module):
    def __init__(self, vocab: int, emb: int, ocultas: int, dropout: float):
        super().__init__()
        self.emb = nn.Embedding(vocab, emb, padding_idx=0)
        self.lstm = nn.LSTM(emb, ocultas, batch_first=True)
        self.drop = nn.Dropout(dropout)
        self.salida = nn.Linear(ocultas, 1)

    def forward(self, ids):
        mascara = (ids != 0).unsqueeze(-1).float()
        h, _ = self.lstm(self.emb(ids))
        # Promedio de las salidas de la LSTM sobre los tokens reales (sin relleno).
        prom = (h * mascara).sum(1) / mascara.sum(1).clamp(min=1)
        return self.salida(self.drop(prom)).squeeze(-1)


class LSTMPropia:
    """Alternativa (T8): embeddings propios (sin preentrenar) + LSTM de una capa."""

    def __init__(self, emb: int = 64, ocultas: int = 64, dropout: float = 0.3, max_tokens: int = 200,
                 min_frec: int = 2, epocas: int = 15, lr: float = 2e-3, lote: int = 32, semilla: int = config.SEMILLA):
        self.emb, self.ocultas, self.dropout, self.max_tokens = emb, ocultas, dropout, max_tokens
        self.min_frec, self.epocas, self.lr, self.lote, self.semilla = min_frec, epocas, lr, lote, semilla

    def _ids(self, textos) -> torch.Tensor:
        filas = [[self.vocab.get(t, 1) for t in tokenizar(x)][: self.max_tokens] or [1] for x in textos]
        largo = max(len(f) for f in filas)
        return torch.tensor([f + [0] * (largo - len(f)) for f in filas], dtype=torch.long)

    def fit(self, textos, y):
        from collections import Counter
        torch.manual_seed(self.semilla)
        gen = torch.Generator().manual_seed(self.semilla)
        frec = Counter(t for x in textos for t in tokenizar(x))
        # 0 = relleno, 1 = desconocida
        self.vocab = {t: i + 2 for i, t in enumerate(sorted(t for t, n in frec.items() if n >= self.min_frec))}
        X = self._ids(textos)
        t = torch.tensor(np.asarray(y), dtype=torch.float32)
        self.red = _RedLSTM(len(self.vocab) + 2, self.emb, self.ocultas, self.dropout)
        opt = torch.optim.Adam(self.red.parameters(), lr=self.lr)
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

    def predict_proba(self, textos) -> np.ndarray:
        with torch.no_grad():
            return torch.sigmoid(self.red(self._ids(list(textos)))).numpy()
