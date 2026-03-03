"""
Centralized Logging Module

This module provides a unified logging system for the Bloom Control Center.
Uses Python's standard logging module with configuration for multiple handlers
and log files (SSH logs, history logs, general application logs).
"""

import logging
import logging.handlers
import os
from app.config import LOGS_DIR


# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)


import re as _re

class SanitizedFormatter(logging.Formatter):
    """
    Custom formatter that sanitizes sensitive information from logs.
    Masks tokens, API keys, passwords and private key material before writing.
    """

    # Паттерны: (compiled_regex, replacement)
    _PATTERNS = [
        # GitHub/GitLab токены в URL: https://TOKEN@github.com
        (_re.compile(r'(https?://)([^@\s]{8,})(@)', _re.IGNORECASE),
         r'\1***MASKED_TOKEN***\3'),
        # key=VALUE или token=VALUE или password=VALUE (в URL или query string)
        (_re.compile(r'((?:key|token|password|secret|credential|api_key)\s*[=:]\s*)([^\s,&\'"]{6,})',
                     _re.IGNORECASE),
         r'\1***MASKED***'),
        # Длинные base64/hex строки (≥40 символов) — вероятные ключи/токены
        (_re.compile(r'\b([A-Za-z0-9+/=_\-]{40,})\b'),
         r'***MASKED_KEY***'),
        # BEGIN PRIVATE KEY / BEGIN RSA PRIVATE KEY блоки
        (_re.compile(r'-----BEGIN [A-Z ]+-----.*?-----END [A-Z ]+-----',
                     _re.DOTALL),
         r'***MASKED_PRIVATE_KEY***'),
    ]

    def format(self, record):
        """Sanitize sensitive data from log messages."""
        message = super().format(record)
        for pattern, replacement in self._PATTERNS:
            message = pattern.sub(replacement, message)
        return message


# ============================================================================
# LOGGER CONFIGURATION
# ============================================================================

def get_logger(name, log_file=None):
    """
    Get or create a logger with specified configuration.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional specific log file (default: app.log in LOGS_DIR)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    if not log_file:
        log_file = os.path.join(LOGS_DIR, "app.log")
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = SanitizedFormatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# SPECIALIZED LOGGERS
# ============================================================================

class SSHLogger:
    """
    Specialized logger for SSH operations with structured logging format.
    """
    
    def __init__(self):
        self.logger = get_logger(
            'ssh',
            os.path.join(LOGS_DIR, 'ssh_audit.log')
        )
    
    def log_command_execution(self, username, command, output, exit_status, validation_status):
        """
        Log SSH command execution with full context.
        
        Args:
            username: SSH username
            command: Executed command
            output: Command output
            exit_status: Command exit code
            validation_status: Security validation result
        """
        status_marker = "SUCCESS" if exit_status == 0 else f"FAILED (code {exit_status})"
        
        log_message = (
            f"EXECUTION | USER: {username} | STATUS: {status_marker} | "
            f"VALIDATION: {validation_status} | CMD: {command[:100]}"
        )
        
        self.logger.info(log_message)
        
        # Log full output at DEBUG level
        if output:
            self.logger.debug(f"OUTPUT:\n{output[:1000]}")  # Log first 1000 chars
    
    def log_blocked_command(self, command, validation_report):
        """
        Log a command that was blocked due to security validation.
        
        Args:
            command: Blocked command
            validation_report: Detailed validation report
        """
        log_message = f"BLOCKED | CMD: {command[:100]}"
        self.logger.warning(log_message)
        self.logger.warning(f"VALIDATION_REPORT:\n{validation_report[:500]}")
    
    def log_ssh_error(self, command, error, validation_status):
        """
        Log SSH connection or execution errors.
        
        Args:
            command: Command that was being executed
            error: Error message
            validation_status: Security validation result
        """
        log_message = (
            f"ERROR | CMD: {command[:100]} | "
            f"VALIDATION: {validation_status} | ERROR: {str(error)[:200]}"
        )
        self.logger.error(log_message)


class HistoryLogger:
    """
    Specialized logger for project action history.
    """
    
    def __init__(self):
        self.logger = get_logger(
            'history',
            os.path.join(LOGS_DIR, 'HISTORY.log')
        )
    
    def log_action(self, action_text):
        """
        Log a project action.
        
        Args:
            action_text: Description of the action
            
        Returns:
            str: Status message
        """
        try:
            self.logger.info(action_text)
            return "✅ Запись добавлена в HISTORY.log"
        except Exception as e:
            return f"❌ Ошибка записи лога: {str(e)}"
    
    def log_skill_installation(self, skill_name, status, details=""):
        """Log skill installation action."""
        log_message = f"SKILL_INSTALLATION | SKILL: {skill_name} | STATUS: {status}"
        if details:
            log_message += f" | DETAILS: {details}"
        self.logger.info(log_message)
    
    def log_git_operation(self, operation, files=None, message=""):
        """Log git operations."""
        log_message = f"GIT_OPERATION | TYPE: {operation}"
        if files:
            log_message += f" | FILES: {files}"
        if message:
            log_message += f" | MESSAGE: {message}"
        self.logger.info(log_message)


class ValidationLogger:
    """
    Specialized logger for validation events.
    """
    
    def __init__(self):
        self.logger = get_logger(
            'validation',
            os.path.join(LOGS_DIR, 'validation.log')
        )
    
    def log_validation(self, command, is_safe, report_summary):
        """
        Log command validation event.
        
        Args:
            command: Command being validated
            is_safe: Whether validation passed
            report_summary: Brief summary of validation result
        """
        status = "PASSED" if is_safe else "FAILED"
        log_message = (
            f"VALIDATION | STATUS: {status} | "
            f"CMD: {command[:100]} | SUMMARY: {report_summary[:150]}"
        )
        level = logging.INFO if is_safe else logging.WARNING
        self.logger.log(level, log_message)


class ApplicationLogger:
    """
    General application logger for other events.
    """
    
    def __init__(self):
        self.logger = get_logger(
            'app',
            os.path.join(LOGS_DIR, 'app.log')
        )
    
    def log_initialization(self, component, status, message=""):
        """Log component initialization."""
        log_message = f"INIT | COMPONENT: {component} | STATUS: {status}"
        if message:
            log_message += f" | MESSAGE: {message}"
        level = logging.INFO if status == "OK" else logging.ERROR
        self.logger.log(level, log_message)
    
    def log_error(self, component, error_message):
        """Log application error."""
        self.logger.error(f"ERROR | COMPONENT: {component} | ERROR: {error_message}")
    
    def log_info(self, message):
        """Log general information."""
        self.logger.info(message)


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

# Create singleton instances for easy access throughout the app
ssh_logger = SSHLogger()
history_logger = HistoryLogger()
validation_logger = ValidationLogger()
app_logger = ApplicationLogger()
