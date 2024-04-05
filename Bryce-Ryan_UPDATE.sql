UPDATE Business
SET numCheckins = (
    SELECT SUM(count)
    FROM Checkins
    WHERE Checkins.business_id = Business.business_id
);

UPDATE Business
SET reviewcount = (
    SELECT COUNT(*)
    FROM Review
    WHERE Review.business_id = Business.business_id
);

UPDATE Business
SET reviewrating = (
    SELECT AVG(review_stars)
    FROM Review
    WHERE Review.business_id = Business.business_id
);

