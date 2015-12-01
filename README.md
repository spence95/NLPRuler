# NLPRuler
NLPRuler is a simple Python natural language processing program. It has simple rules using regex and NLTK to decide if a record is positive or negative of a certain trait.

##### Rules
Rules are classes that have the main method called run. Run accepts the record text, does some analysis, and returns true or false based on the logic you write in that class

##### Workers
Workers are classes that perform some sort of data extraction on the record text
