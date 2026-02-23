from code_executor import CodeExecutor
from sandbox import SandboxExecutor
from resource_limiter import ResourceLimiter


class CodeExecutionTool:
    """Complete code execution tool with validation, sandboxing, and resource limits."""
    
    def __init__(self, use_sandbox=True, memory_limit_mb=128, cpu_limit=0.5, timeout=30):
        self.use_sandbox = use_sandbox
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit = cpu_limit
        self.timeout = timeout
        self.code_executor = CodeExecutor(default_timeout=timeout)
    
    def execute(self, code, sandbox=None, timeout=None):
        """Execute code with optional sandboxing."""
        timeout = timeout or self.timeout
        
        # Validate syntax first
        validation = self.code_executor.validate_syntax(code)
        if not validation["valid"]:
            return {
                "success": False,
                "output": None,
                "error": validation["error"],
                "error_type": "SyntaxError",
                "sandboxed": False
            }
        
        # Execute in sandbox if enabled
        if self.use_sandbox or sandbox:
            return self._execute_sandboxed(code, timeout)
        else:
            result = self.code_executor.execute(code, timeout)
            result["sandboxed"] = False
            return result
    
    def _execute_sandboxed(self, code, timeout):
        """Execute code in sandboxed environment."""
        try:
            with SandboxExecutor(
                memory_limit_mb=self.memory_limit_mb,
                cpu_limit=self.cpu_limit,
                timeout=timeout
            ) as sandbox:
                result = sandbox.execute_in_container(code)
                result["sandboxed"] = True
                
                # Add resource usage if available
                usage = sandbox.get_resource_usage()
                if usage.get("success"):
                    result["resource_usage"] = {
                        "cpu_percent": usage["cpu_percent"],
                        "memory_mb": usage["memory_mb"]
                    }
                
                return result
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "error_type": type(e).__name__,
                "sandboxed": True
            }
    
    def execute_with_monitoring(self, code):
        """Execute code and return detailed resource monitoring."""
        if not self.use_sandbox:
            return {"error": "Monitoring requires sandbox mode"}
        
        try:
            with SandboxExecutor(
                memory_limit_mb=self.memory_limit_mb,
                cpu_limit=self.cpu_limit,
                timeout=self.timeout
            ) as sandbox:
                result = sandbox.execute_in_container(code)
                usage = sandbox.get_resource_usage()
                
                return {
                    "execution": result,
                    "resources": usage if usage.get("success") else None
                }
        except Exception as e:
            return {"error": str(e)}
    
    def update_limits(self, memory_mb=None, cpu_limit=None):
        """Update resource limits."""
        if memory_mb is not None:
            self.memory_limit_mb = memory_mb
        if cpu_limit is not None:
            self.cpu_limit = cpu_limit
        return {"success": True, "memory_mb": self.memory_limit_mb, "cpu_limit": self.cpu_limit}
