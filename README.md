# LET20-Cutecchia-Marco  
* TinyHI
* Interprete Iterativo
* ANTLR + Python
* La grammatica si trova in [tinyhi/parser/TinyHi.g4](https://github.com/mapio-teaching/LET20-Cutecchia-Marco/blob/parser/tinyhi/parser/TinyHi.g4)
* Per i test sto usando `pytest`
* Le funzioni `parse` e `run` sono esposte anche direttamente dal modulo `tinyhi`. Basta fare `from tinyhi import parse, run`
* È anche possibile eseguire un file direttamente facendo `python -m tinyhi NomeFile`