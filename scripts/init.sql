-- 数据库初始化脚本
-- 创建必要的索引和优化

-- 为用户表创建索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- 为运动员表创建索引
CREATE INDEX IF NOT EXISTS idx_athletes_user_id ON athletes(user_id);
CREATE INDEX IF NOT EXISTS idx_athletes_student_id ON athletes(student_id);
CREATE INDEX IF NOT EXISTS idx_athletes_name ON athletes(name);
CREATE INDEX IF NOT EXISTS idx_athletes_gender ON athletes(gender);
CREATE INDEX IF NOT EXISTS idx_athletes_group ON athletes(group);

-- 为比赛表创建索引
CREATE INDEX IF NOT EXISTS idx_events_name ON events(name);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);

-- 为成绩表创建索引
CREATE INDEX IF NOT EXISTS idx_scores_athlete_id ON scores(athlete_id);
CREATE INDEX IF NOT EXISTS idx_scores_event_id ON scores(event_id);
CREATE INDEX IF NOT EXISTS idx_scores_score ON scores(score);
CREATE INDEX IF NOT EXISTS idx_scores_created_at ON scores(created_at);

-- 为考勤表创建索引
CREATE INDEX IF NOT EXISTS idx_attendance_athlete_id ON attendance(athlete_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);

-- 为通知表创建索引
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);

-- 创建复合索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_scores_athlete_event ON scores(athlete_id, event_id);
CREATE INDEX IF NOT EXISTS idx_attendance_athlete_date ON attendance(athlete_id, date);

-- 为用户登录记录创建索引
CREATE INDEX IF NOT EXISTS idx_login_logs_user_id ON login_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_login_logs_created_at ON login_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_login_logs_ip_address ON login_logs(ip_address);

-- 创建全文搜索索引（如果PostgreSQL版本支持）
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- CREATE INDEX IF NOT EXISTS idx_athletes_name_trgm ON athletes USING gin (name gin_trgm_ops);

-- 分析表以更新统计信息
ANALYZE;

-- 创建视图以简化常用查询
CREATE OR REPLACE VIEW athlete_stats AS
SELECT 
    a.id,
    a.name,
    a.student_id,
    a.gender,
    a.group,
    COUNT(DISTINCT s.event_id) as events_participated,
    COUNT(DISTINCT s.id) as total_scores,
    AVG(s.score) as average_score,
    MAX(s.score) as best_score,
    MIN(s.score) as worst_score
FROM athletes a
LEFT JOIN scores s ON a.id = s.athlete_id
GROUP BY a.id, a.name, a.student_id, a.gender, a.group;

CREATE OR REPLACE VIEW recent_activities AS
SELECT 
    'score' as activity_type,
    s.athlete_id,
    a.name as athlete_name,
    s.event_id,
    e.name as event_name,
    s.score,
    s.created_at
FROM scores s
JOIN athletes a ON s.athlete_id = a.id
JOIN events e ON s.event_id = e.id
UNION ALL
SELECT 
    'attendance' as activity_type,
    a.athlete_id,
    ath.name as athlete_name,
    a.id as event_id,
    'Attendance' as event_name,
    a.status,
    a.date as created_at
FROM attendance a
JOIN athletes ath ON a.athlete_id = ath.id
ORDER BY created_at DESC
LIMIT 100;

-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_user_last_login()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET last_login = NOW() WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trg_update_user_last_login
AFTER INSERT ON login_logs
FOR EACH ROW EXECUTE FUNCTION update_user_last_login();

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL,
    record_id INTEGER NOT NULL,
    old_data JSONB,
    new_data JSONB,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 创建审计触发器函数
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, record_id, new_data, user_id)
        VALUES (TG_TABLE_NAME, 'INSERT', NEW.id, to_jsonb(NEW), NEW.created_by);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, record_id, old_data, new_data, user_id)
        VALUES (TG_TABLE_NAME, 'UPDATE', NEW.id, to_jsonb(OLD), to_jsonb(NEW), NEW.updated_by);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, record_id, old_data, user_id)
        VALUES (TG_TABLE_NAME, 'DELETE', OLD.id, to_jsonb(OLD), OLD.deleted_by);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 为主要表启用审计
CREATE TRIGGER trg_audit_users
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER trg_audit_athletes
AFTER INSERT OR UPDATE OR DELETE ON athletes
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER trg_audit_events
AFTER INSERT OR UPDATE OR DELETE ON events
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER trg_audit_scores
AFTER INSERT OR UPDATE OR DELETE ON scores
FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- 创建存储过程以清理旧数据
CREATE OR REPLACE PROCEDURE cleanup_old_data()
LANGUAGE plpgsql
AS $$
BEGIN
    -- 清理30天前的登录日志
    DELETE FROM login_logs WHERE created_at < NOW() - INTERVAL '30 days';
    
    -- 清理90天前的审计日志
    DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';
    
    -- 清理已读的通知
    DELETE FROM notifications WHERE is_read = true AND created_at < NOW() - INTERVAL '7 days';
    
    -- 更新统计信息
    ANALYZE;
    
    RAISE NOTICE 'Cleanup completed';
END;
$$;

-- 创建定时任务（需要使用pg_cron扩展或外部调度器）
-- SELECT cron.schedule('0 2 * * *', $$CALL cleanup_old_data()$$);