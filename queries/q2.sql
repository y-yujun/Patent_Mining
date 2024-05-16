-- select universities which were granted at least a patent

SELECT DISTINCT name 
FROM grantees
WHERE country = 'US' AND (name LIKE '%University%' OR name LIKE '%College%') 
ORDER BY name ASC;