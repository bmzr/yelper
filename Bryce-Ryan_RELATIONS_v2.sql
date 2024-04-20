CREATE TABLE zipcodeData (
    zipcode VARCHAR(255),
    medianIncome INT,
    meanIncome INT,
    population INT,
    PRIMARY KEY (zipcode)
);

CREATE TABLE Business (
    business_id CHAR(22) PRIMARY KEY,
    name VARCHAR(255),
    address VARCHAR(255),
    state CHAR(2),
    city VARCHAR(255),
    zipcode VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    stars FLOAT,
    reviewcount INT,
    numCheckins INT,
    openStatus VARCHAR(5),
    reviewrating FLOAT DEFAULT 0.0,
    FOREIGN KEY (zipcode) REFERENCES zipcodeData(zipcode)
);

CREATE TABLE Checkins (
    business_id CHAR(22) NOT NULL,
    day VARCHAR(255),
    time CHAR(5),
    count INT,
    PRIMARY KEY (business_id, day, time),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE Attributes (
    business_id CHAR(22) NOT NULL,
    attr_name VARCHAR(255),
    value VARCHAR(255),
    PRIMARY KEY (business_id, attr_name),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE Categories (
    business_id CHAR(22) NOT NULL,
    category_name VARCHAR(255),
    PRIMARY KEY (business_id, category_name),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE Review (
    business_id CHAR(22) NOT NULL,
    review_id CHAR(22),
    review_stars INT,
    date DATE,
    text TEXT,
    useful_vote INT,
    funny_vote INT,
    cool_vote INT,
    PRIMARY KEY (business_id, review_id),
    FOREIGN KEY (business_id) REFERENCES Business(business_id)
);