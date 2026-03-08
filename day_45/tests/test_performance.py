"""
Tests for Performance Monitor
"""

import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'utils'))

from performance import PerformanceMonitor, PerformanceDashboard, get_monitor


def test_response_time_tracking():
    """Test response time tracking"""
    print("\n=== Test: Response Time Tracking ===")
    
    monitor = PerformanceMonitor()
    
    # Record some response times
    monitor.record_response_time("query_db", 0.1, success=True)
    monitor.record_response_time("query_db", 0.2, success=True)
    monitor.record_response_time("query_db", 0.15, success=True)
    
    stats = monitor.get_response_time_stats("query_db")
    
    assert stats["avg"] > 0
    assert stats["min"] == 0.1
    assert stats["max"] == 0.2
    print(f"✓ Response times tracked: avg={stats['avg']:.3f}s")


def test_throughput_monitoring():
    """Test throughput monitoring"""
    print("\n=== Test: Throughput Monitoring ===")
    
    monitor = PerformanceMonitor()
    
    # Record requests
    for i in range(10):
        monitor.record_response_time("api_call", 0.01, success=True)
    
    time.sleep(0.1)  # Small delay
    throughput = monitor.get_throughput("api_call")
    
    assert throughput > 0
    print(f"✓ Throughput: {throughput:.2f} req/s")


def test_error_rate_tracking():
    """Test error rate tracking"""
    print("\n=== Test: Error Rate Tracking ===")
    
    monitor = PerformanceMonitor()
    
    # Record successes and failures
    monitor.record_response_time("operation", 0.1, success=True)
    monitor.record_response_time("operation", 0.1, success=True)
    monitor.record_response_time("operation", 0.1, success=False)
    
    error_rate = monitor.get_error_rate("operation")
    
    assert 0.3 <= error_rate <= 0.4  # 1/3 ≈ 0.33
    print(f"✓ Error rate: {error_rate:.2%}")


def test_resource_usage():
    """Test resource usage monitoring"""
    print("\n=== Test: Resource Usage ===")
    
    monitor = PerformanceMonitor()
    
    usage = monitor.get_resource_usage()
    
    assert "cpu_percent" in usage
    assert "memory_mb" in usage
    assert "memory_percent" in usage
    assert "threads" in usage
    print(f"✓ Resource usage: CPU={usage['cpu_percent']:.1f}%, Memory={usage['memory_mb']:.1f}MB")


def test_metrics_summary():
    """Test metrics summary"""
    print("\n=== Test: Metrics Summary ===")
    
    monitor = PerformanceMonitor()
    
    # Generate some data
    for i in range(5):
        monitor.record_response_time("test_op", 0.1, success=True)
    
    summary = monitor.get_metrics_summary()
    
    assert "response_times" in summary
    assert "throughput" in summary
    assert "error_rate" in summary
    assert "resource_usage" in summary
    assert summary["total_requests"] == 5
    print("✓ Metrics summary generated")


def test_metrics_export():
    """Test metrics export"""
    print("\n=== Test: Metrics Export ===")
    
    monitor = PerformanceMonitor()
    
    # Generate data
    monitor.record_response_time("op1", 0.1, success=True)
    monitor.record_response_time("op2", 0.2, success=True)
    
    # Export as dict
    metrics = monitor.export_metrics(format="dict")
    
    assert "summary" in metrics
    assert "by_operation" in metrics
    assert "op1" in metrics["by_operation"]
    print("✓ Metrics exported as dict")
    
    # Export as Prometheus
    prom = monitor.export_metrics(format="prometheus")
    assert isinstance(prom, str)
    assert len(prom) > 0
    print("✓ Metrics exported as Prometheus format")


def test_dashboard_display():
    """Test dashboard display"""
    print("\n=== Test: Dashboard Display ===")
    
    monitor = PerformanceMonitor()
    
    # Generate data
    for i in range(10):
        monitor.record_response_time("test", 0.1 + i * 0.01, success=True)
    
    dashboard = PerformanceDashboard(monitor)
    
    # Should not raise exception
    dashboard.display()
    print("✓ Dashboard displayed")


def test_alerts():
    """Test performance alerts"""
    print("\n=== Test: Performance Alerts ===")
    
    monitor = PerformanceMonitor()
    dashboard = PerformanceDashboard(monitor)
    
    # Generate high error rate
    for i in range(10):
        monitor.record_response_time("failing_op", 0.1, success=False)
    
    alerts = dashboard.check_alerts()
    
    assert len(alerts) > 0
    print(f"✓ Alerts generated: {len(alerts)}")


def test_percentiles():
    """Test percentile calculations"""
    print("\n=== Test: Percentiles ===")
    
    monitor = PerformanceMonitor()
    
    # Record times from 0.1 to 1.0
    for i in range(100):
        monitor.record_response_time("test", 0.01 * (i + 1), success=True)
    
    stats = monitor.get_response_time_stats("test")
    
    assert stats["p50"] > 0
    assert stats["p95"] > stats["p50"]
    assert stats["p99"] > stats["p95"]
    print(f"✓ Percentiles: P50={stats['p50']:.3f}, P95={stats['p95']:.3f}, P99={stats['p99']:.3f}")


def test_global_monitor():
    """Test global monitor instance"""
    print("\n=== Test: Global Monitor ===")
    
    monitor = get_monitor()
    
    monitor.record_response_time("global_test", 0.1, success=True)
    
    stats = monitor.get_response_time_stats("global_test")
    assert stats["avg"] > 0
    print("✓ Global monitor working")


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("PERFORMANCE MONITOR - TEST SUITE")
    print("=" * 70)
    
    try:
        test_response_time_tracking()
        test_throughput_monitoring()
        test_error_rate_tracking()
        test_resource_usage()
        test_metrics_summary()
        test_metrics_export()
        test_dashboard_display()
        test_alerts()
        test_percentiles()
        test_global_monitor()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
