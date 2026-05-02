import logging
import sys
import json

def setup_logging(log_level: str = "INFO"):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Simple JSON formatter
    class JSONFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "line": record.lineno
            }
            # Add extra fields if present
            if hasattr(record, 'extra_data'):
                log_data.update(record.extra_data)
            return json.dumps(log_data)
    
    logHandler = logging.StreamHandler(sys.stdout)
    formatter = JSONFormatter()
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    return logger