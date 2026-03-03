{{
    config(
        materialized='table',
        tags=['northwind', 'marts', 'analytics']
    )
}}

with employees as (
    select * from {{ ref('stg_employees') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

order_details as (
    select * from {{ ref('stg_order_details') }}
),

employee_sales as (
    select
        o.employee_id,
        count(distinct o.order_id) as total_orders,
        count(distinct o.customer_id) as unique_customers,
        sum(od.net_amount) as total_revenue,
        avg(od.net_amount) as avg_order_value,
        sum(od.quantity) as total_units_sold,
        min(o.order_date) as first_order_date,
        max(o.order_date) as most_recent_order_date,
        sum(case when o.is_shipped then 1 else 0 end) as orders_shipped,
        sum(case when o.is_late_shipment then 1 else 0 end) as late_shipments,
        avg(o.days_to_ship) as avg_days_to_ship
    from orders o
    join order_details od on o.order_id = od.order_id
    where o.employee_id is not null
    group by o.employee_id
),

final as (
    select
        e.employee_id,
        e.full_name,
        e.title,
        e.years_employed,
        e.city,
        e.country,
        
        -- Manager relationship
        e.manager_employee_id,
        m.full_name as manager_name,
        
        -- Sales performance
        coalesce(es.total_orders, 0) as total_orders,
        coalesce(es.unique_customers, 0) as unique_customers,
        coalesce(es.total_revenue, 0) as total_revenue,
        coalesce(es.avg_order_value, 0) as avg_order_value,
        coalesce(es.total_units_sold, 0) as total_units_sold,
        
        -- Performance per year of employment
        case
            when e.years_employed > 0
            then round(coalesce(es.total_revenue, 0)::numeric / e.years_employed::numeric, 2)
            else 0
        end as revenue_per_year_employed,
        
        -- Service quality
        es.orders_shipped,
        es.late_shipments,
        case
            when es.orders_shipped > 0
            then round((es.late_shipments::numeric / es.orders_shipped::numeric) * 100, 2)
            else 0
        end as late_shipment_rate_pct,
        es.avg_days_to_ship,
        
        -- Performance ranking
        row_number() over (order by es.total_revenue desc nulls last) as revenue_rank,
        row_number() over (order by es.total_orders desc nulls last) as orders_rank,
        
        -- Activity dates
        es.first_order_date,
        es.most_recent_order_date,
        
        current_timestamp as calculated_at
        
    from employees e
    left join employees m on e.manager_employee_id = m.employee_id
    left join employee_sales es on e.employee_id = es.employee_id
)

select * from final
order by total_revenue desc nulls last
