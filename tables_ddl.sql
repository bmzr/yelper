CREATE TABLE Business (
    business_id CHAR(22),
    name VARCHAR(100) NOT NULL,
    address VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    review_count INT DEFAULT 0,
    PRIMARY KEY (business_id)
);

CREATE TABLE BusinessCategory (
    business_id CHAR(22),
    category VARCHAR(100),
    FOREIGN KEY (business_id) REFERENCES Business(business_id),
    PRIMARY KEY (category, business_id)
);

CREATE TABLE BusinessAttribute (
    business_id CHAR(22),
    attribute VARCHAR(100),
    FOREIGN KEY (business_id) REFERENCES Business(business_id),
    PRIMARY KEY (attribute, business_id)
);

CREATE TABLE Checkin (
    business_id CHAR(22),
    time INT,
    FOREIGN KEY (business_id) REFERENCES Business(business_id),
    PRIMARY KEY (business_id)
);

CREATE TABLE Review (
    review_id CHAR(22),
    user_id CHAR(22) NOT NULL,
    business_id CHAR(22) NOT NULL,
    stars INT NOT NULL,
    date CHAR(10) NOT NULL,
    text VARCHAR(10000) NOT NULL,
    useful INT DEFAULT 0,
    funny INT DEFAULT 0,
    cool INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES User(user_id),
    FOREIGN KEY (business_id) REFERENCES Business(business_id),
    PRIMARY KEY (review_id)
);

CREATE TABLE User (
    user_id CHAR(22),
    name VARCHAR(100) NOT NULL,
    review_count INT DEFAULT 0,
    yelping_since CHAR(10) NOT NULL,
    useful INT DEFAULT 0,
    funny INT DEFAULT 0,
    cool INT DEFAULT 0,
    fans INT DEFAULT 0,
    PRIMARY KEY (user_id)
);