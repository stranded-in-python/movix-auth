## Что это?

movix-auth это сервис аутентификации для онлайн-кинотеатра, разработанный с помощью [fast-api](https://fastapi.tiangolo.com/) (со слов менторов это было допустимо) и основанный на [архитектуре fast-api-users](https://fastapi-users.github.io/fastapi-users/11.0/configuration/overview/).

## Что под капотом?
 - initial миграция для postgreSQL с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/)
 - Регистрация, логин, взаимодействие с ролями и правами по restAPI.
 - Авторизация через JWT-токен. Блеклисты для токенов (redis).
 - Хеширование паролей с помощью passlib с легкозаменяемым алгоритмом хеширования.
 - Кеширование результатов http-запросов (redis).

При билде происходит initial миграция для postgreSQL, реализованная с помощью [alembic](https://alembic.sqlalchemy.org/en/latest/) и создание супер-юзера.

## Как установить?

Инструкция по установке в [главном репозитории](https://github.com/stranded-in-python/movix)

## Люди
 - [Станислав](https://github.com/SBKubric)
 - [Виктор](https://github.com/Viktor-Gostyaikin)
 - [Сергей](https://github.com/dogbusiness)
