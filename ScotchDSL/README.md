# Setup
Scotch heavily relies on the ANTLR parser generator. 

Install the ANTLR4 python runtime:
```bash
pip install antlr4-python-runtime
```

Move to the Grammar directory and download the ANLR jar File:
```bash
wget https://www.antlr.org/download/antlr-4.7.2-complete.jar
```

Move to the Grammar directory and execute the following commands:
```bash
bash generateParser.sh
```
It generates the parser files and copies them to the translation directory where they are needed.
