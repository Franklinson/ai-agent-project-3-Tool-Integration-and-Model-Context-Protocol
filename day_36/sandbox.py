import docker
from docker.errors import DockerException, ContainerError, ImageNotFound
from resource_limiter import ResourceLimiter


class SandboxExecutor:
    def __init__(self, image="python:3.11-slim", timeout=30, memory_limit_mb=128, cpu_limit=0.5):
        self.image = image
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit = cpu_limit
        self.client = docker.from_env()
        self.container = None
        self.limiter = ResourceLimiter()
    
    def create_container(self):
        """Create a Docker container for code execution."""
        try:
            # Pull image if not available
            try:
                self.client.images.get(self.image)
            except ImageNotFound:
                self.client.images.pull(self.image)
            
            self.container = self.client.containers.create(
                self.image,
                command="sleep infinity",
                detach=True,
                mem_limit=f"{self.memory_limit_mb}m",
                cpu_quota=int(self.cpu_limit * 100000),
                cpu_period=100000,
                network_mode="none"
            )
            self.container.start()
            return {"success": True, "error": None}
        except DockerException as e:
            return {"success": False, "error": str(e)}
    
    def execute_in_container(self, code):
        """Execute code in the Docker container."""
        if not self.container:
            create_result = self.create_container()
            if not create_result["success"]:
                return {
                    "success": False,
                    "output": None,
                    "error": f"Container creation failed: {create_result['error']}",
                    "error_type": "ContainerError"
                }
        
        try:
            exit_code, output = self.container.exec_run(
                f"python -c '{code}'",
                demux=True,
                timeout=self.timeout
            )
            
            stdout = output[0].decode() if output[0] else ""
            stderr = output[1].decode() if output[1] else ""
            
            if exit_code == 0:
                return {
                    "success": True,
                    "output": stdout,
                    "error": None,
                    "error_type": None
                }
            else:
                return {
                    "success": False,
                    "output": stdout,
                    "error": stderr,
                    "error_type": "RuntimeError"
                }
        
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def get_resource_usage(self):
        """Get current resource usage of the container."""
        if not self.container:
            return {"success": False, "error": "No container running"}
        return self.limiter.monitor_resources(self.container)
    
    def update_limits(self, memory_mb=None, cpu_limit=None):
        """Update resource limits for running container."""
        if not self.container:
            return {"success": False, "error": "No container running"}
        
        results = {}
        if memory_mb is not None:
            results['memory'] = self.limiter.set_memory_limit(self.container, memory_mb)
        if cpu_limit is not None:
            results['cpu'] = self.limiter.set_cpu_limit(self.container, cpu_limit)
        
        return {"success": True, "results": results}
    
    def cleanup(self):
        """Stop and remove the container."""
        try:
            if self.container:
                self.container.stop(timeout=1)
                self.container.remove()
                self.container = None
            return {"success": True, "error": None}
        except DockerException as e:
            return {"success": False, "error": str(e)}
    
    def __enter__(self):
        self.create_container()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
