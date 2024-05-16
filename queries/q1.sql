-- select patent records with University of Illinois as grantee

SELECT g.name, p.document_number, p.document_date, p.title_of_invention
FROM patents p
INNER JOIN grantees g ON g.document_number = p.document_number
WHERE g.name LIKE '%University of Illinois%'
ORDER BY p.document_number ASC;