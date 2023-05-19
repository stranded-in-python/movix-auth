CREATE SCHEMA IF NOT EXISTS users;

CREATE TABLE IF NOT EXISTS users.role (
    id      uuid PRIMARY KEY,
    name    VARCHAR NOT NULL
)

CREATE TABLE IF NOT EXISTS users.sensetive (
    id          uuid PRIMARY KEY,
    username    VARCHAR NOT NULL,
    email       VARCHAR NULL,
    first_name  VARCHAR NULL,
    last_name   VARCHAR NULL,
    password    VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS users.user_role (
    id          uuid PRIMARY KEY,
    user_id     uuid NOT NULL FOREIGN KEY id REFERENCES sensetive,
    role_id     uuid NOT NULL FOREIGN KEY id REFERENCES role,
--     start_at    TIMESTAMP with time zone NOT NULL,
--     stop_at     TIMESTAMP with time zone NULL
);
-- 1to1 или 1toM ? Какую модель стоит использовать
-- при учете ролей пользователей

CREATE TABLE IF NOT EXISTS users.sign_in_history (
    id uuid     PRIMARY KEY,
    user_id     uuid NOT NULL FOREIGN KEY id REFERENCES sensetive,
    user_agent  TEXT,
    sign_in_at  TIMESTAMP with time zone NOT NULL
);

CREATE TABLE IF NOT EXISTS users.refresh_token(
    id          uuid PRIMARY KEY,
    session_id  uuid NOT NULL FOREIGN KEY id REFERENCES sign_in_history
--     token       VARCHAR NOT NULL
)