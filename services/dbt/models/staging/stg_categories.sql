{{
    config(
        materialized='view',
        tags=['northwind', 'staging']
    )
}}

with source as (
    select * from {{ source('northwind', 'categories') }}
),

cleaned as (
    select
        -- Primary key
        category_id,
        
        -- Category information
        trim(category_name) as category_name,
        trim(description) as description,
        
        -- Metadata
        current_timestamp as loaded_at
        
    from source
)

select * from cleaned
