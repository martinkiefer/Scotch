wget https://www.antlr.org/download/antlr-4.7.2-complete.jar
java -jar ./antlr-4.7.2-complete.jar -Dlanguage=Python3 -no-listener -visitor functiondescription.g4
cp *.py ../Translation
