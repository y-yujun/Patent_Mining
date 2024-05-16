-- select grantees with their patents in the state Illinois

SELECT g.name, p.document_number, p.title_of_invention
FROM patents p
INNER JOIN grantees g ON p.document_number=g.document_number
WHERE g.state="IL"
ORDER BY p.document_number ASC;