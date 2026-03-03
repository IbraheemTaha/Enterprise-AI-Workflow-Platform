{{
    config(
        materialized='view',
        tags=['northwind', 'staging']
    )
}}

with source as (
    select * from {{ source('northwind', 'products') }}
),

cleaned as (
    select
        -- Primary key
        product_id,
        
        -- Foreign keys
        supplier_id,
        category_id,
        
        -- Product information
        trim(product_name) as product_name,
        trim(quantity_per_unit) as quantity_per_unit,
        
        -- Pricing and inventory
        unit_price,
        units_in_stock,
        units_on_order,
        reorder_level,
        
        -- Status flags
        case when discontinued = 1 then true else false end as is_discontinued,
        case when units_in_stock <= reorder_level then true else false end as needs_reorder,
        case when units_in_stock = 0 then true else false end as is_out_of_stock,
        
        -- Inventory health
        units_in_stock + units_on_order as total_available_units,
        
        -- Metadata
        current_timestamp as loaded_at
        
    from source
)

select * from cleaned
