-- question: Calculate the 7-day moving average of sales for each product.
-- table: sales
-- schema: sale_id, product_id, sale_date (dd-mm-yyyy), amount

WITH SaleWithDate AS (
    SELECT
        product_id,
        sale_date,
        sum(amount) as total_amount
    FROM
        sales
    GROUP BY
        product_id,
        sale_date
),
FinalQuery AS (
    SELECT
      product_id,
      sale_date,
      AVG(total_amount) OVER (
        PARTITION BY product_id
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
      ) AS moving_avg_7d
    FROM sales_filled
    ORDER BY product_id, sales_date;
)
SELECT * FROM FinalQuery
;
