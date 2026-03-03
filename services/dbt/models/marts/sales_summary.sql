{{
    config(
        materialized='table',
        tags=['northwind', 'marts', 'analytics']
    )
}}

with orders as (
    select * from {{ ref('stg_orders') }}
),

order_details as (
    select * from {{ ref('stg_order_details') }}
),

daily_sales as (
    select
        o.order_date,
        extract(year from o.order_date) as year,
        extract(month from o.order_date) as month,
        extract(quarter from o.order_date) as quarter,
        to_char(o.order_date, 'Day') as day_of_week,
        
        -- Order counts
        count(distinct o.order_id) as total_orders,
        count(distinct o.customer_id) as unique_customers,
        
        -- Revenue metrics
        sum(od.gross_amount) as gross_revenue,
        sum(od.net_amount) as net_revenue,
        sum(od.discount_amount) as total_discounts,
        avg(od.net_amount) as avg_order_value,
        
        -- Units sold
        sum(od.quantity) as total_units_sold,
        avg(od.quantity) as avg_units_per_order,
        
        -- Shipping metrics
        sum(o.freight) as total_freight,
        avg(o.freight) as avg_freight_per_order,
        sum(case when o.is_shipped then 1 else 0 end) as orders_shipped,
        sum(case when o.is_late_shipment then 1 else 0 end) as late_shipments
        
    from orders o
    join order_details od on o.order_id = od.order_id
    where o.order_date is not null
    group by o.order_date
),

with_comparisons as (
    select
        *,
        
        -- Month-over-month growth
        lag(net_revenue) over (order by order_date) as previous_day_revenue,
        net_revenue - lag(net_revenue) over (order by order_date) as revenue_change,
        
        -- Running totals
        sum(net_revenue) over (
            partition by year, month
            order by order_date
            rows between unbounded preceding and current row
        ) as month_to_date_revenue,
        
        sum(net_revenue) over (
            partition by year
            order by order_date
            rows between unbounded preceding and current row
        ) as year_to_date_revenue
        
    from daily_sales
)

select * from with_comparisons
order by order_date desc
