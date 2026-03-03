"""
Security Validators Module

This module contains all validation logic for secure command execution,
including bash command syntax verification and semantic analysis.
"""

import subprocess
import bashlex
from typing import Tuple, List


def validate_bash_command(command: str) -> Tuple[bool, str]:
    """
    Comprehensive security check: Shellcheck + AST Analysis.
    
    Performs two-level validation:
    1. Static analysis with Shellcheck (syntax and style)
    2. Semantic analysis with bashlex (forbidden commands, dangerous patterns)
    
    Args:
        command: Bash command string to validate
        
    Returns:
        Tuple[bool, str]: (is_safe, report)
            - is_safe: True if command passed all checks, False if critical issues found
            - report: Detailed report of findings (warnings, errors, or success message)
    """
    report = []
    is_safe = True
    
    # --- 1. STATIC ANALYSIS (Shellcheck) ---
    try:
        process = subprocess.run(
            ['shellcheck', '-s', 'bash', '-'],
            input=command.encode(),
            capture_output=True,
            check=False,
            timeout=5
        )
        
        if process.returncode != 0:
            sc_output = process.stdout.decode()
            report.append(f"⚠️ **Shellcheck Issues:**\n{sc_output}")
            if "error:" in sc_output.lower():
                is_safe = False
    except FileNotFoundError:
        report.append("ℹ️ Shellcheck не установлен, пропуск синтаксического анализа.")
    except subprocess.TimeoutExpired:
        report.append("⚠️ Shellcheck timeout - команда может быть очень сложной.")

    # --- 2. SEMANTIC ANALYSIS (bashlex) ---
    try:
        parts = bashlex.parse(command)
        forbidden_commands = [
            'rm',       # Remove files
            'mkfs',     # Format filesystem
            'dd',       # Dangerous low-level copy
            'chmod',    # Change permissions on system
            'chown',    # Change ownership
            'mount',    # Mount filesystems
            'umount',   # Unmount filesystems
            'reboot',   # System reboot
            'shutdown', # System shutdown
            'init',     # Init system
            'halt',     # Halt system
        ]
        
        dangerous_patterns = {
            'sudo': "Использование 'sudo' требует явного подтверждения в ADR",
            '> /dev/sda': "Запись прямо на диск может быть деструктивной",
            '> /etc/': "Изменение системных конфигураций требует осторожности",
        }
        
        def check_node(node):
            nonlocal is_safe
            
            if node.kind == 'command':
                # Extract command name
                cmd_name = node.parts[0].word if hasattr(node.parts[0], 'word') else ""
                
                # Check against forbidden list
                if cmd_name in forbidden_commands:
                    report.append(f"❌ **CRITICAL:** Запрещена команда '{cmd_name}'!")
                    is_safe = False
                
                # Check for dangerous patterns
                for pattern, warning in dangerous_patterns.items():
                    if pattern in command:
                        report.append(f"⚠️ **WARNING:** {warning}")
                
                # Special check for sudo without restrictions
                if cmd_name == 'sudo':
                    report.append("⚠️ **SECURITY:** 'sudo' требует явного разрешения из ADR")
            
            # Recursively check nested elements
            if hasattr(node, 'parts'):
                for p in node.parts:
                    check_node(p)

        for part in parts:
            check_node(part)
            
    except Exception as e:
        report.append(f"⚠️ **AST Parsing:** Не удалось разобрать команду ({e})")
        # Don't block execution if parser fails on complex command

    # --- 3. FINAL REPORT ---
    final_report = "\n".join(report) if report else "✅ Команда прошла автоматическую проверку безопасности."
    return is_safe, final_report


def get_validation_summary(is_safe: bool, report: str) -> str:
    """
    Get a brief summary of validation results for logging.
    
    Args:
        is_safe: Validation result
        report: Detailed report from validate_bash_command
        
    Returns:
        str: Brief summary for logging
    """
    if is_safe:
        return "✅ VALIDATION PASSED"
    else:
        # Extract critical issues only for summary
        lines = report.split('\n')
        critical_lines = [l for l in lines if '❌ CRITICAL' in l or '⛔' in l]
        if critical_lines:
            return f"❌ VALIDATION FAILED: {critical_lines[0][:80]}"
        return "⚠️ VALIDATION WARNING"
