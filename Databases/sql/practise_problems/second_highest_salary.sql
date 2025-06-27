
-- question: Find the second highest salary without using LIMIT, OFFSET, or TOP.

-- what is limit - limiting the number of records
-- what is offset - skipping a number of records
-- what is top - limiting the number of records in the result set, TOP is not better than LIMIT — it's just a different syntax for the same goal.



-- [Solution ]
SELECT
    max(salary) AS SecondHighestSalary
FROM
    salary_info
WHERE
    salary < (SELECT max(salary) FROM salary_info)
;


-- [Solution]  using limit, offset
SELECT
    DISTINCT salary AS SecondHighestSalary
FROM
    salary_info
ORDER BY
    salary DESC
LIMIT 1 OFFSET 1
;



-- [Solution] using row_number
with inner_query AS (
    SELECT
        salary AS SecondHighestSalary,
        DENSE_RANK() OVER (ORDER BY salary DESC) AS RowNum
    FROM
        salary_info
)
SELECT
    SecondHighestSalary
FROM
    inner_query
WHERE
    RowNum = 2
;



