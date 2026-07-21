create database if not exists movie_tracker;
use movie_tracker;

create table if not exists users (
    id int auto_increment primary key,
    firstname varchar(100) not null, 
    lastname varchar(100),
    email varchar(100) not null unique,
    password_hash varchar(225) not null,
    created_at timestamp default current_timestamp,
    notifications boolean default false
);

create table if not exists franchises (
    id int auto_increment primary key,
    name varchar(100) not null unique
);

create table if not exists media_items (
    id int auto_increment primary key,
    tmdb_id int not null,
    franchise_id int not null,
    type enum('movie', 'tv') not null,
    category enum('main', 'extra') not null default 'main',
    title varchar(255) not null,
    release_data date null,
    foreign key (franchise_id) references franchises(id),
    unique key unique_tmdb_per_type (tmdb_id, type)
);

create table if not exists watched(
    user_id int not null,
    media_item_id int not null,
    watched_at timestamp default current_timestamp,
    primary key (user_id, media_item_id),
    foreign key (user_id) references users(id),
    foreign key (media_item_id) references media_items(id)
)

