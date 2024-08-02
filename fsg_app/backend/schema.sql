DROP TABLE IF EXISTS crimes;
DROP TABLE IF EXISTS crime_types;



-- --------------
-- Table crimes
-- Stores each crime and accompanying information
-- --------------
CREATE TABLE crimes(
    crime_id INTEGER PRIMARY KEY,
    crime_name TEXT NOT NULL,
    ors TEXT NOT NULL UNIQUE,
    ranking INTEGER,
    ranking_language TEXT,
    crime_type_id INTEGER,
    FOREIGN KEY (crime_type_id)
        REFERENCES crime_types
        ON DELETE CASCADE
);


-- --------------
-- Table crime_types
-- Stores crime types 
-- --------------
CREATE TABLE crime_types(
    crime_type_id INTEGER PRIMARY KEY,
    crime_type TEXT NOT NULL
);