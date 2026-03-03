{{
    config(
        materialized='view',
        tags=['northwind', 'staging']
    )
}}

with source as (
    select * from {{ source('northwind', 'order_details') }}
),

cleaned as (
    select
        -- Composite key (order_id + product_id)
        order_id,
        product_id,
        
        -- Pricing
        unit_price,
        quantity,
        discount,
        
        -- Calculated fields
        unit_price * quantity as gross_amount,
        unit_price * quantity * (1 - discount) as net_amount,
        unit_price * quantity * discount as discount_amount,
        
        -- Metadata
        current_timestamp as loaded_at
        
    from source
)

select * from cleaned
