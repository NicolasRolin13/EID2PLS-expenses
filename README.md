
## Pré-requis (trouver sur internet comment les installer)

1. pip
2. docker

## Installation

Dans un terminal à la racine du projet (là ou se trouve ce readme) :

Si votre dossier Skeleton est vide :
$ git submodule update --init --recursive

Puis :

$ pip install -r requirements/base_requirements.txt
(pour avoir les dépendances accessibles)

## Téléchargement des images et run

$ docker-compose build
$ docker-compose up web

regarder si vous trouvez un site sur l'adresse http://127.0.0.1:8000/
Il est conseillé de faire ça avant le cours, les images docker étant assez lourdes

Vous pouvez détruire les conteneurs dockers en tapant
$ docker compose down

si les images sont trop grosses, vous pouvez détruire les images autres que python et postgres,
qui peuvent être reconstruites sans téléchargement
("$docker images" pour avoir la liste, et "$docker rmi [nom_de_l_image]" pour détruire une image)