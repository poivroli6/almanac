"""
Performance Monitoring Dashboard

Provides real-time performance monitoring, metrics collection, and health checks.
"""

import time
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from flask import Flask, jsonify, render_template_string
from dash import html, dcc, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px

from .memory_manager import get_memory_profiler
from .query_optimizer import get_query_optimizer
from .cache_enhancer import EnhancedCache


@dataclass
class HealthStatus:
    """Health status for a system component."""
    component: str
    status: str  # 'healthy', 'warning', 'critical'
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]


@dataclass
class PerformanceMetrics:
    """Performance metrics container."""
    timestamp: datetime
    memory_mb: float
    query_count: int
    avg_query_time: float
    cache_hit_rate: float
    active_connections: int
    error_count: int


class PerformanceMonitor:
    """Real-time performance monitoring system."""
    
    def __init__(self, app: Flask, cache_manager: EnhancedCache = None):
        self.app = app
        self.cache_manager = cache_manager
        self.logger = logging.getLogger(__name__)
        
        # Monitoring data
        self.metrics_history: List[PerformanceMetrics] = []
        self.health_checks: List[HealthStatus] = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Performance thresholds
        self.thresholds = {
            'memory_warning_mb': 1024,
            'memory_critical_mb': 2048,
            'query_time_warning_s': 1.0,
            'query_time_critical_s': 5.0,
            'cache_hit_rate_warning': 50.0,
            'error_rate_warning': 5.0
        }
        
        # Initialize monitoring endpoints
        self._setup_monitoring_endpoints()
    
    def _setup_monitoring_endpoints(self):
        """Setup Flask monitoring endpoints."""
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint."""
            return jsonify(self.get_health_status())
        
        @self.app.route('/metrics')
        def get_metrics():
            """Get current performance metrics."""
            return jsonify(self.get_current_metrics())
        
        @self.app.route('/performance-history')
        def get_performance_history():
            """Get performance history."""
            return jsonify(self.get_metrics_history())
        
        @self.app.route('/cache-stats')
        def get_cache_stats():
            """Get cache statistics."""
            if self.cache_manager:
                return jsonify(self.cache_manager.get_cache_stats())
            return jsonify({'error': 'Cache manager not available'})
    
    def start_monitoring(self, interval: int = 30):
        """
        Start performance monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info(f"Performance monitoring started (interval: {interval}s)")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self, interval: int):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._collect_metrics()
                self._run_health_checks()
                
                # Clean up old data (keep last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history if m.timestamp >= cutoff_time
                ]
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(interval)
    
    def _collect_metrics(self):
        """Collect current performance metrics."""
        try:
            memory_profiler = get_memory_profiler()
            query_optimizer = get_query_optimizer()
            
            # Get memory stats
            memory_stats = memory_profiler.get_memory_stats()
            
            # Get query performance
            query_stats = query_optimizer.get_query_performance_stats(hours=1)
            
            # Get cache stats
            cache_stats = {}
            if self.cache_manager:
                cache_stats = self.cache_manager.get_cache_stats()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                memory_mb=memory_stats.process_memory_mb,
                query_count=query_stats.get('total_queries', 0),
                avg_query_time=query_stats.get('avg_execution_time', 0),
                cache_hit_rate=cache_stats.get('redis_hit_rate', 0),
                active_connections=0,  # Would need database connection monitoring
                error_count=0  # Would need error tracking
            )
            
            self.metrics_history.append(metrics)
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
    
    def _run_health_checks(self):
        """Run system health checks."""
        health_checks = []
        
        # Memory health check
        if self.metrics_history:
            latest_memory = self.metrics_history[-1].memory_mb
            if latest_memory > self.thresholds['memory_critical_mb']:
                status = 'critical'
                message = f"Critical memory usage: {latest_memory:.1f}MB"
            elif latest_memory > self.thresholds['memory_warning_mb']:
                status = 'warning'
                message = f"High memory usage: {latest_memory:.1f}MB"
            else:
                status = 'healthy'
                message = f"Memory usage normal: {latest_memory:.1f}MB"
            
            health_checks.append(HealthStatus(
                component='memory',
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={'memory_mb': latest_memory}
            ))
        
        # Query performance health check
        if self.metrics_history:
            latest_query_time = self.metrics_history[-1].avg_query_time
            if latest_query_time > self.thresholds['query_time_critical_s']:
                status = 'critical'
                message = f"Critical query time: {latest_query_time:.2f}s"
            elif latest_query_time > self.thresholds['query_time_warning_s']:
                status = 'warning'
                message = f"Slow queries: {latest_query_time:.2f}s"
            else:
                status = 'healthy'
                message = f"Query performance normal: {latest_query_time:.2f}s"
            
            health_checks.append(HealthStatus(
                component='queries',
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics={'avg_query_time': latest_query_time}
            ))
        
        # Cache health check
        if self.cache_manager:
            cache_stats = self.cache_manager.get_cache_stats()
            hit_rate = cache_stats.get('redis_hit_rate', 0)
            
            if hit_rate < self.thresholds['cache_hit_rate_warning']:
                status = 'warning'
                message = f"Low cache hit rate: {hit_rate:.1f}%"
            else:
                status = 'healthy'
                message = f"Cache performance good: {hit_rate:.1f}%"
            
            health_checks.append(HealthStatus(
                component='cache',
                status=status,
                message=message,
                timestamp=datetime.now(),
                metrics=cache_stats
            ))
        
        self.health_checks = health_checks
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self.health_checks:
            return {
                'status': 'unknown',
                'message': 'No health checks available',
                'components': []
            }
        
        # Determine overall status
        statuses = [check.status for check in self.health_checks]
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        return {
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'components': [asdict(check) for check in self.health_checks]
        }
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.metrics_history:
            return {'message': 'No metrics available'}
        
        latest = self.metrics_history[-1]
        return asdict(latest)
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance metrics history."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [
            asdict(m) for m in self.metrics_history 
            if m.timestamp >= cutoff_time
        ]
        return recent_metrics
    
    def create_performance_dashboard(self) -> html.Div:
        """Create a Dash performance monitoring dashboard."""
        
        dashboard_layout = html.Div([
            html.H1("Almanac Futures - Performance Dashboard", 
                   style={'textAlign': 'center', 'marginBottom': '30px'}),
            
            # Health Status Cards
            html.Div([
                html.Div(id='health-status-cards', className='row'),
            ], style={'marginBottom': '30px'}),
            
            # Performance Charts
            html.Div([
                html.Div([
                    dcc.Graph(id='memory-usage-chart'),
                ], className='col-md-6'),
                
                html.Div([
                    dcc.Graph(id='query-performance-chart'),
                ], className='col-md-6'),
            ], className='row', style={'marginBottom': '30px'}),
            
            html.Div([
                html.Div([
                    dcc.Graph(id='cache-performance-chart'),
                ], className='col-md-6'),
                
                html.Div([
                    html.H4("System Metrics"),
                    html.Div(id='system-metrics-table'),
                ], className='col-md-6'),
            ], className='row'),
            
            # Auto-refresh
            dcc.Interval(
                id='performance-interval',
                interval=30*1000,  # 30 seconds
                n_intervals=0
            ),
        ], style={'padding': '20px'})
        
        return dashboard_layout
    
    def register_dashboard_callbacks(self, app):
        """Register Dash callbacks for the performance dashboard."""
        
        @app.callback(
            [Output('health-status-cards', 'children'),
             Output('memory-usage-chart', 'figure'),
             Output('query-performance-chart', 'figure'),
             Output('cache-performance-chart', 'figure'),
             Output('system-metrics-table', 'children')],
            [Input('performance-interval', 'n_intervals')]
        )
        def update_performance_dashboard(n_intervals):
            """Update the performance dashboard."""
            
            # Health status cards
            health_status = self.get_health_status()
            health_cards = self._create_health_cards(health_status)
            
            # Performance charts
            memory_chart = self._create_memory_chart()
            query_chart = self._create_query_performance_chart()
            cache_chart = self._create_cache_performance_chart()
            
            # System metrics table
            metrics_table = self._create_metrics_table()
            
            return health_cards, memory_chart, query_chart, cache_chart, metrics_table
    
    def _create_health_cards(self, health_status: Dict[str, Any]) -> List[html.Div]:
        """Create health status cards."""
        cards = []
        
        status_colors = {
            'healthy': '#28a745',
            'warning': '#ffc107', 
            'critical': '#dc3545',
            'unknown': '#6c757d'
        }
        
        overall_status = health_status.get('status', 'unknown')
        cards.append(
            html.Div([
                html.H4("Overall Status"),
                html.H5(overall_status.title(), 
                       style={'color': status_colors.get(overall_status, '#6c757d')}),
                html.P(health_status.get('message', 'No status available'))
            ], className='col-md-3', style={
                'backgroundColor': '#f8f9fa',
                'padding': '15px',
                'margin': '5px',
                'borderRadius': '5px'
            })
        )
        
        for component in health_status.get('components', []):
            status = component.get('status', 'unknown')
            cards.append(
                html.Div([
                    html.H6(component.get('component', 'Unknown').title()),
                    html.P(component.get('message', 'No message'),
                           style={'color': status_colors.get(status, '#6c757d')}),
                    html.Small(component.get('timestamp', '')[:19])
                ], className='col-md-3', style={
                    'backgroundColor': '#f8f9fa',
                    'padding': '15px',
                    'margin': '5px',
                    'borderRadius': '5px'
                })
            )
        
        return cards
    
    def _create_memory_chart(self) -> go.Figure:
        """Create memory usage chart."""
        if not self.metrics_history:
            return go.Figure()
        
        times = [m.timestamp for m in self.metrics_history[-100:]]  # Last 100 points
        memory_values = [m.memory_mb for m in self.metrics_history[-100:]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=memory_values,
            mode='lines+markers',
            name='Memory Usage (MB)',
            line=dict(color='blue')
        ))
        
        # Add threshold lines
        fig.add_hline(y=self.thresholds['memory_warning_mb'], 
                     line_dash="dash", line_color="orange",
                     annotation_text="Warning Threshold")
        fig.add_hline(y=self.thresholds['memory_critical_mb'], 
                     line_dash="dash", line_color="red",
                     annotation_text="Critical Threshold")
        
        fig.update_layout(
            title="Memory Usage Over Time",
            xaxis_title="Time",
            yaxis_title="Memory (MB)",
            height=300
        )
        
        return fig
    
    def _create_query_performance_chart(self) -> go.Figure:
        """Create query performance chart."""
        if not self.metrics_history:
            return go.Figure()
        
        times = [m.timestamp for m in self.metrics_history[-100:]]
        query_times = [m.avg_query_time for m in self.metrics_history[-100:]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=query_times,
            mode='lines+markers',
            name='Avg Query Time (s)',
            line=dict(color='green')
        ))
        
        # Add threshold lines
        fig.add_hline(y=self.thresholds['query_time_warning_s'], 
                     line_dash="dash", line_color="orange",
                     annotation_text="Warning Threshold")
        fig.add_hline(y=self.thresholds['query_time_critical_s'], 
                     line_dash="dash", line_color="red",
                     annotation_text="Critical Threshold")
        
        fig.update_layout(
            title="Query Performance Over Time",
            xaxis_title="Time",
            yaxis_title="Average Query Time (seconds)",
            height=300
        )
        
        return fig
    
    def _create_cache_performance_chart(self) -> go.Figure:
        """Create cache performance chart."""
        if not self.metrics_history:
            return go.Figure()
        
        times = [m.timestamp for m in self.metrics_history[-100:]]
        cache_rates = [m.cache_hit_rate for m in self.metrics_history[-100:]]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times,
            y=cache_rates,
            mode='lines+markers',
            name='Cache Hit Rate (%)',
            line=dict(color='purple')
        ))
        
        # Add threshold line
        fig.add_hline(y=self.thresholds['cache_hit_rate_warning'], 
                     line_dash="dash", line_color="orange",
                     annotation_text="Warning Threshold")
        
        fig.update_layout(
            title="Cache Performance Over Time",
            xaxis_title="Time",
            yaxis_title="Cache Hit Rate (%)",
            height=300
        )
        
        return fig
    
    def _create_metrics_table(self) -> html.Div:
        """Create system metrics table."""
        if not self.metrics_history:
            return html.P("No metrics available")
        
        latest = self.metrics_history[-1]
        
        metrics_data = [
            ("Memory Usage", f"{latest.memory_mb:.1f} MB"),
            ("Query Count (1h)", str(latest.query_count)),
            ("Avg Query Time", f"{latest.avg_query_time:.3f} s"),
            ("Cache Hit Rate", f"{latest.cache_hit_rate:.1f}%"),
            ("Active Connections", str(latest.active_connections)),
            ("Error Count", str(latest.error_count)),
        ]
        
        table_rows = [
            html.Tr([
                html.Td(metric[0], style={'fontWeight': 'bold'}),
                html.Td(metric[1])
            ]) for metric in metrics_data
        ]
        
        return html.Table([
            html.Tbody(table_rows)
        ], className='table table-striped')


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """Get the global performance monitor instance."""
    return _performance_monitor


def init_performance_monitor(app: Flask, cache_manager: EnhancedCache = None):
    """Initialize the global performance monitor."""
    global _performance_monitor
    _performance_monitor = PerformanceMonitor(app, cache_manager)
    return _performance_monitor
