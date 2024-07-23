CREATE TABLE IF NOT EXISTS Users (
    id varchar(64) PRIMARY KEY,
    username varchar(64) 
);

CREATE TABLE IF NOT EXISTS Entities (
    uid varchar(64) PRIMARY KEY,
    created_at timestamp,
    updated_at timestamp,
    user_id varchar(64),
    description varchar(256),
    type varchar(16),
    status varchar(16),
    FOREIGN KEY (user_id) REFERENCES Users (id)
);
