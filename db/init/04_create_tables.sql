-- Switch to the target database
\c boardgameanalytics_db

-- Create tables
CREATE TABLE game_details
(
    game_id       int PRIMARY KEY,
    title         text NOT NULL,
    description   text NOT NULL,
    release_year  int,
    avg_rating    real,
    bayes_rating  real,
    total_ratings int,
    std_ratings   real,
    min_players   int,
    max_players   int,
    min_playtime  int,
    max_playtime  int,
    min_age       int,
    weight        real,
    owned_copies  int,
    wishlist      int,
    kickstarter   bool,
    popularity    real GENERATED ALWAYS AS (LN(ABS((bayes_rating - 5.5) * total_ratings) + 1) *
                                            SIGN((bayes_rating - 5.5))) STORED
);

CREATE TABLE mechanic_details
(
    mechanic_id   int PRIMARY KEY,
    mechanic_name text NOT NULL
);

CREATE TABLE category_details
(
    category_id   int PRIMARY KEY,
    category_name text NOT NULL
);

CREATE TABLE artist_details
(
    artist_id   int PRIMARY KEY,
    artist_name text NOT NULL
);

CREATE TABLE publisher_details
(
    publisher_id   int PRIMARY KEY,
    publisher_name text NOT NULL
);

CREATE TABLE designer_details
(
    designer_id   int PRIMARY KEY,
    designer_name text NOT NULL
);

CREATE TABLE game_mechanic_link
(
    game_id     int,
    mechanic_id int,
    PRIMARY KEY (game_id, mechanic_id),
    CONSTRAINT fk_game_id
        FOREIGN KEY (game_id)
            REFERENCES game_details (game_id),
    CONSTRAINT fk_mech_id
        FOREIGN KEY (mechanic_id)
            REFERENCES mechanic_details (mechanic_id)
);

CREATE TABLE game_category_link
(
    game_id     int,
    category_id int,
    PRIMARY KEY (game_id, category_id),
    CONSTRAINT fk_game_id
        FOREIGN KEY (game_id)
            REFERENCES game_details (game_id),
    CONSTRAINT fk_cat_id
        FOREIGN KEY (category_id)
            REFERENCES category_details (category_id)
);

CREATE TABLE game_designer_link
(
    game_id     int,
    designer_id int,
    PRIMARY KEY (game_id, designer_id),
    CONSTRAINT fk_game_id
        FOREIGN KEY (game_id)
            REFERENCES game_details (game_id),
    CONSTRAINT fk_cat_id
        FOREIGN KEY (designer_id)
            REFERENCES designer_details (designer_id)
);

CREATE TABLE game_artist_link
(
    game_id   int,
    artist_id int,
    PRIMARY KEY (game_id, artist_id),
    CONSTRAINT fk_game_id
        FOREIGN KEY (game_id)
            REFERENCES game_details (game_id),
    CONSTRAINT fk_cat_id
        FOREIGN KEY (artist_id)
            REFERENCES artist_details (artist_id)
);

CREATE TABLE game_publisher_link
(
    game_id      int,
    publisher_id int,
    PRIMARY KEY (game_id, publisher_id),
    CONSTRAINT fk_game_id
        FOREIGN KEY (game_id)
            REFERENCES game_details (game_id),
    CONSTRAINT fk_cat_id
        FOREIGN KEY (publisher_id)
            REFERENCES publisher_details (publisher_id)
);
