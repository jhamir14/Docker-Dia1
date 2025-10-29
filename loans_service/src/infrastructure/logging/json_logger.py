import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            data["user_id"] = record.user_id
        if hasattr(record, 'book_id'):
            data["book_id"] = record.book_id
        if hasattr(record, 'loan_id'):
            data["loan_id"] = record.loan_id
        if hasattr(record, 'duration_ms'):
            data["duration_ms"] = record.duration_ms
        if hasattr(record, 'http_status'):
            data["http_status"] = record.http_status
        if hasattr(record, 'http_method'):
            data["http_method"] = record.http_method
        if hasattr(record, 'url'):
            data["url"] = record.url
        if hasattr(record, 'attempt'):
            data["attempt"] = record.attempt
            
        # Add exception info if present
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(data, ensure_ascii=False)


def setup_json_logging(logger_name: str = "loans", level: int = logging.INFO) -> logging.Logger:
    """Setup JSON logging for the application"""
    logger = logging.getLogger(logger_name)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate logs
    
    return logger


# Global logger instance
logger = setup_json_logging()