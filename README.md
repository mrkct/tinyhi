# LET20-Cutecchia-Marco  
* TinyHI
* Interprete Iterativo
* ANTLR + Python
* La grammatica si trova in `tinyhi/parser/TinyHi.g4`

* Le funzioni `parse` e `run` sono esposte anche direttamente dal modulo `tinyhi`. Basta fare `from tinyhi import parse, run`
* Le funzioni `parse` e `run` hanno un parametro opzionale `throw_errors` (default False) che se messo a True lancia delle eccezioni in caso di errori (in particolare `ParseError`, `ThreadError` e `ExecutionError`)
* È anche possibile eseguire un file direttamente facendo `python -m tinyhi NomeFile`

### Broadcasting
Gli operatori matematici binari `+-*/` supportano tutti il broadcasting, sia da destra che da sinistra. 
Il significato però cambia per gli operatori senza proprietà commutativa:

    1 - [1, 2, 3] != [1, 2, 3] - 1

Il risultato di `1 - [1, 2, 3]` è il vettore `[0, -1, -2]` mentre il risultato di `[1, 2, 3] - 1` è il vettore `[0, 1, 2]`. Stesso discorso si applica per l'operatore di divisione, che effettua la divisione tra interi.
