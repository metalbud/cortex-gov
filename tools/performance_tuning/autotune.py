#!/usr/bin/env python3
"""
Performance Autotune System for Cortex-GOV
Automatically detects performance issues and applies optimization strategies
"""

import json
import logging
import time
import psutil
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\Users\\metalbud\\clawd\\cortex-gov\\artifacts\\performance\\H019-autotune.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceAutotune:
    def __init__(self, baseline_path: str = "cortex-gov/artifacts/performance/H019-baseline-metrics.json"):
        self.baseline_path = baseline_path
        self.baseline_metrics = self._load_baseline()
        self.performance_history = []
        self.optimization_history = []
        self.resource_thresholds = {
            'cpu_high': 80.0,
            'cpu_critical': 90.0,
            'memory_high': 85.0,
            'memory_critical': 95.0,
            'disk_high': 90.0,
            'disk_critical': 95.0
        }
        
    def _load_baseline(self) -> Dict[str, Any]:
        """Load performance baselines from file"""
        try:
            with open(self.baseline_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Baseline file not found at {self.baseline_path}, using defaults")
            return self._create_default_baseline()
    
    def _create_default_baseline(self) -> Dict[str, Any]:
        """Create default performance baselines"""
        return {
            'cpu_normal': (20.0, 40.0),
            'memory_normal': (30.0, 60.0),
            'disk_normal': (50.0, 80.0),
            'response_time_normal': (0.1, 0.5),
            'error_rate_normal': (0.0, 0.01),
            'timestamp': datetime.now().isoformat()
        }
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system performance metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'disk_free': psutil.disk_usage('/').free,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
            'process_count': len(psutil.pids()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add process-level metrics
        process_metrics = []
        for proc in psutil.process_iter(['cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] is not None and proc_info['memory_percent'] is not None:
                    process_metrics.append({
                        'pid': proc.pid,
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_percent': proc_info['memory_percent'],
                        'name': proc.name()
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        metrics['processes'] = process_metrics[:10]  # Top 10 processes by CPU
        self.performance_history.append(metrics)
        
        return metrics
    
    def _analyze_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current performance against baselines"""
        analysis = {
            'timestamp': metrics['timestamp'],
            'issues': [],
            'optimization_opportunities': [],
            'overall_status': 'normal'
        }
        
        # CPU Analysis
        if metrics['cpu_percent'] > self.resource_thresholds['cpu_critical']:
            analysis['issues'].append({
                'type': 'cpu_critical',
                'value': metrics['cpu_percent'],
                'threshold': self.resource_thresholds['cpu_critical'],
                'severity': 'critical'
            })
            analysis['overall_status'] = 'critical'
        elif metrics['cpu_percent'] > self.resource_thresholds['cpu_high']:
            analysis['issues'].append({
                'type': 'cpu_high',
                'value': metrics['cpu_percent'],
                'threshold': self.resource_thresholds['cpu_high'],
                'severity': 'high'
            })
            analysis['overall_status'] = 'degraded'
        
        # Memory Analysis
        if metrics['memory_percent'] > self.resource_thresholds['memory_critical']:
            analysis['issues'].append({
                'type': 'memory_critical',
                'value': metrics['memory_percent'],
                'threshold': self.resource_thresholds['memory_critical'],
                'severity': 'critical'
            })
            analysis['overall_status'] = 'critical'
        elif metrics['memory_percent'] > self.resource_thresholds['memory_high']:
            analysis['issues'].append({
                'type': 'memory_high',
                'value': metrics['memory_percent'],
                'threshold': self.resource_thresholds['memory_high'],
                'severity': 'high'
            })
            analysis['overall_status'] = 'degraded'
        
        # Disk Analysis
        if metrics['disk_percent'] > self.resource_thresholds['disk_critical']:
            analysis['issues'].append({
                'type': 'disk_critical',
                'value': metrics['disk_percent'],
                'threshold': self.resource_thresholds['disk_critical'],
                'severity': 'critical'
            })
            analysis['overall_status'] = 'critical'
        elif metrics['disk_percent'] > self.resource_thresholds['disk_high']:
            analysis['issues'].append({
                'type': 'disk_high',
                'value': metrics['disk_percent'],
                'threshold': self.resource_thresholds['disk_high'],
                'severity': 'high'
            })
            analysis['overall_status'] = 'degraded'
        
        # Process Analysis
        high_cpu_processes = [p for p in metrics['processes'] if p['cpu_percent'] > 10]
        if high_cpu_processes:
            analysis['optimization_opportunities'].append({
                'type': 'process_optimization',
                'description': f"Found {len(high_cpu_processes)} processes using >10% CPU",
                'processes': high_cpu_processes,
                'potential_impact': 'high'
            })
        
        return analysis
    
    def _generate_optimization_strategies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization strategies based on performance analysis"""
        strategies = []
        
        for issue in analysis['issues']:
            if issue['type'] == 'cpu_critical' or issue['type'] == 'cpu_high':
                strategies.append({
                    'type': 'cpu_optimization',
                    'action': 'resource_limiting',
                    'description': 'Implement CPU resource limits for high-usage processes',
                    'target': processes_using_high_cpu,
                    'priority': 'high' if issue['type'] == 'cpu_critical' else 'medium'
                })
            
            elif issue['type'] == 'memory_critical' or issue['type'] == 'memory_high':
                strategies.append({
                    'type': 'memory_optimization',
                    'action': 'cache_management',
                    'description': 'Implement cache management and memory cleanup',
                    'target': 'system_memory',
                    'priority': 'high' if issue['type'] == 'memory_critical' else 'medium'
                })
            
            elif issue['type'] == 'disk_critical' or issue['type'] == 'disk_high':
                strategies.append({
                    'type': 'disk_optimization',
                    'action': 'cleanup_management',
                    'description': 'Implement disk cleanup and space management',
                    'target': 'disk_space',
                    'priority': 'high' if issue['type'] == 'disk_critical' else 'medium'
                })
        
        # Add process optimization strategies
        for opportunity in analysis['optimization_opportunities']:
            if opportunity['type'] == 'process_optimization':
                strategies.append({
                    'type': 'process_optimization',
                    'action': 'process_priority_adjustment',
                    'description': 'Adjust process priorities based on importance',
                    'target': opportunity['processes'],
                    'priority': 'medium'
                })
        
        return strategies
    
    def _apply_optimization(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an optimization strategy"""
        result = {
            'strategy': strategy,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'details': '',
            'rollback_data': None
        }
        
        try:
            if strategy['type'] == 'cpu_optimization':
                result['success'], result['details'] = self._apply_cpu_optimization(strategy)
            elif strategy['type'] == 'memory_optimization':
                result['success'], result['details'] = self._apply_memory_optimization(strategy)
            elif strategy['type'] == 'disk_optimization':
                result['success'], result['details'] = self._apply_disk_optimization(strategy)
            elif strategy['type'] == 'process_optimization':
                result['success'], result['details'] = self._apply_process_optimization(strategy)
        except Exception as e:
            result['details'] = f"Error applying optimization: {str(e)}"
        
        self.optimization_history.append(result)
        return result
    
    def _apply_cpu_optimization(self, strategy: Dict[str, Any]) -> tuple:
        """Apply CPU optimization strategies"""
        # In a real implementation, this would use cgroups or process priorities
        logger.info(f"Applying CPU optimization: {strategy['description']}")
        return True, "CPU optimization applied (simulation)"
    
    def _apply_memory_optimization(self, strategy: Dict[str, Any]) -> tuple:
        """Apply memory optimization strategies"""
        # In a real implementation, this would clear caches and manage memory
        logger.info(f"Applying memory optimization: {strategy['description']}")
        return True, "Memory optimization applied (simulation)"
    
    def _apply_disk_optimization(self, strategy: Dict[str, Any]) -> tuple:
        """Apply disk optimization strategies"""
        # In a real implementation, this would clean up temporary files
        logger.info(f"Applying disk optimization: {strategy['description']}")
        return True, "Disk optimization applied (simulation)"
    
    def _apply_process_optimization(self, strategy: Dict[str, Any]) -> tuple:
        """Apply process optimization strategies"""
        # In a real implementation, this would adjust process priorities
        logger.info(f"Applying process optimization: {strategy['description']}")
        return True, "Process optimization applied (simulation)"
    
    def analyze(self, output_path: str = None) -> Dict[str, Any]:
        """Run performance analysis"""
        logger.info("Starting performance analysis")
        
        metrics = self._collect_system_metrics()
        analysis = self._analyze_performance(metrics)
        strategies = self._generate_optimization_strategies(analysis)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics,
            'analysis': analysis,
            'strategies': strategies,
            'recommendations': len(strategies)
        }
        
        if output_path:
            # Convert to absolute path
            import os
            abs_path = os.path.abspath(output_path)
            with open(abs_path, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Analysis results saved to {abs_path}")
        
        return result
    
    def optimize(self, validate: bool = True) -> Dict[str, Any]:
        """Apply optimizations"""
        logger.info("Starting performance optimization")
        
        analysis = self._analyze_performance(self._collect_system_metrics())
        strategies = self._generate_optimization_strategies(analysis)
        
        results = []
        for strategy in strategies:
            result = self._apply_optimization(strategy)
            results.append(result)
        
        optimization_summary = {
            'timestamp': datetime.now().isoformat(),
            'strategies_applied': len(strategies),
            'successful_optimizations': sum(1 for r in results if r['success']),
            'failed_optimizations': sum(1 for r in results if not r['success']),
            'results': results
        }
        
        if validate:
            validation_result = self._validate_optimizations(optimization_summary)
            optimization_summary['validation'] = validation_result
        
        return optimization_summary
    
    def _validate_optimizations(self, optimization_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that optimizations improved performance"""
        logger.info("Validating optimization results")
        
        # Collect metrics after optimization
        post_metrics = self._collect_system_metrics()
        pre_metrics = self.performance_history[-2] if len(self.performance_history) > 1 else post_metrics
        
        validation = {
            'timestamp': datetime.now().isoformat(),
            'improvements': {},
            'degradations': {},
            'overall_impact': 'neutral'
        }
        
        # Compare CPU usage
        if post_metrics['cpu_percent'] < pre_metrics['cpu_percent']:
            validation['improvements']['cpu'] = {
                'before': pre_metrics['cpu_percent'],
                'after': post_metrics['cpu_percent'],
                'improvement': pre_metrics['cpu_percent'] - post_metrics['cpu_percent']
            }
        elif post_metrics['cpu_percent'] > pre_metrics['cpu_percent']:
            validation['degradations']['cpu'] = {
                'before': pre_metrics['cpu_percent'],
                'after': post_metrics['cpu_percent'],
                'degradation': post_metrics['cpu_percent'] - pre_metrics['cpu_percent']
            }
        
        # Compare memory usage
        if post_metrics['memory_percent'] < pre_metrics['memory_percent']:
            validation['improvements']['memory'] = {
                'before': pre_metrics['memory_percent'],
                'after': post_metrics['memory_percent'],
                'improvement': pre_metrics['memory_percent'] - post_metrics['memory_percent']
            }
        elif post_metrics['memory_percent'] > pre_metrics['memory_percent']:
            validation['degradations']['memory'] = {
                'before': pre_metrics['memory_percent'],
                'after': post_metrics['memory_percent'],
                'degradation': post_metrics['memory_percent'] - pre_metrics['memory_percent']
            }
        
        # Determine overall impact
        if len(validation['improvements']) > len(validation['degradations']):
            validation['overall_impact'] = 'positive'
        elif len(validation['degradations']) > len(validation['improvements']):
            validation['overall_impact'] = 'negative'
        else:
            validation['overall_impact'] = 'neutral'
        
        return validation


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Cortex-GOV Performance Autotune')
    parser.add_argument('--analyze', action='store_true', help='Run performance analysis')
    parser.add_argument('--optimize', action='store_true', help='Apply optimizations')
    parser.add_argument('--validate', action='store_true', help='Validate optimization results')
    parser.add_argument('--baseline', default='C:\\Users\\metalbud\\clawd\\cortex-gov\\artifacts\\performance\\H019-baseline-metrics.json',
                       help='Path to baseline metrics file')
    
    args = parser.parse_args()
    
    autotune = PerformanceAutotune(args.baseline)
    
    if args.analyze:
        result = autotune.analyze('C:\\Users\\metalbud\\clawd\\cortex-gov\\artifacts\\performance\\H019-analysis-result.json')
        print(f"Analysis complete. Found {result['recommendations']} optimization opportunities.")
    
    if args.optimize:
        result = autotune.optimize(args.validate)
        print(f"Optimization complete. Applied {result['strategies_applied']} strategies.")
        print(f"Success rate: {result['successful_optimizations']}/{result['strategies_applied']}")
        
        if args.validate and 'validation' in result:
            validation = result['validation']
            print(f"Validation result: {validation['overall_impact']}")
            if validation['improvements']:
                print("Improvements:")
                for resource, improvement in validation['improvements'].items():
                    print(f"  {resource}: {improvement['improvement']:.2f}% improvement")
            if validation['degradations']:
                print("Degradations:")
                for resource, degradation in validation['degradations'].items():
                    print(f"  {resource}: {degradation['degradation']:.2f}% degradation")


if __name__ == '__main__':
    main()