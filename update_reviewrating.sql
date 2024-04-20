UPDATE business AS b
SET reviewrating = (
    SELECT AVG(review_stars)
    FROM review AS r
    WHERE r.business_id = b.business_id
)
WHERE EXISTS (
    SELECT 1
    FROM review AS r
    WHERE r.business_id = b.business_id
);
