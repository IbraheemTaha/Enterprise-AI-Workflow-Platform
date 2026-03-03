{{
    config(
        materialized='view',
        tags=['northwind', 'staging']
    )
}}

with source as (
    select * from {{ source('northwind', 'customers') }}
),

cleaned as (
    select
        -- Primary key
        customer_id,
        
        -- Company information
        upper(trim(company_name)) as company_name,
        trim(contact_name) as contact_name,
        trim(contact_title) as contact_title,
        
        -- Location
        trim(address) as address,
        trim(city) as city,
        trim(region) as region,
        trim(postal_code) as postal_code,
        trim(country) as country,
        
        -- Contact details
        regexp_replace(phone, '[^0-9+-]', '', 'g') as phone_cleaned,
        phone as phone_original,
        fax,
        
        -- Metadata
        current_timestamp as loaded_at
        
    from source
)

select * from cleaned
