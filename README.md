# Lab&Co - solution métier pour fluidifier les relations entre chercheurs et administration

## A propos de Lab&Co

Lab&Co est un progiciel permettant aux établissements de recherche ou d'enseignement et de recherche(universités, EPST, etc.) de fluidifier les relations entre les chercheurs (porteurs de projets) et l'administration.

Il couvre notamment:

- Le recrutement de personnel sur contrat de projets (doctorants, bourses, CDD...)
- Les contrats de recherche (recherche partenariale, ANR, projets européens...)
- La valorisation de la recherche (logiciels, brevets, bases de donnée...)

## Illustration

<img src="https://raw.githubusercontent.com/abilian/labandco/main/doc/illustration.png">

### Historique

Lab&Co est développé par [Abilian](http://www.abilian.com/) en partenariat avec [Will Strategy](https://willstrategy.com/) depuis 2014 pour l'Université Pierre et Marie Curie (UPMC), devenue depuis Sorbonne Université.

Il est utilisé par plusieurs centaines de chercheurs et la soixantaine de personnes travaillant à la DR&I (Direction de la Recherche et de l'Innovation).

La version du code que vous consultez actuellement est la version "3.0" de l'application, qui été déployée fin 2019 à Sorbonne Université.

### Votre projet

Lab&Co peut être déployé dans votre établissement, après connexion à son annuaire LDAP et adaptation des modèles et des workflows à vos processus métiers.

Contactez-nous à: [contact@abilian.com](mailto:contact@abilian.com) pour toute demande d'information.


## Développement

### Installer en 1 ligne

Si votre machine de développement est "raisonnablement" configurée, vous pouvez installer Lab&Co localement en une ligne avec la commande:

    ./install.py

De manière alternative, si vous avez [Poetry](https://poetry.eustace.io/) installé, vous pouvez tapper:

    poetry install


### Installer un environnement de développement

1) Créer et activer un virtualenv (Python 3.9 pour l'instant)

2) Installer Poetry <https://github.com/sdispater/poetry>

3) Dans `/etc/hosts`, faire pointer `labster.local` sur `localhost`.

4) Tapper:

        poetry install
        yarn --cwd front


### Comment développper

En mode développement, il suffit de lancer `flask devserver`.

Puis lancer le navigateur sur: http://labster.local:5000/

Pour lancer les tests: `pytest` ou mieux `tox`.

Il y d'autres commandes utiles, tapper juste `flask` pour avoir la
liste.


### BDD de prod

Créer une base Postgresql `labster`:

    createdb labster

puis:

    flask create-db


### Migrations

    flask db migrate
    flask db upgrade

Doc: http://alembic.zzzcomputing.com/en/latest/tutorial.html


### Tests

1) Tests unitaires:

        pytest
        yarn --cwd front run test:unit

2) Tests e2e:

        flask cypress
        flask testcafe

3) Pour tester manuellement en tant qu'un autre utilisateur, utiliser l'url
`backdoor/uid=xxx` (see blueprints/auth/cas.py).


#### Tester l'envoi de mails

Lancer

    python -m smtpd -n -c DebuggingServer localhost:1025

et dans `DevConfig`

    # MAIL_SUPPRESS_SEND = True
    MAIL_SUPPRESS_SEND = False
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025

Ainsi les mais envoyés seront affichés sur stdout.

Autre possibilité, mettre la variable que l'on veux changer (par rapport au défaut)
dans un fichier `.env` (similaire au fichier `.flaskenv` qui existe déjà).

Le fichier `.env` a priorité sur `.flaskenv`.

Pour les tests unitaires, voir la doc de [flask-mail](https://pythonhosted.org/Flask-Mail/).


## Architecture

L'application est constitué d'un backend en Python, utilisant notamment le framework Web Flask, l'ORM SQLAlchemy, et d'un front-end SPA en JavaScript utilisant le framework réactif Vuejs.

La communication entre front-end et back-end se fait soit en utilisant le paradigme REST (sans HATEOAS), soit le protocole JSON-RPC 2.0.

Le backend utilise également le framework Abilian-Core développé par Abilian. Il utilise également l'injection de dépendance grâce à la bibliothèque Injector (+ Flask-Injector).

L'authentification se fait en utilisant le protocole CAS implémenté par l'Université.

### Modèle de données (simplifié)

<img src="https://raw.githubusercontent.com/abilian/labandco/main/doc/model.png">



## FAQ

### L'application s'appelle-t-elle "Labster" ou "Lab&Co" ?

Le projet s'appelait initialement "Labster", d'où le nom encore donné au package principal et à certaines variables ou constantes. Il s'appelle à présent "Lab&Co".
