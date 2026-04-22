# 生产级监控和日志配置

# 日志配置
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        },
        "json": {
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "level": "ERROR"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file", "error_file"],
            "level": "INFO",
            "propagate": False
        },
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False
        }
    }
}

# 监控配置
MONITORING_CONFIG = {
    "metrics": {
        "enabled": True,
        "port": 8000,
        "path": "/metrics",
        "namespace": "athletics",
        "subsystem": "api"
    },
    "health_check": {
        "enabled": True,
        "path": "/health",
        "interval": 30,
        "timeout": 10
    },
    "tracing": {
        "enabled": False,
        "service_name": "athletics-api",
        "jaeger_endpoint": "http://jaeger:14268/api/traces"
    }
}

# 性能配置
PERFORMANCE_CONFIG = {
    "database": {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_recycle": 3600,
        "pool_pre_ping": True
    },
    "cache": {
        "enabled": True,
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "default_timeout": 3600
    },
    "security": {
        "rate_limit": {
            "requests_per_minute": 100,
            "burst_size": 10
        },
        "session_timeout": 1800,  # 30分钟
        "max_login_attempts": 5,
        "lockout_duration": 900  # 15分钟
    }
}

# 安全配置
SECURITY_CONFIG = {
    "jwt": {
        "algorithm": "HS256",
        "access_token_expire_minutes": 1440,
        "refresh_token_expire_days": 7
    },
    "password": {
        "min_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special": True
    },
    "cors": {
        "allow_origins": [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173"
        ],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"]
    }
}

# 备份配置
BACKUP_CONFIG = {
    "database": {
        "enabled": True,
        "schedule": "0 2 * * *",  # 每天凌晨2点
        "retention_days": 30,
        "compression": True
    },
    "logs": {
        "enabled": True,
        "schedule": "0 3 * * *",  # 每天凌晨3点
        "retention_days": 7
    }
}