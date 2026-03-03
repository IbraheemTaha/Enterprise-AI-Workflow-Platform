{{
    config(
        materialized='table',
        tags=['northwind', 'marts', 'analytics']
    )
}}

with products as (
    select * from {{ ref('stg_products') }}
),

categories as (
    select * from {{ ref('stg_categories') }}
),

order_details as (
    select * from {{ ref('stg_order_details') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

product_sales as (
    select
        od.product_id,
        count(distinct o.order_id) as times_ordered,
        count(distinct o.customer_id) as unique_customers,
        sum(od.quantity) as total_units_sold,
        sum(od.gross_amount) as gross_revenue,
        sum(od.net_amount) as net_revenue,
        sum(od.discount_amount) as total_discounts,
        avg(od.unit_price) as avg_selling_price,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date
    from order_details od
    join orders o on od.order_id = o.order_id
    group by od.product_id
),

final as (
    select
        p.product_id,
        p.product_name,
        c.category_name,
        
        -- Current inventory status
        p.unit_price as current_unit_price,
        p.units_in_stock,
        p.units_on_order,
        p.is_discontinued,
        p.needs_reorder,
        p.is_out_of_stock,
        
        -- Sales performance
        coalesce(ps.times_ordered, 0) as times_ordered,
        coalesce(ps.unique_customers, 0) as unique_customers,
        coalesce(ps.total_units_sold, 0) as total_units_sold,
        coalesce(ps.gross_revenue, 0) as gross_revenue,
        coalesce(ps.net_revenue, 0) as net_revenue,
        coalesce(ps.total_discounts, 0) as total_discounts,
        
        -- Pricing analysis
        ps.avg_selling_price,
        case
            when ps.avg_selling_price is not null
            then round(((p.unit_price::numeric - ps.avg_selling_price::numeric) / ps.avg_selling_price::numeric) * 100, 2)
            else 0
        end as price_change_pct,
        
        -- Revenue contribution
        round(
            (ps.net_revenue::numeric / sum(ps.net_revenue::numeric) over ()) * 100,
            2
        ) as revenue_contribution_pct,
        
        -- Performance ranking
        row_number() over (order by ps.net_revenue desc nulls last) as revenue_rank,
        row_number() over (order by ps.total_units_sold desc nulls last) as units_rank,
        
        -- Product lifecycle
        ps.first_order_date,
        ps.last_order_date,
        case
            when ps.last_order_date >= current_date - interval '90 days' then 'Active'
            when ps.last_order_date >= current_date - interval '180 days' then 'Declining'
            when ps.last_order_date is not null then 'Inactive'
            else 'Never Sold'
        end as product_lifecycle_stage,
        
        current_timestamp as calculated_at
        
    from products p
    left join categories c on p.category_id = c.category_id
    left join product_sales ps on p.product_id = ps.product_id
)

select * from final
order by net_revenue desc nulls last
