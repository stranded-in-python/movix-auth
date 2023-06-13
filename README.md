## Что это?

Movix-auth - это сервис аутентификации, разработанный с помощью [fast-api](https://fastapi.tiangolo.com/), и основанный на [архитектуре fast-api-users](https://fastapi-users.github.io/fastapi-users/11.0/configuration/overview/).

![Alt text](./architecture.svg)
<img src="./architecture.svg">

## Что под капотом?

-   initial миграция для postgreSQL с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/)
-   Регистрация, логин, взаимодействие с ролями и правами по restAPI.
-   Авторизация через JWT-токен. Блеклисты для токенов (redis).
-   Хеширование паролей с помощью passlib с легкозаменяемым алгоритмом хеширования.
-   Кеширование результатов http-запросов (redis).

При билде происходит initial миграция для postgreSQL, реализованная с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/) и создание супер-юзера.

## Как установить dev-build?

Инструкция по установке в [главном репозитории](https://github.com/stranded-in-python/movix)

## Люди

-   [Станислав](https://github.com/SBKubric)
-   [Виктор](https://github.com/Viktor-Gostyaikin)
-   [Сергей](https://github.com/dogbusiness)
