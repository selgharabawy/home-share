# Home Share API Django application

## Setup

- The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/selgharabawy/home-share.git ./home-share-api
$ cd home-share-api
```

- Project is dockerized

```sh
$ docker-compose run --rm sh -c "python manage.py createsuperuser"
```

## Project is dockerized

- To run project

```sh
$ docker-compose up
```

- To run tests

```sh
$ docker-compose run --rm sh -c "python manage.py test && flake8"
```

- To add new migrations

```sh
$ docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations"
$ docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"
```

- To create new apps:

```sh
$ docker-compose run --rm app sh -c "python manage.py startapp <new_app_name>"
```
