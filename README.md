# Sök Annonser API
Skapa separat virtual environment för projektet (Virtualenv, Conda)

## Installation och körning (rekommenderar starkt att skapa en virtualenv eller anaconda-env innan).

**OBS!** 
Om du ska utveckla i valuestore-modulen behöver du först checka ut den i sitt eget repo och följa instruktionerna i README.

När du står i projektets rot-katalog:

    $ pip install -r requirements.txt
    $ python setup.py develop
    $ export FLASK_APP=sokannonser
    $ export FLASK_ENV=development
    $ flask run

Gå till http://localhost:5000 för att testa med Swagger-API:et.

## Alternativt

Bygg en docker-image:

    $ sudo docker build -t sokannonser:latest .
    $ sudo docker run -d -p 80:8081 sokannonser

Gå till http://localhost:80 för att testa med Swagger-API:et.


## Miljövariabler

Det finns en rad miljövariabler som kan sättas som kontrollerar både Flask och själva Sök-Annonser-applikationen.

Default-värdena är satta i beskrivningen

### Applikationskonfiguration


    ES_HOST=localhost

Anger vilken Elasticsearch-host som ska användas.

    ES_PORT=9200
   
Väljer vilken port som användas för Elasticsearch

    ES_INDEX=platsannons
    
Elasticsearchindex som innehåller sökbara platsannonser

    ES_TAX_INDEX=taxonomy
    
Elasticsearchindex som innehåller taxonomins värdeförråd

### Flask

    FLASK_APP

Namnet på applikationen. Bör sättas till "sokannonser". (Se ovan)

    FLASK_ENV=production
    
Kan med fördel sättas till development under utveckling. Ändrar defaultvärdet för nästa parameter (FLASK_DEBUG) till True

    FLASK_DEBUG=False
   
Ger debugmeddelanden vid fel.

### Test

att köra unit/integration tester: 

    $ python3 -m pytest -svv -ra -m unit tests/
    $ python3 -m pytest -svv -ra -m integration tests/
    
### Test coverage
https://pytest-cov.readthedocs.io/en/latest/
python3 -m pytest -svv -ra -m unit --cov=. tests/

För att lägga till coverage i IntelliJ, gå till menyn IntelliJ IDEA/Preferences/
Välj menyn Tools/Python Integrated Tools och för Default test runner, välj py.test.
Högerklicka därefter på katalogen sokannonser-api/tests och välj "Run py.test with coverage"

