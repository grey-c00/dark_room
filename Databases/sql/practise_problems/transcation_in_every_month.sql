-- question: Identify customers who made transactions in every month of the year.
-- table: transactions
-- schema: transaction_id, customer_id, transaction_date (dd-mm-yyyy), amount


-- [Solution]

WITH TransactionMonth AS (
    SELECT
        customer_id,
        MONTH(transaction_date) AS transaction_month,
    FROM
        transactions
),
customerWithEveryMonth AS (
    SELECT
        customer_id,
        COUNT(DISTINCT transaction_month) AS month_count
    FROM
        TransactionMonth
    GROUP BY
        customer_id
    HAVING
        COUNT(DISTINCT transaction_month) = 12
)
SELECT * FROM customerWithEveryMonth;



-- [Solution - 2]
SELECT
    customer_id
FROM
    transactions
GROUP BY
    customer_id
HAVING count(distinct MONTH(transaction_date)) = 12;