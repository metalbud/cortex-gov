#!/usr/bin/env python3
"""
Error Handling and Recovery System for Cortex GOV
Provides centralized error management, recovery mechanisms, and logging
"""

import json
import logging
import os
import sys
import traceback
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import subprocess


class ErrorHandler:
    """Centralized error handling and recovery for Cortex GOV components"""
    
    def __init__(self, log_dir: str = "artifacts/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self.setup_logging()
        
        # Error counters and statistics
        self.error_stats = {
            "total_errors": 0,
            "recoverable_errors": 0,
            "fatal_errors": 0,
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }
        
        # Recovery strategies registry
        self.recovery_strategies = {}
        self.register_default_strategies()
        
    def setup_logging(self):
        """Setup comprehensive logging configuration"""
        log_file = self.log_dir / f"error_handler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("ErrorHandler")
        self.logger.info("ErrorHandler initialized")
    
    def register_default_strategies(self):
        """Register default recovery strategies"""
        # File system errors
        self.register_strategy("file_not_found", self.recover_file_not_found)
        self.register_strategy("permission_denied", self.recover_permission_denied)
        self.register_strategy("disk_full", self.recover_disk_full)
        
        # Network/Connection errors
        self.register_strategy("connection_failed", self.recover_connection_failed)
        self.register_strategy("timeout", self.recover_timeout)
        
        # Configuration errors
        self.register_strategy("config_invalid", self.recover_config_invalid)
        self.register_strategy("missing_dependency", self.recover_missing_dependency)
        
        # Process errors
        self.register_strategy("process_failed", self.recover_process_failed)
        self.register_strategy("memory_exhausted", self.recover_memory_exhausted)
    
    def register_strategy(self, error_type: str, strategy_func):
        """Register a recovery strategy for a specific error type"""
        self.recovery_strategies[error_type] = strategy_func
        self.logger.info(f"Registered recovery strategy for: {error_type}")
    
    def handle_error(self, 
                    error: Exception, 
                    context: Dict[str, Any] = None, 
                    error_type: str = None,
                    recovery_attempt: int = 0,
                    max_attempts: int = 3) -> Dict[str, Any]:
        """
        Handle an error with potential recovery
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            error_type: Type of error (auto-detected if not provided)
            recovery_attempt: Current attempt number for recovery
            max_attempts: Maximum recovery attempts
            
        Returns:
            Dict with error details and recovery status
        """
        self.error_stats["total_errors"] += 1
        
        # Auto-detect error type if not provided
        if error_type is None:
            error_type = self.detect_error_type(error)
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": str(error),
            "error_class": error.__class__.__name__,
            "traceback": traceback.format_exc(),
            "context": context or {},
            "recovery_attempt": recovery_attempt,
            "max_attempts": max_attempts
        }
        
        self.logger.error(f"Error occurred: {error_info}")
        
        # Check if error is recoverable
        if self.is_recoverable(error_type) and recovery_attempt < max_attempts:
            return self.attempt_recovery(error_info)
        else:
            self.error_stats["fatal_errors"] += 1
            return {
                **error_info,
                "status": "fatal",
                "recovery_successful": False,
                "message": "Error is not recoverable or max attempts reached"
            }
    
    def detect_error_type(self, error: Exception) -> str:
        """Detect the type of error based on exception details"""
        error_str = str(error).lower()
        
        if "no such file" in error_str or "file not found" in error_str:
            return "file_not_found"
        elif "permission denied" in error_str or "access denied" in error_str:
            return "permission_denied"
        elif "disk full" in error_str or "no space left" in error_str:
            return "disk_full"
        elif "connection failed" in error_str or "connection refused" in error_str:
            return "connection_failed"
        elif "timeout" in error_str:
            return "timeout"
        elif "invalid" in error_str and "config" in error_str:
            return "config_invalid"
        elif "dependency" in error_str or "module not found" in error_str:
            return "missing_dependency"
        elif "process failed" in error_str or "subprocess" in error_str:
            return "process_failed"
        elif "memory" in error_str and "exhausted" in error_str:
            return "memory_exhausted"
        else:
            return "unknown"
    
    def is_recoverable(self, error_type: str) -> bool:
        """Check if an error type is recoverable"""
        return error_type in self.recovery_strategies
    
    def attempt_recovery(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to recover from an error"""
        self.error_stats["recovery_attempts"] += 1
        error_type = error_info["error_type"]
        
        try:
            self.logger.info(f"Attempting recovery for {error_type} (attempt {error_info['recovery_attempt'] + 1}/{error_info['max_attempts']})")
            
            # Get recovery strategy
            strategy_func = self.recovery_strategies.get(error_type)
            if strategy_func is None:
                return {
                    **error_info,
                    "status": "fatal",
                    "recovery_successful": False,
                    "message": "No recovery strategy available"
                }
            
            # Execute recovery strategy
            recovery_result = strategy_func(error_info)
            
            if recovery_result.get("success", False):
                self.error_stats["successful_recoveries"] += 1
                self.error_stats["recoverable_errors"] += 1
                
                return {
                    **error_info,
                    "status": "recovered",
                    "recovery_successful": True,
                    "recovery_message": recovery_result.get("message", "Recovery successful"),
                    "recovery_details": recovery_result
                }
            else:
                return {
                    **error_info,
                    "status": "retry_failed",
                    "recovery_successful": False,
                    "recovery_message": recovery_result.get("message", "Recovery failed"),
                    "recovery_details": recovery_result
                }
                
        except Exception as recovery_error:
            self.logger.error(f"Recovery attempt failed: {recovery_error}")
            return {
                **error_info,
                "status": "recovery_failed",
                "recovery_successful": False,
                "recovery_error": str(recovery_error)
            }
    
    # Recovery Strategy Implementations
    def recover_file_not_found(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for missing files"""
        context = error_info.get("context", {})
        file_path = context.get("file_path")
        
        if not file_path:
            return {"success": False, "message": "No file path provided in context"}
        
        try:
            # Try to create the file or directory
            path_obj = Path(file_path)
            
            # If the path has a suffix, treat it as a file. Otherwise, treat it as a directory.
            if path_obj.suffix or str(file_path).endswith(("/", "\\")):
                # Create parent directories and empty file
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                path_obj.touch(exist_ok=True)
                return {
                    "success": True, 
                    "message": f"Created missing file: {file_path}",
                    "action": "file_created"
                }
            else:
                # Create directory
                path_obj.mkdir(parents=True, exist_ok=True)
                return {
                    "success": True, 
                    "message": f"Created missing directory: {file_path}",
                    "action": "directory_created"
                }
                
        except Exception as e:
            return {
                "success": False, 
                "message": f"Failed to create missing file/directory: {e}",
                "action": "create_failed"
            }
    
    def recover_permission_denied(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for permission issues"""
        context = error_info.get("context", {})
        file_path = context.get("file_path")
        
        if not file_path:
            return {"success": False, "message": "No file path provided in context"}
        
        try:
            # Try to set appropriate permissions
            path_obj = Path(file_path)
            
            # For Windows, try to take ownership (requires admin)
            # For Unix-like, try chmod
            if sys.platform == "win32":
                # Windows permission recovery is limited without admin rights
                return {
                    "success": False, 
                    "message": "Windows permission recovery requires administrative privileges",
                    "action": "permission_recovery_failed"
                }
            else:
                # Unix-like systems: try to make file readable/writable
                os.chmod(file_path, 0o644)  # rw-r--r--
                return {
                    "success": True, 
                    "message": f"Set permissions on {file_path}",
                    "action": "permissions_set"
                }
                
        except Exception as e:
            return {
                "success": False, 
                "message": f"Failed to set permissions: {e}",
                "action": "permission_set_failed"
            }
    
    def recover_disk_full(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for disk full errors"""
        # Limited recovery options for disk full
        return {
            "success": False, 
            "message": "Disk full requires manual intervention - free up space",
            "action": "manual_intervention_required"
        }
    
    def recover_connection_failed(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for connection failures"""
        context = error_info.get("context", {})
        retry_count = context.get("retry_count", 0)
        max_retries = context.get("max_retries", 3)
        delay = context.get("delay", 2)
        
        if retry_count >= max_retries:
            return {
                "success": False, 
                "message": f"Connection failed after {max_retries} attempts",
                "action": "max_retries_exceeded"
            }
        
        # Wait before retry (simulated)
        time.sleep(delay)
        
        return {
            "success": True, 
            "message": f"Connection retry prepared (attempt {retry_count + 1})",
            "action": "retry_prepared",
            "next_retry": retry_count + 1
        }
    
    def recover_timeout(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for timeout errors"""
        context = error_info.get("context", {})
        timeout = context.get("timeout", 30)
        
        # Suggest increasing timeout
        new_timeout = timeout * 1.5
        
        return {
            "success": True, 
            "message": f"Suggest increasing timeout from {timeout}s to {new_timeout}s",
            "action": "timeout_adjustment",
            "recommended_timeout": new_timeout
        }
    
    def recover_config_invalid(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for invalid configuration"""
        context = error_info.get("context", {})
        config_file = context.get("config_file")
        
        if not config_file:
            return {"success": False, "message": "No config file provided in context"}
        
        try:
            # Create a backup of the invalid config
            path_obj = Path(config_file)
            backup_path = f"{config_file}.backup.{int(time.time())}"
            
            if path_obj.exists():
                path_obj.rename(backup_path)
            
            # Create a minimal valid config
            minimal_config = {"version": "1.0", "enabled": True}
            
            with open(config_file, 'w') as f:
                json.dump(minimal_config, f, indent=2)
            
            return {
                "success": True, 
                "message": f"Created minimal config at {config_file} (backup saved to {backup_path})",
                "action": "config_reset",
                "backup_file": backup_path
            }
            
        except Exception as e:
            return {
                "success": False, 
                "message": f"Failed to reset config: {e}",
                "action": "config_reset_failed"
            }
    
    def recover_missing_dependency(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for missing dependencies"""
        context = error_info.get("context", {})
        dependency = context.get("dependency")
        
        if not dependency:
            return {"success": False, "message": "No dependency specified in context"}
        
        try:
            # Try to install the dependency using pip
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", dependency],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "success": True, 
                    "message": f"Successfully installed dependency: {dependency}",
                    "action": "dependency_installed"
                }
            else:
                return {
                    "success": False, 
                    "message": f"Failed to install dependency: {result.stderr}",
                    "action": "dependency_install_failed"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False, 
                "message": f"Dependency installation timed out: {dependency}",
                "action": "dependency_install_timeout"
            }
        except Exception as e:
            return {
                "success": False, 
                "message": f"Failed to install dependency: {e}",
                "action": "dependency_install_error"
            }
    
    def recover_process_failed(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for process failures"""
        context = error_info.get("context", {})
        command = context.get("command")
        
        if not command:
            return {"success": False, "message": "No command provided in context"}
        
        try:
            # Try with more timeout and error handling
            timeout = context.get("timeout", 30)
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout * 2
            )
            
            if result.returncode == 0:
                return {
                    "success": True, 
                    "message": "Process succeeded with extended timeout",
                    "action": "process_succeeded",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False, 
                    "message": f"Process failed even with extended timeout: {result.stderr}",
                    "action": "process_failed_extended",
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False, 
                "message": f"Process timed out even with extended timeout ({timeout * 2}s)",
                "action": "process_timeout_extended"
            }
        except Exception as e:
            return {
                "success": False, 
                "message": f"Process recovery failed: {e}",
                "action": "process_recovery_error"
            }
    
    def recover_memory_exhausted(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery strategy for memory exhaustion"""
        # Suggest memory optimization strategies
        return {
            "success": True, 
            "message": "Recommend memory optimization: reduce batch sizes, increase memory limits, or optimize algorithms",
            "action": "memory_optimization_advice",
            "suggestions": [
                "Reduce batch processing sizes",
                "Implement streaming for large datasets",
                "Increase memory limits if possible",
                "Optimize data structures and algorithms"
            ]
        }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error handling statistics"""
        return self.error_stats.copy()
    
    def export_error_log(self, output_path: str = None) -> str:
        """Export error handling statistics and recent errors"""
        if output_path is None:
            output_path = self.log_dir / f"error_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.error_stats,
            "recovery_strategies": list(self.recovery_strategies.keys()),
            "log_directory": str(self.log_dir)
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Error statistics exported to: {output_path}")
        return output_path


def handle_error_decorator(error_handler: ErrorHandler):
    """Decorator to automatically handle errors using ErrorHandler"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Capture function context
                context = {
                    "function": func.__name__,
                    "args": str(args),
                    "kwargs": str(kwargs)
                }
                
                # Handle the error
                result = error_handler.handle_error(e, context)
                
                # If recovery was successful, we might want to retry
                if result["status"] == "recovered" and result["recovery_successful"]:
                    try:
                        return func(*args, **kwargs)
                    except Exception as retry_error:
                        # If retry fails, handle that error too
                        retry_result = error_handler.handle_error(retry_error, context, recovery_attempt=1)
                        return retry_result
                
                return result
        return wrapper
    return decorator


# Global error handler instance
_global_error_handler = None


def get_global_error_handler() -> ErrorHandler:
    """Get or create the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_global_error_handler(handler: ErrorHandler):
    """Set the global error handler instance"""
    global _global_error_handler
    _global_error_handler = handler


if __name__ == "__main__":
    # Example usage and testing
    handler = ErrorHandler()
    
    # Test file not found recovery
    try:
        open("nonexistent_file.txt", "r")
    except FileNotFoundError as e:
        result = handler.handle_error(e, {"file_path": "nonexistent_file.txt"})
        print(f"File not found recovery result: {result}")
    
    # Test connection failure recovery
    try:
        # Simulate connection failure
        raise ConnectionError("Connection failed")
    except ConnectionError as e:
        result = handler.handle_error(e, {"retry_count": 0, "max_retries": 3, "delay": 1})
        print(f"Connection failure recovery result: {result}")
    
    # Print error statistics
    print(f"Error statistics: {handler.get_error_stats()}")
    
    # Export error log
    export_path = handler.export_error_log()
    print(f"Error log exported to: {export_path}")