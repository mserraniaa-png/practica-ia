| Modelo | Calibración | ECE [IC 95 %] | Brier | Costo honesto / 1000, umbral barrido (± desv) | FP / FN | Costo honesto / 1000, umbral 0.09 | FP / FN |
|---|---|---|---|---|---|---|---|
| TF-IDF + red densa (entregado) | sin calibrar | 0.099 [0.072, 0.148] | 0.108 | 919 (± 22) | 41.2 / 2.0 | 810 | 54.0 / 0.0 |
| TF-IDF + red densa (entregado) | Platt | 0.059 [0.046, 0.114] | 0.101 | 964 (± 110) | 43.2 / 2.1 | 833 | 44.5 / 1.1 |
| TF-IDF + red densa (entregado) | isotónica | 0.086 [0.053, 0.130] | 0.103 | 902 (± 55) | 40.6 / 1.9 | 876 | 41.4 / 1.7 |
| Regresión logística (referencia) | sin calibrar | 0.132 [0.114, 0.179] | 0.112 | 575 (± 108) | 35.9 / 0.2 | 1,920 | 128.0 / 0.0 |
| Regresión logística (referencia) | Platt | 0.062 [0.049, 0.113] | 0.095 | 556 (± 78) | 34.6 / 0.2 | 635 | 42.4 / 0.0 |
| Regresión logística (referencia) | isotónica | 0.038 [0.027, 0.087] | 0.095 | 638 (± 33) | 32.0 / 1.1 | 518 | 32.5 / 0.2 |
| LSTM con embeddings propios (alternativa) | sin calibrar | 0.248 [0.193, 0.306] | 0.243 | 1,300 (± 57) | 64.7 / 2.2 | 1,395 | 63.0 / 3.0 |
| LSTM con embeddings propios (alternativa) | Platt | 0.028 [0.030, 0.097] | 0.138 | 1,269 (± 92) | 64.6 / 2.0 | 1,411 | 62.5 / 3.1 |
| LSTM con embeddings propios (alternativa) | isotónica | 0.059 [0.042, 0.119] | 0.143 | 1,299 (± 60) | 64.6 / 2.2 | 1,321 | 66.0 / 2.2 |
