-- Create sample source tables for the dbt project
-- This script sets up the raw data that dbt will transform

-- 1. User Sessions Table
CREATE TABLE IF NOT EXISTS public.user_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    ip_address VARCHAR(45)
);

-- Insert sample data
INSERT INTO public.user_sessions (session_id, user_id, started_at, ended_at, ip_address) VALUES
('sess_001', 'user_001', '2024-02-15 09:00:00', '2024-02-15 09:45:00', '192.168.1.1'),
('sess_002', 'user_002', '2024-02-15 10:30:00', '2024-02-15 11:15:00', '192.168.1.2'),
('sess_003', 'user_001', '2024-02-15 14:00:00', '2024-02-15 14:30:00', '192.168.1.1'),
('sess_004', 'user_003', '2024-02-16 08:00:00', '2024-02-16 09:00:00', '192.168.1.3'),
('sess_005', 'user_002', '2024-02-16 11:00:00', '2024-02-16 12:30:00', '192.168.1.2'),
('sess_006', 'user_004', '2024-02-16 15:00:00', '2024-02-16 16:20:00', '192.168.1.4'),
('sess_007', 'user_001', '2024-02-17 09:00:00', '2024-02-17 10:00:00', '192.168.1.1')
ON CONFLICT (session_id) DO NOTHING;

-- 2. Model Requests Table
CREATE TABLE IF NOT EXISTS public.model_requests (
    request_id VARCHAR(50) PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    request_timestamp TIMESTAMP NOT NULL,
    response_time_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10, 6),
    status VARCHAR(20)
);

-- Insert sample data
INSERT INTO public.model_requests (request_id, session_id, model_name, request_timestamp, response_time_ms, tokens_used, cost_usd, status) VALUES
-- Session 1
('req_001', 'sess_001', 'gpt-4', '2024-02-15 09:05:00', 1200, 150, 0.0045, 'success'),
('req_002', 'sess_001', 'gpt-4', '2024-02-15 09:15:00', 1500, 200, 0.0060, 'success'),
('req_003', 'sess_001', 'gpt-3.5-turbo', '2024-02-15 09:30:00', 800, 100, 0.0002, 'success'),
-- Session 2
('req_004', 'sess_002', 'claude-3-opus', '2024-02-15 10:35:00', 2000, 300, 0.0045, 'success'),
('req_005', 'sess_002', 'claude-3-sonnet', '2024-02-15 10:50:00', 1100, 250, 0.00075, 'success'),
('req_006', 'sess_002', 'claude-3-sonnet', '2024-02-15 11:00:00', 5500, 280, 0.00084, 'timeout'),
-- Session 3
('req_007', 'sess_003', 'gpt-4-turbo', '2024-02-15 14:05:00', 900, 180, 0.0018, 'success'),
('req_008', 'sess_003', 'gpt-4-turbo', '2024-02-15 14:15:00', 1000, 220, 0.0022, 'success'),
-- Session 4
('req_009', 'sess_004', 'gemini-pro', '2024-02-16 08:15:00', 700, 120, 0.00003, 'success'),
('req_010', 'sess_004', 'gemini-pro', '2024-02-16 08:30:00', 650, 130, 0.000033, 'success'),
('req_011', 'sess_004', 'gemini-ultra', '2024-02-16 08:45:00', 1800, 250, 0.0025, 'success'),
-- Session 5
('req_012', 'sess_005', 'gpt-4', '2024-02-16 11:10:00', 1300, 190, 0.0057, 'success'),
('req_013', 'sess_005', 'gpt-4', '2024-02-16 11:30:00', 1400, 210, 0.0063, 'error'),
('req_014', 'sess_005', 'gpt-3.5-turbo', '2024-02-16 12:00:00', 750, 95, 0.00019, 'success'),
-- Session 6
('req_015', 'sess_006', 'claude-3-haiku', '2024-02-16 15:15:00', 500, 80, 0.00002, 'success'),
('req_016', 'sess_006', 'claude-3-haiku', '2024-02-16 15:30:00', 550, 90, 0.0000225, 'success'),
('req_017', 'sess_006', 'claude-3-opus', '2024-02-16 16:00:00', 2100, 320, 0.0048, 'success'),
-- Session 7
('req_018', 'sess_007', 'gpt-4-turbo', '2024-02-17 09:10:00', 950, 175, 0.00175, 'success'),
('req_019', 'sess_007', 'gpt-4-turbo', '2024-02-17 09:30:00', 1050, 195, 0.00195, 'success'),
('req_020', 'sess_007', 'gpt-4-turbo', '2024-02-17 09:50:00', 1100, 205, 0.00205, 'success')
ON CONFLICT (request_id) DO NOTHING;

-- 3. Model Feedback Table
CREATE TABLE IF NOT EXISTS public.model_feedback (
    feedback_id VARCHAR(50) PRIMARY KEY,
    request_id VARCHAR(50) NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    created_at TIMESTAMP NOT NULL
);

-- Insert sample data
INSERT INTO public.model_feedback (feedback_id, request_id, rating, feedback_text, created_at) VALUES
('fb_001', 'req_001', 5, 'Excellent response, very helpful!', '2024-02-15 09:06:00'),
('fb_002', 'req_002', 4, 'Good but could be faster', '2024-02-15 09:16:00'),
('fb_003', 'req_004', 5, 'Amazing quality of response', '2024-02-15 10:36:00'),
('fb_004', 'req_005', 4, NULL, '2024-02-15 10:51:00'),
('fb_005', 'req_006', 2, 'Too slow, timed out', '2024-02-15 11:01:00'),
('fb_006', 'req_007', 5, 'Very fast and accurate', '2024-02-15 14:06:00'),
('fb_007', 'req_009', 4, 'Good value for money', '2024-02-16 08:16:00'),
('fb_008', 'req_011', 3, 'OK but expensive', '2024-02-16 08:46:00'),
('fb_009', 'req_013', 1, 'Got an error, not helpful', '2024-02-16 11:31:00'),
('fb_010', 'req_015', 5, 'Super fast!', '2024-02-16 15:16:00'),
('fb_011', 'req_017', 4, 'Great quality', '2024-02-16 16:01:00'),
('fb_012', 'req_018', 5, 'Perfect response', '2024-02-17 09:11:00'),
('fb_013', 'req_020', 5, 'Exactly what I needed', '2024-02-17 09:51:00')
ON CONFLICT (feedback_id) DO NOTHING;

-- Verify data was inserted
SELECT 'user_sessions' as table_name, COUNT(*) as record_count FROM public.user_sessions
UNION ALL
SELECT 'model_requests', COUNT(*) FROM public.model_requests
UNION ALL
SELECT 'model_feedback', COUNT(*) FROM public.model_feedback;
