"""
Performance Monitor
Tracks response times, throughput, error rates, and resource usage.
"""

import time
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import deque, defaultdict
import statistics


@dataclass
class Metric:
    """Performance metric"""
    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)


class PerformanceMonitor:
    """Monitors performance metrics"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.response_times: deque = deque(maxlen=window_size)
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        self.start_time = time.time()
        self._metrics_history: List[Metric] = []
    
    def record_response_time(self, operation: str, duration: float, success: bool = True):
        """Record response time for an operation"""
        self.response_times.append({
            "operation": operation,
            "duration": duration,
            "success": success,
            "timestamp": time.time()
        })
        
        self.request_counts[operation] += 1
        if not success:
            self.error_counts[operation] += 1
        
        # Store as metric
        self._metrics_history.append(Metric(
            name="response_time",
            value=duration,
            tags={"operation": operation, "success": str(success)}
        ))
    
    def get_response_time_stats(self, operation: Optional[str] = None) -> Dict[str, float]:
        """Get response time statistics"""
        if not self.response_times:
            return {"avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}
        
        # Filter by operation if specified
        times = [r["duration"] for r in self.response_times 
                if operation is None or r["operation"] == operation]
        
        if not times:
            return {"avg": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}
        
        sorted_times = sorted(times)
        return {
            "avg": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "p50": statistics.median(times),
            "p95": sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 1 else sorted_times[0],
            "p99": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 1 else sorted_times[0]
        }
    
    def get_throughput(self, operation: Optional[str] = None) -> float:
        """Get requests per second"""
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        
        if operation:
            return self.request_counts[operation] / elapsed
        return sum(self.request_counts.values()) / elapsed
    
    def get_error_rate(self, operation: Optional[str] = None) -> float:
        """Get error rate (0-1)"""
        if operation:
            total = self.request_counts[operation]
            errors = self.error_counts[operation]
        else:
            total = sum(self.request_counts.values())
            errors = sum(self.error_counts.values())
        
        return errors / total if total > 0 else 0
    
    def get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        if not PSUTIL_AVAILABLE:
            return {
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "memory_percent": 0.0,
                "threads": 1
            }
        
        process = psutil.Process()
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "threads": process.num_threads()
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            "response_times": self.get_response_time_stats(),
            "throughput": self.get_throughput(),
            "error_rate": self.get_error_rate(),
            "resource_usage": self.get_resource_usage(),
            "total_requests": sum(self.request_counts.values()),
            "total_errors": sum(self.error_counts.values()),
            "uptime": time.time() - self.start_time
        }
    
    def export_metrics(self, format: str = "dict") -> Any:
        """Export metrics in specified format"""
        if format == "dict":
            return {
                "summary": self.get_metrics_summary(),
                "by_operation": {
                    op: {
                        "response_times": self.get_response_time_stats(op),
                        "throughput": self.get_throughput(op),
                        "error_rate": self.get_error_rate(op),
                        "total_requests": self.request_counts[op],
                        "total_errors": self.error_counts[op]
                    }
                    for op in self.request_counts.keys()
                }
            }
        elif format == "prometheus":
            return self._export_prometheus()
        return {}
    
    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []
        
        # Response times
        for op, count in self.request_counts.items():
            stats = self.get_response_time_stats(op)
            lines.append(f'response_time_avg{{operation="{op}"}} {stats["avg"]}')
            lines.append(f'response_time_p95{{operation="{op}"}} {stats["p95"]}')
        
        # Throughput
        for op in self.request_counts.keys():
            lines.append(f'throughput{{operation="{op}"}} {self.get_throughput(op)}')
        
        # Error rate
        for op in self.request_counts.keys():
            lines.append(f'error_rate{{operation="{op}"}} {self.get_error_rate(op)}')
        
        return "\n".join(lines)
    
    def reset(self):
        """Reset all metrics"""
        self.response_times.clear()
        self.error_counts.clear()
        self.request_counts.clear()
        self.start_time = time.time()
        self._metrics_history.clear()


class PerformanceDashboard:
    """Display performance metrics"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    def display(self):
        """Display performance dashboard"""
        summary = self.monitor.get_metrics_summary()
        
        print("=" * 70)
        print("PERFORMANCE DASHBOARD")
        print("=" * 70)
        
        # Response Times
        print("\n[Response Times]")
        rt = summary["response_times"]
        print(f"  Average: {rt['avg']:.3f}s")
        print(f"  Min: {rt['min']:.3f}s")
        print(f"  Max: {rt['max']:.3f}s")
        print(f"  P50: {rt['p50']:.3f}s")
        print(f"  P95: {rt['p95']:.3f}s")
        print(f"  P99: {rt['p99']:.3f}s")
        
        # Throughput
        print(f"\n[Throughput]")
        print(f"  Requests/sec: {summary['throughput']:.2f}")
        print(f"  Total requests: {summary['total_requests']}")
        
        # Error Rate
        print(f"\n[Error Rate]")
        print(f"  Error rate: {summary['error_rate']:.2%}")
        print(f"  Total errors: {summary['total_errors']}")
        
        # Resource Usage
        print(f"\n[Resource Usage]")
        ru = summary["resource_usage"]
        print(f"  CPU: {ru['cpu_percent']:.1f}%")
        print(f"  Memory: {ru['memory_mb']:.1f} MB ({ru['memory_percent']:.1f}%)")
        print(f"  Threads: {ru['threads']}")
        
        # Uptime
        print(f"\n[Uptime]")
        print(f"  {summary['uptime']:.1f} seconds")
        
        print("=" * 70)
    
    def display_by_operation(self):
        """Display metrics by operation"""
        metrics = self.monitor.export_metrics()
        
        print("\n" + "=" * 70)
        print("METRICS BY OPERATION")
        print("=" * 70)
        
        for op, data in metrics["by_operation"].items():
            print(f"\n[{op}]")
            print(f"  Requests: {data['total_requests']}")
            print(f"  Errors: {data['total_errors']}")
            print(f"  Error rate: {data['error_rate']:.2%}")
            print(f"  Throughput: {data['throughput']:.2f} req/s")
            print(f"  Avg response: {data['response_times']['avg']:.3f}s")
            print(f"  P95 response: {data['response_times']['p95']:.3f}s")
    
    def check_alerts(self) -> List[str]:
        """Check for performance issues"""
        alerts = []
        summary = self.monitor.get_metrics_summary()
        
        # High error rate
        if summary["error_rate"] > 0.1:
            alerts.append(f"⚠️  High error rate: {summary['error_rate']:.2%}")
        
        # Slow response times
        if summary["response_times"]["p95"] > 1.0:
            alerts.append(f"⚠️  Slow P95 response time: {summary['response_times']['p95']:.3f}s")
        
        # High memory usage
        if summary["resource_usage"]["memory_percent"] > 80:
            alerts.append(f"⚠️  High memory usage: {summary['resource_usage']['memory_percent']:.1f}%")
        
        # High CPU usage
        if summary["resource_usage"]["cpu_percent"] > 80:
            alerts.append(f"⚠️  High CPU usage: {summary['resource_usage']['cpu_percent']:.1f}%")
        
        return alerts


# Global monitor instance
_global_monitor = PerformanceMonitor()


def get_monitor() -> PerformanceMonitor:
    """Get global monitor instance"""
    return _global_monitor
