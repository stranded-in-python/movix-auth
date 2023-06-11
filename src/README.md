movix-auth это сервис аутентификации для онлайн-кинотеатра, разработанный с помощью [fast-api](https://fastapi.tiangolo.com/) (со слов менторов это было допустимо) и основанный на [архитектуре](https://fastapi-users.github.io/fastapi-users/11.0/configuration/overview/) fast-api-users. При билде происходит initial миграция для postgreSQL, реализованная с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/) и создание супер-юзера.

## Запуск

```sh
docker compose -f local.yml up -d --build
```

## Люди
 - [](Станислав - тимлид)
 - [](Виктор)
 - [](Сергей)


## Features
 - Регистрация, логин, взаимодействие с ролями и правами по restAPI.
 - Авторизация через JWT-токен. Блеклисты для токенов (redis).
 - Хеширование паролей с помощью passlib с легкозаменяемым алгоритмом хеширования.
 - Кеширование результатов http-запросов (redis).
 - Каптча.
    
