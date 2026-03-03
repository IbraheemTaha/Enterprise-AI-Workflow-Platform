{{
    config(
        materialized='view',
        tags=['northwind', 'staging']
    )
}}

with source as (
    select * from {{ source('northwind', 'employees') }}
),

cleaned as (
    select
        -- Primary key
        employee_id,
        
        -- Name
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        trim(first_name) || ' ' || trim(last_name) as full_name,
        
        -- Title
        trim(title) as title,
        trim(title_of_courtesy) as title_of_courtesy,
        
        -- Dates
        birth_date,
        hire_date,
        extract(year from age(current_date, hire_date)) as years_employed,
        extract(year from age(current_date, birth_date)) as age_years,
        
        -- Location
        trim(address) as address,
        trim(city) as city,
        trim(region) as region,
        trim(postal_code) as postal_code,
        trim(country) as country,
        
        -- Contact
        trim(home_phone) as home_phone,
        trim(extension) as extension,
        
        -- Organizational
        reports_to as manager_employee_id,
        
        -- Notes
        notes,
        
        -- Metadata
        current_timestamp as loaded_at
        
    from source
)

select * from cleaned
