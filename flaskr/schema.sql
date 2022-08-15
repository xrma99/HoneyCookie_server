DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS fakeuser;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS cookie;
DROP TABLE IF EXISTS fakeblogs;
-- Cookie is used to store cookies

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    legal INTEGER NOT NULL
);

CREATE TABLE fakeuser (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    legal INTEGER NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE cookie(
    session_id INTEGER PRIMARY KEY AUTOINCREMENT, -- session specific id
    user_id INTEGER NOT NULL,-- authentication Cookie
    user_name TEXT NOT NULL,
    honey_security TEXT NOT NULL,
    content TEXT,
    legal INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE fakeblogs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);