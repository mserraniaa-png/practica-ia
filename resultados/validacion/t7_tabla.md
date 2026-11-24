| Modelo | Umbral | Costo / 1000 (min) | VP | FP | FN | VN | AUC val |
|---|---|---|---|---|---|---|---|
| Nada es atender (mayoritaria) | — | 7,650 | 0 | 0 | 51 | 149 | — |
| Todo es atender | — | 2,235 | 51 | 149 | 0 | 0 | — |
| ≤ 2★ = atender | — | 3,720 | 27 | 8 | 24 | 141 | — |
| Regresión logística (referencia) | 0.38 | 540 | 51 | 36 | 0 | 113 | 0.936 |
| TF-IDF + red densa (entregado) | 0.13 | 675 | 51 | 45 | 0 | 104 | 0.928 |
| LSTM con embeddings propios (alternativa) | 0.06 | 1,125 | 50 | 65 | 1 | 84 | 0.851 |
