CREATE TABLE anime(
    id integer primary key asc autoincrement,
    name text not null,
    startdate date not null,
    enddate date,
    company_id integer references anime_companys(id) on update cascade on delete cascade,
    episodes integer, 
    status text not null default "未看",
    unique (name, startdate) on conflict ignore
);
CREATE TABLE anime_alias(
    anime_id integer references anime(id) on update cascade on delete cascade,
    alias text not null,
    primary key(anime_id, alias)
);
CREATE TABLE anime_series(
    id integer not null,
    anime_id integer references anime(id) on update cascade on delete cascade,
    unique(id, anime_id)
);
CREATE TABLE anime_companys(
  id integer primary key asc autoincrement,
  name text not null unique
);
CREATE TABLE anime_file_patterns(
    anime_id integer references anime(id) on update cascade on delete cascade,
    pattern text not null unique
);
CREATE TABLE anime_comments(
    id integer primary key asc autoincrement,
    anime_id integer references anime(id) on update cascade on delete cascade,
    score integer default 80,
    comment text not null,
    timestamp timestamp not null default current_timestamp
);
CREATE TABLE anime_types(
    anime_id integer references anime(id) on update cascade on delete cascade,
    type text,
    unique(anime_id, type)
);
