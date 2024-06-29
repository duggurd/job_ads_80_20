CREATE DATABASE ingestion;
\c ingestion;
CREATE SCHEMA finn;

CREATE TABLE finn.finn_job_ads__metadata
(
    finnkode VARCHAR(10) NOT NULL PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    occupation VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    latiude FLOAT,
    longitude FLOAT
);

CREATE TABLE finn.finn_job_ads__content
(
    finnkode VARCHAR(10) NOT NULL PRIMARY KEY,
    title VARCHAR(255),
    business VARCHAR(255),
    ad_content TEXT,
    keywords TEXT,
    location VARCHAR(255),
    business_area VARCHAR(255),
    occupation VARCHAR(255),
    occupation_type VARCHAR(255),
    due_date VARCHAR(255),
    created_at TIMESTAMP NOT NULL
);