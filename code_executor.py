import subprocess
import sys
import ast


class CodeExecutor:
    def __init__(self, default_timeout=30):
        self.default_timeout = default_timeout
    
    def validate_syntax(self, code):
        """Validate Python code syntax."""
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": f"Syntax error at line {e.lineno}: {e.msg}"}
    
    def execute(self, code, timeout=None):
        """Execute Python code with timeout and error handling."""
        if timeout is None:
            timeout = self.default_timeout
        
        # Validate syntax first
        validation = self.validate_syntax(code)
        if not validation["valid"]:
            return {
                "success": False,
                "output": None,
                "error": validation["error"],
                "error_type": "SyntaxError"
            }
        
        # Execute code
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "error": None,
                    "error_type": None
                }
            else:
                return {
                    "success": False,
                    "output": result.stdout,
                    "error": result.stderr,
                    "error_type": "RuntimeError"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": f"Execution timed out after {timeout} seconds",
                "error_type": "TimeoutError"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "error_type": type(e).__name__
            }
