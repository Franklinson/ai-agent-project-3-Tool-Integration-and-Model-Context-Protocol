import time


class ResourceLimiter:
    @staticmethod
    def set_cpu_limit(container, cpu_quota):
        """Set CPU limit for container (0.0 to 1.0 = 0% to 100%)."""
        try:
            container.update(cpu_quota=int(cpu_quota * 100000), cpu_period=100000)
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def set_memory_limit(container, limit_mb):
        """Set memory limit for container in MB."""
        try:
            container.update(mem_limit=f"{limit_mb}m")
            return {"success": True, "error": None}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def monitor_resources(container):
        """Monitor container resource usage."""
        try:
            stats = container.stats(stream=False)
            
            # CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Memory usage
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            memory_mb = memory_usage / (1024 * 1024)
            memory_percent = (memory_usage / memory_limit * 100) if memory_limit > 0 else 0.0
            
            return {
                "success": True,
                "cpu_percent": round(cpu_percent, 2),
                "memory_mb": round(memory_mb, 2),
                "memory_percent": round(memory_percent, 2),
                "error": None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def enforce_time_limit(func, timeout, *args, **kwargs):
        """Execute function with time limit."""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Execution exceeded {timeout} seconds")
        
        # Set alarm for timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # Cancel alarm
            return result
        except TimeoutError as e:
            return {"success": False, "error": str(e), "error_type": "TimeoutError"}
