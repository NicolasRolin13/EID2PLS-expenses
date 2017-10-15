
### continuous integration

## flake8

Flake8 est un checker de style : il vérifie que le code source vérifie 
certains critères de qualité de style de code (nombre de lignes, etc.)
Pour le lancer, faites 
$ flake8


## serveur d'integration

Lorsqu'un commit arrive, le serveur d'intégration et run des scripts selon le fichier qui le décrit (ici le circle.yaml)
Ce qui est fait classiquement, c'est de faire tourner les tests et flake8, et si les deux sont positifs, execute le script de deployment.

