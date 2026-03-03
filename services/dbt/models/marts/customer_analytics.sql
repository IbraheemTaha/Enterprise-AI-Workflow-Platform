{{
    config(
        materialized='table',
        tags=['northwind', 'marts', 'analytics']
    )
}}

with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

order_details as (
    select * from {{ ref('stg_order_details') }}
),

order_aggregates as (
    select
        o.customer_id,
        count(distinct o.order_id) as total_orders,
        sum(od.net_amount) as lifetime_revenue,
        avg(od.net_amount) as avg_order_value,
        sum(od.quantity) as total_items_purchased,
        min(o.order_date) as first_order_date,
        max(o.order_date) as most_recent_order_date,
        max(o.order_date) - min(o.order_date) as customer_lifespan_days,
        sum(case when o.is_shipped then 1 else 0 end) as orders_shipped,
        sum(case when o.is_late_shipment then 1 else 0 end) as late_shipments,
        avg(o.days_to_ship) as avg_days_to_ship
    from orders o
    join order_details od on o.order_id = od.order_id
    group by o.customer_id
),

final as (
    select
        c.customer_id,
        c.company_name,
        c.contact_name,
        c.city,
        c.country,
        
        -- Order metrics
        coalesce(oa.total_orders, 0) as total_orders,
        coalesce(oa.lifetime_revenue, 0) as lifetime_revenue,
        coalesce(oa.avg_order_value, 0) as avg_order_value,
        coalesce(oa.total_items_purchased, 0) as total_items_purchased,
        
        -- Dates
        oa.first_order_date,
        oa.most_recent_order_date,
        oa.customer_lifespan_days,
        
        -- Service quality
        oa.orders_shipped,
        oa.late_shipments,
        case
            when oa.orders_shipped > 0
            then round((oa.late_shipments::numeric / oa.orders_shipped::numeric) * 100, 2)
            else 0
        end as late_shipment_rate_pct,
        oa.avg_days_to_ship,
        
        -- Customer segmentation
        case
            when coalesce(oa.total_orders, 0) = 0 then 'No Orders'
            when oa.lifetime_revenue > 10000 then 'High Value'
            when oa.lifetime_revenue > 5000 then 'Medium Value'
            else 'Low Value'
        end as customer_segment,
        
        case
            when oa.most_recent_order_date >= current_date - interval '90 days' then 'Active'
            when oa.most_recent_order_date >= current_date - interval '180 days' then 'At Risk'
            when oa.most_recent_order_date is not null then 'Churned'
            else 'No Orders'
        end as customer_status,
        
        current_timestamp as calculated_at
        
    from customers c
    left join order_aggregates oa on c.customer_id = oa.customer_id
)

select * from final
