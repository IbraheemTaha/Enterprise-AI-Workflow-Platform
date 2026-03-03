{{
    config(
        materialized='view',
        tags=['northwind', 'staging']
    )
}}

with source as (
    select * from {{ source('northwind', 'orders') }}
),

cleaned as (
    select
        -- Primary key
        order_id,
        
        -- Foreign keys
        customer_id,
        employee_id,
        ship_via as shipper_id,
        
        -- Order dates
        order_date,
        required_date,
        shipped_date,
        
        -- Shipping details
        freight,
        trim(ship_name) as ship_name,
        trim(ship_address) as ship_address,
        trim(ship_city) as ship_city,
        trim(ship_region) as ship_region,
        trim(ship_postal_code) as ship_postal_code,
        trim(ship_country) as ship_country,
        
        -- Business logic flags
        case
            when shipped_date is not null then true
            else false
        end as is_shipped,
        
        case
            when shipped_date is not null and shipped_date > required_date
            then true
            else false
        end as is_late_shipment,
        
        case
            when shipped_date is not null
            then shipped_date - order_date
            else null
        end as days_to_ship,
        
        -- Metadata
        current_timestamp as loaded_at
        
    from source
)

select * from cleaned
