#!/usr/bin/env python3
"""
TODO Backlog Analyzer for H030 task
Analyzes TODO items, identifies stale items, and generates cleanup recommendations
"""

import json
import os
import re
from datetime import datetime, timedelta
import argparse

def scan_project_directory(directory):
    """Scan directory for PROJECT.md files and extract TODO tasks"""
    todo_items = []
    
    for root, dirs, files in os.walk(directory):
        # Skip artifacts and other directories we don't need to scan
        if 'artifacts' in root or 'node_modules' in root:
            continue
            
        if 'PROJECT.md' in files:
            project_path = os.path.join(root, 'PROJECT.md')
            try:
                with open(project_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract task headers with TODO status
                task_pattern = r'### (H\d{3}):\s*.*?\n.*?Status: (TODO|IN_PROGRESS|VERIFY|DONE|BLOCKED)'
                matches = re.findall(task_pattern, content, re.DOTALL)
                
                for task_id, status in matches:
                    if status == 'TODO':
                        # Extract task title and epic
                        title_match = re.search(rf'### {re.escape(task_id)}:\s*(.*?)\n', content)
                        title = title_match.group(1) if title_match else 'Unknown'
                        
                        # Extract epic if available
                        epic_match = re.search(r'Epic:\s*(.*?)\n', content[content.find(f'### {task_id}:'):])
                        epic = epic_match.group(1) if epic_match else 'Unknown'
                        
                        todo_items.append({
                            'id': task_id,
                            'title': title.strip(),
                            'epic': epic.strip(),
                            'path': project_path,
                            'last_modified': datetime.fromtimestamp(os.path.getmtime(project_path)).isoformat(),
                            'age_days': (datetime.now() - datetime.fromtimestamp(os.path.getmtime(project_path))).days
                        })
                        
            except Exception as e:
                print(f"Error reading {project_path}: {e}")
    
    return todo_items

def generate_backlog_report(todo_items):
    """Generate a comprehensive backlog analysis report"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_todo_items': len(todo_items),
        'todo_by_epic': {},
        'todo_by_age': {
            '0-7_days': 0,
            '8-30_days': 0,
            '31-90_days': 0,
            '90+_days': 0
        },
        'stale_candidates': [],
        'recommendations': []
    }
    
    # Categorize by epic
    for item in todo_items:
        epic = item['epic']
        if epic not in report['todo_by_epic']:
            report['todo_by_epic'][epic] = []
        report['todo_by_epic'][epic].append(item)
    
    # Categorize by age
    for item in todo_items:
        age = item['age_days']
        if age <= 7:
            report['todo_by_age']['0-7_days'] += 1
        elif age <= 30:
            report['todo_by_age']['8-30_days'] += 1
        elif age <= 90:
            report['todo_by_age']['31-90_days'] += 1
        else:
            report['todo_by_age']['90+_days'] += 1
    
    # Identify stale candidates (older than 30 days)
    for item in todo_items:
        if item['age_days'] > 30:
            report['stale_candidates'].append(item)
    
    # Generate recommendations
    if report['stale_candidates']:
        report['recommendations'].append({
            'priority': 'high',
            'action': 'review_stale_items',
            'description': f'Review {len(report["stale_candidates"])} stale TODO items older than 30 days',
            'items': [item['id'] for item in report['stale_candidates']]
        })
    
    if report['total_todo_items'] > 10:
        report['recommendations'].append({
            'priority': 'medium',
            'action': 'optimize_planning',
            'description': f'High TODO backlog ({report["total_todo_items"]} items) may indicate planning inefficiency',
            'suggestion': 'Consider breaking down large tasks or removing low-priority items'
        })
    
    return report

def main():
    parser = argparse.ArgumentParser(description='Analyze TODO backlog for cleanup')
    parser.add_argument('--directory', '-d', default='.', help='Directory to scan (default: current)')
    parser.add_argument('--report', '-r', action='store_true', help='Generate detailed report')
    parser.add_argument('--scan', '-s', action='store_true', help='Just scan and count TODOs')
    parser.add_argument('--output', '-o', help='Output file for report')
    
    args = parser.parse_args()
    
    print(f"Scanning directory: {os.path.abspath(args.directory)}")
    todo_items = scan_project_directory(args.directory)
    
    if args.scan:
        print(f"Found {len(todo_items)} TODO items")
        return
    
    if args.report:
        report = generate_backlog_report(todo_items)
        
        print(f"\n=== TODO BACKLOG ANALYSIS ===")
        print(f"Generated: {report['generated_at']}")
        print(f"Total TODO items: {report['total_todo_items']}")
        
        print(f"\nTODO by Age:")
        for age_group, count in report['todo_by_age'].items():
            print(f"  {age_group}: {count}")
        
        print(f"\nTODO by Epic:")
        for epic, items in report['todo_by_epic'].items():
            print(f"  {epic}: {len(items)} items")
        
        if report['stale_candidates']:
            print(f"\nStale Candidates (>30 days):")
            for item in report['stale_candidates']:
                print(f"  {item['id']}: {item['title']} ({item['age_days']} days)")
        
        print(f"\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority']}] {rec['description']}")
            if 'items' in rec:
                print(f"    Items: {', '.join(rec['items'])}")
        
        # Save report if output specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {args.output}")
    else:
        print(f"\nSummary: Found {len(todo_items)} TODO items")
        for item in todo_items:
            print(f"  {item['id']}: {item['title']} (Epic: {item['epic']})")

if __name__ == '__main__':
    main()