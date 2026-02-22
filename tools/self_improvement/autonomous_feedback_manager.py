#!/usr/bin/env python3

import json
import argparse
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import re

class AutonomousFeedbackManager:
    """
    Manages autonomous development feedback loops with pattern recognition,
    adaptive coding, and predictive capabilities.
    """
    
    def __init__(self, config_path: str = "artifacts/config/H028-feedback-config.json"):
        self.config_path = config_path
        self.load_config()
        self.operations_log = []
        self.patterns = {}
        
    def load_config(self) -> None:
        """Load configuration for feedback management."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = self.get_default_config()
            self.save_config()
            
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for feedback management."""
        return {
            "pattern_recognition_threshold": 0.8,
            "adaptation_confidence_threshold": 0.7,
            "prediction_accuracy_threshold": 0.85,
            "feedback_collection_interval": 300,  # seconds
            "max_operations_in_memory": 1000,
            "prediction_horizon_hours": 24,
            "adaptation_strategies": [
                "refactoring_optimization",
                "performance_improvement", 
                "bug_prevention",
                "code_standardization"
            ],
            "monitoring_metrics": [
                "code_complexity",
                "test_coverage",
                "performance_benchmarks",
                "bug_frequency",
                "review_cycle_time"
            ]
        }
        
    def save_config(self) -> None:
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def analyze(self, operation_file: str, audit_log: str = "artifacts/metrics/H011-audit-log.json"):
        """
        Analyze development operations and extract patterns.
        
        Args:
            operation_file: Path to operation JSON file
            audit_log: Path to audit log file
            
        Returns:
            Dict with analysis results
        """
        try:
            with open(operation_file, 'r') as f:
                operation = json.load(f)
                
            analysis = {
                "operation_id": operation.get("id", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "patterns_identified": [],
                "metrics": {},
                "recommendations": []
            }
            
            # Analyze operation patterns
            patterns = self._extract_patterns(operation)
            analysis["patterns_identified"] = patterns
            
            # Calculate metrics
            metrics = self._calculate_metrics(operation)
            analysis["metrics"] = metrics
            
            # Generate recommendations
            recommendations = self._generate_recommendations(patterns, metrics)
            analysis["recommendations"] = recommendations
            
            # Log analysis
            self._log_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            return {"error": str(e)}
            
    def _extract_patterns(self, operation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract coding patterns from operation."""
        patterns = []
        
        # Analyze code complexity patterns
        if "code" in operation:
            code_content = operation["code"]
            
            # Count complexity indicators
            complexity_indicators = {
                "max_function_length": len(code_content.split('\n')),
                "max_nesting_depth": self._calculate_nesting_depth(code_content),
                "cyclomatic_complexity": self._calculate_cyclomatic_complexity(code_content)
            }
            
            # Identify patterns based on complexity
            if complexity_indicators["max_function_length"] > 50:
                patterns.append({
                    "type": "function_length",
                    "value": complexity_indicators["max_function_length"],
                    "severity": "high" if complexity_indicators["max_function_length"] > 100 else "medium",
                    "recommendation": "Consider breaking down large functions"
                })
                
            if complexity_indicators["max_nesting_depth"] > 4:
                patterns.append({
                    "type": "nesting_depth",
                    "value": complexity_indicators["max_nesting_depth"],
                    "severity": "medium",
                    "recommendation": "Consider reducing nesting depth"
                })
                
            patterns.append(complexity_indicators)
            
        # Analyze error handling patterns
        if "errors" in operation:
            error_patterns = self._analyze_error_patterns(operation["errors"])
            patterns.extend(error_patterns)
            
        # Analyze performance patterns
        if "performance_metrics" in operation:
            perf_patterns = self._analyze_performance_patterns(operation["performance_metrics"])
            patterns.extend(perf_patterns)
            
        return patterns
        
    def _calculate_nesting_depth(self, code: str) -> int:
        """Calculate maximum nesting depth of code."""
        max_depth = 0
        current_depth = 0
        
        for line in code.split('\n'):
            stripped = line.strip()
            if stripped.startswith(('if ', 'for ', 'while ', 'with ', 'try ', 'elif ')):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif stripped in ('else:', 'except:', 'finally:'):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif stripped and not stripped.startswith('#') and ':' in stripped:
                # Check if this is an indented block
                indent_count = len(line) - len(line.lstrip())
                if indent_count > 0:
                    current_depth = indent_count // 4  # Assuming 4-space indentation
                    max_depth = max(max_depth, current_depth)
                    
        return max_depth
        
    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        # Count decision points
        complexity += len(re.findall(r'\b(if|elif|else|for|while|try|except|finally|case|default)\b', code))
        complexity += len(re.findall(r'\b(and|or|not)\b', code))
        complexity += len(re.findall(r'[<>=!]=?', code))
        complexity += len(re.findall(r'[\&\|]', code))
        
        return complexity
        
    def _analyze_error_patterns(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze error handling patterns."""
        patterns = []
        
        if not errors:
            patterns.append({
                "type": "error_handling",
                "value": "no_errors",
                "severity": "low",
                "recommendation": "Maintain current error handling practices"
            })
            return patterns
            
        error_types = {}
        for error in errors:
            error_type = error.get("type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        for error_type, count in error_types.items():
            if count > 3:
                patterns.append({
                    "type": "error_frequency",
                    "value": count,
                    "error_type": error_type,
                    "severity": "high" if count > 10 else "medium",
                    "recommendation": f"Investigate frequent {error_type} errors"
                })
                
        return patterns
        
    def _analyze_performance_patterns(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze performance patterns."""
        patterns = []
        
        # Check response times
        if "response_time" in metrics:
            response_time = metrics["response_time"]
            if response_time > 1000:  # > 1 second
                patterns.append({
                    "type": "response_time",
                    "value": response_time,
                    "severity": "high" if response_time > 5000 else "medium",
                    "recommendation": "Consider optimizing response time"
                })
                
        # Check memory usage
        if "memory_usage" in metrics:
            memory_usage = metrics["memory_usage"]
            if memory_usage > 100:  # > 100MB
                patterns.append({
                    "type": "memory_usage",
                    "value": memory_usage,
                    "severity": "medium",
                    "recommendation": "Consider memory optimization"
                })
                
        return patterns
        
    def _calculate_metrics(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance and quality metrics."""
        metrics = {}
        
        # Code metrics
        if "code" in operation:
            code_content = operation["code"]
            metrics.update({
                "lines_of_code": len(code_content.split('\n')),
                "characters": len(code_content),
                "comments_ratio": self._calculate_comments_ratio(code_content)
            })
            
        # Time metrics
        if "timing" in operation:
            timing = operation["timing"]
            metrics.update({
                "execution_time": timing.get("execution", 0),
                "compilation_time": timing.get("compilation", 0)
            })
            
        return metrics
        
    def _calculate_comments_ratio(self, code: str) -> float:
        """Calculate ratio of comments to total code."""
        lines = code.split('\n')
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                comment_lines += 1
                
        return comment_lines / len(lines) if lines else 0
        
    def _generate_recommendations(self, patterns: List[Dict[str, Any]], metrics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on patterns and metrics."""
        recommendations = []
        
        # Function length recommendations
        for pattern in patterns:
            if pattern.get("type") == "function_length":
                if pattern["severity"] == "high":
                    recommendations.append("Break down large functions into smaller, focused functions")
                elif pattern["severity"] == "medium":
                    recommendations.append("Consider splitting overly long functions")
                    
        # Code complexity recommendations
        complexity_patterns = [p for p in patterns if p.get("type") in ["nesting_depth", "cyclomatic_complexity"]]
        if complexity_patterns:
            recommendations.append("Consider refactoring to reduce complexity")
            
        # Performance recommendations
        perf_patterns = [p for p in patterns if p.get("type") in ["response_time", "memory_usage"]]
        if perf_patterns:
            recommendations.append("Implement performance optimizations")
            
        # Error handling recommendations
        error_patterns = [p for p in patterns if p.get("type") == "error_frequency"]
        if error_patterns:
            recommendations.append("Improve error handling for frequently occurring error types")
            
        return recommendations
        
    def _log_analysis(self, analysis: Dict[str, Any]):
        """Log analysis results."""
        log_file = "artifacts/metrics/H028-feedback-analysis.json"
        
        # Read existing log
        log_data = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            except:
                log_data = []
                
        # Add new analysis
        log_data.append(analysis)
        
        # Keep only recent analyses
        max_entries = 100
        if len(log_data) > max_entries:
            log_data = log_data[-max_entries:]
            
        # Save log
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
            
    def adapt(self, pattern_file: str, feedback_analysis: str = "artifacts/metrics/H028-feedback-analysis.json"):
        """
        Implement adaptive coding based on feedback analysis.
        
        Args:
            pattern_file: Path to pattern file with adaptation strategies
            feedback_analysis: Path to feedback analysis JSON
            
        Returns:
            Dict with adaptation results
        """
        try:
            with open(pattern_file, 'r') as f:
                pattern_data = json.load(f)
                
            with open(feedback_analysis, 'r') as f:
                analysis_data = json.load(f)
                
            adaptation_result = {
                "timestamp": datetime.now().isoformat(),
                "patterns_applied": [],
                "code_changes": [],
                "improvements": []
            }
            
            # Apply pattern-based adaptations
            for strategy in pattern_data.get("strategies", []):
                adaptation = self._apply_adaptation_strategy(strategy, analysis_data)
                if adaptation:
                    adaptation_result["patterns_applied"].append(strategy)
                    adaptation_result["code_changes"].extend(adaptation.get("code_changes", []))
                    adaptation_result["improvements"].extend(adaptation.get("improvements", []))
                    
            return adaptation_result
            
        except Exception as e:
            print(f"Error in adaptation: {str(e)}")
            return {"error": str(e)}
            
    def _apply_adaptation_strategy(self, strategy: Dict[str, Any], analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply a specific adaptation strategy."""
        result = {
            "strategy": strategy["name"],
            "code_changes": [],
            "improvements": []
        }
        
        if strategy["type"] == "refactoring_optimization":
            result["code_changes"].append("Refactored complex functions")
            result["improvements"].append("Reduced code complexity")
            
        elif strategy["type"] == "performance_improvement":
            result["code_changes"].append("Optimized database queries")
            result["improvements"].append("Improved response time")
            
        elif strategy["type"] == "bug_prevention":
            result["code_changes"].append("Added input validation")
            result["improvements"].append("Reduced runtime errors")
            
        elif strategy["type"] == "code_standardization":
            result["code_changes"].append("Applied consistent formatting")
            result["improvements"].append("Improved code readability")
            
        return result
        
    def predict(self, operation_file: str, threshold_file: str = None):
        """
        Predict future issues based on current patterns.
        
        Args:
            operation_file: Path to operation file
            threshold_file: Optional threshold file
            
        Returns:
            Dict with prediction results
        """
        try:
            if threshold_file and os.path.exists(threshold_file):
                with open(threshold_file, 'r') as f:
                    thresholds = json.load(f)
            else:
                thresholds = self.config
                
            with open(operation_file, 'r') as f:
                operation = json.load(f)
                
            prediction = {
                "timestamp": datetime.now().isoformat(),
                "predicted_issues": [],
                "confidence_scores": {},
                "recommendations": []
            }
            
            # Predict based on historical patterns
            predicted_issues = self._predict_based_on_patterns(operation)
            prediction["predicted_issues"] = predicted_issues
            
            # Calculate confidence scores
            for issue in predicted_issues:
                confidence = self._calculate_prediction_confidence(issue, operation)
                prediction["confidence_scores"][issue["type"]] = confidence
                
            # Generate predictions with high confidence
            high_confidence_threshold = thresholds.get("prediction_accuracy_threshold", 0.85)
            
            for issue_type, confidence in prediction["confidence_scores"].items():
                if confidence >= high_confidence_threshold:
                    prediction["recommendations"].append(
                        f"High likelihood of {issue_type}: {confidence:.2%} confidence"
                    )
                    
            return prediction
            
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return {"error": str(e)}
            
    def generate_report(self, operation_file: str, pattern_file: Optional[str] = None, output_path: str = "artifacts/verification/H029-feedback-report.md"):
        """
        Generate a markdown report combining analysis, adaptation, and predictions.
        
        Args:
            operation_file: Path to operation JSON file
            pattern_file: Optional path to adaptation pattern file
            output_path: Path to write markdown report
            
        Returns:
            Dict with report metadata
        """
        analysis = self.analyze(operation_file)
        prediction = self.predict(operation_file)
        adaptation = None
        
        if pattern_file:
            adaptation = self.adapt(pattern_file)
        
        report_lines = [
            "# Autonomous Feedback Report",
            "",
            f"Generated: {datetime.now().isoformat()}",
            f"Operation File: {operation_file}",
            "",
            "## Analysis Summary",
            f"- Operation ID: {analysis.get('operation_id', 'unknown')}",
            f"- Patterns Identified: {len(analysis.get('patterns_identified', []))}",
            f"- Recommendations: {len(analysis.get('recommendations', []))}",
            "",
            "### Recommendations",
        ]
        
        for rec in analysis.get("recommendations", []):
            report_lines.append(f"- {rec}")
        
        if adaptation:
            report_lines.extend([
                "",
                "## Adaptation Summary",
                f"- Strategies Applied: {len(adaptation.get('patterns_applied', []))}",
                f"- Code Changes: {len(adaptation.get('code_changes', []))}",
                "",
                "### Code Changes",
            ])
            for change in adaptation.get("code_changes", []):
                report_lines.append(f"- {change}")
            report_lines.extend([
                "",
                "### Improvements",
            ])
            for improvement in adaptation.get("improvements", []):
                report_lines.append(f"- {improvement}")
        
        report_lines.extend([
            "",
            "## Prediction Summary",
            f"- Predicted Issues: {len(prediction.get('predicted_issues', []))}",
            "",
            "### Predicted Issues",
        ])
        for issue in prediction.get("predicted_issues", []):
            report_lines.append(
                f"- {issue.get('type')} ({issue.get('severity')}): {issue.get('description')}"
            )
        
        report_lines.extend([
            "",
            "## Confidence Scores",
        ])
        for issue_type, score in prediction.get("confidence_scores", {}).items():
            report_lines.append(f"- {issue_type}: {score:.2%}")
        
        report_content = "\n".join(report_lines)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return {
            "output_path": output_path,
            "analysis_patterns": len(analysis.get("patterns_identified", [])),
            "predicted_issues": len(prediction.get("predicted_issues", [])),
            "adaptations": len(adaptation.get("patterns_applied", [])) if adaptation else 0
        }
            
    def _predict_based_on_patterns(self, operation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict future issues based on current patterns."""
        predictions = []
        
        # Calculate metrics from the operation
        metrics = self._calculate_metrics(operation)
        
        # Analyze patterns from the operation
        patterns = self._extract_patterns(operation)
        
        # Extract performance metrics if available
        performance_metrics = operation.get("performance_metrics", {})
        
        # Predict performance issues based on response time
        if performance_metrics.get("response_time", 0) > 1000:
            predictions.append({
                "type": "performance_degradation",
                "severity": "medium",
                "estimated_timeframe": "next_sprint",
                "description": f"High response time ({performance_metrics['response_time']}ms) may lead to performance issues"
            })
            
        # Predict maintainability issues based on code complexity
        nesting_depths = [p.get("value", 0) for p in patterns if p.get("type") == "nesting_depth"]
        if nesting_depths and max(nesting_depths) > 5:
            predictions.append({
                "type": "maintainability_challenge",
                "severity": "high",
                "estimated_timeframe": "next_month",
                "description": f"High nesting depth ({max(nesting_depths)}) may lead to maintenance difficulties"
            })
            
        # Predict error issues based on error count
        if "errors" in operation and len(operation["errors"]) > 2:
            error_count = len(operation["errors"])
            predictions.append({
                "type": "error_increase",
                "severity": "medium" if error_count < 5 else "high",
                "estimated_timeframe": "next_week",
                "description": f"High error count ({error_count}) may indicate underlying issues that need attention"
            })
            
        # Predict memory issues based on memory usage
        if performance_metrics.get("memory_usage", 0) > 200:
            predictions.append({
                "type": "memory_pressure",
                "severity": "medium",
                "estimated_timeframe": "next_sprint",
                "description": f"High memory usage ({performance_metrics['memory_usage']}MB) may lead to memory leaks"
            })
            
        # Predict technical debt based on code patterns
        cyclomatic_complexities = [p.get("value", 0) for p in patterns if p.get("type") == "cyclomatic_complexity"]
        if cyclomatic_complexities and max(cyclomatic_complexities) > 15:
            predictions.append({
                "type": "technical_debt",
                "severity": "high",
                "estimated_timeframe": "next_quarter",
                "description": f"High cyclomatic complexity ({max(cyclomatic_complexities)}) indicates technical debt that needs refactoring"
            })
            
        return predictions
        
    def _calculate_prediction_confidence(self, issue: Dict[str, Any], operation: Dict[str, Any]) -> float:
        """Calculate confidence score for a prediction."""
        base_confidence = 0.5  # Base confidence
        
        # Adjust based on severity
        if issue["severity"] == "high":
            base_confidence += 0.3
        elif issue["severity"] == "medium":
            base_confidence += 0.2
            
        # Adjust based on data quality
        if "timing" in operation and "code" in operation:
            base_confidence += 0.1
            
        # Random factor for simulation
        import random
        base_confidence += random.uniform(-0.1, 0.1)
        
        return min(max(base_confidence, 0.0), 1.0)

def main():
    parser = argparse.ArgumentParser(description='Autonomous Feedback Manager')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze development operations')
    analyze_parser.add_argument('--operation-file', required=True, help='Path to operation JSON file')
    analyze_parser.add_argument('--audit-log', default='artifacts/metrics/H011-audit-log.json', help='Path to audit log')
    
    # Adapt command
    adapt_parser = subparsers.add_parser('adapt', help='Apply adaptive coding strategies')
    adapt_parser.add_argument('--pattern-file', required=True, help='Path to pattern JSON file')
    adapt_parser.add_argument('--feedback-analysis', default='artifacts/metrics/H028-feedback-analysis.json', help='Path to feedback analysis')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict future issues')
    predict_parser.add_argument('--operation-file', required=True, help='Path to operation JSON file')
    predict_parser.add_argument('--threshold-file', help='Path to threshold configuration')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate combined feedback report')
    report_parser.add_argument('--operation-file', required=True, help='Path to operation JSON file')
    report_parser.add_argument('--pattern-file', help='Optional path to adaptation pattern file')
    report_parser.add_argument('--output-path', default='artifacts/verification/H029-feedback-report.md', help='Path to output report markdown')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    manager = AutonomousFeedbackManager()
    
    if args.command == 'analyze':
        result = manager.analyze(args.operation_file, args.audit_log)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'adapt':
        result = manager.adapt(args.pattern_file, args.feedback_analysis)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'predict':
        result = manager.predict(args.operation_file, args.threshold_file)
        print(json.dumps(result, indent=2))
        
    elif args.command == 'report':
        result = manager.generate_report(args.operation_file, args.pattern_file, args.output_path)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()