#!/usr/bin/env python3
"""
TODO Cleaner for H030 task
Analyzes and cleans up stale TODO items across the workspace
"""

import json
import os
import re
from datetime import datetime, timedelta
import argparse

class TODOCleaner:
    def __init__(self, workspace_root='.'):
        self.workspace_root = workspace_root
        self.cleaned_items = []
        self.backup_items = []
    
    def scan_for_todos(self):
        """Scan workspace for TODO items"""
        todo_items = []
        
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip certain directories
            if any(skip_dir in root for skip_dir in ['artifacts', 'node_modules', '__pycache__', '.git']):
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
                            # Extract task details
                            title_match = re.search(rf'### {re.escape(task_id)}:\s*(.*?)\n', content)
                            title = title_match.group(1).split('\n')[0].strip() if title_match else 'Unknown'
                            
                            epic_match = re.search(r'Epic:\s*(.*?)\n', content[content.find(f'### {task_id}:'):])
                            epic = epic_match.group(1).strip() if epic_match else 'Unknown'
                            
                            age_days = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(project_path))).days
                            
                            todo_items.append({
                                'id': task_id,
                                'title': title,
                                'epic': epic,
                                'path': project_path,
                                'age_days': age_days,
                                'last_modified': datetime.fromtimestamp(os.path.getmtime(project_path)).isoformat()
                            })
                            
                except Exception as e:
                    print(f"Error reading {project_path}: {e}")
        
        return todo_items
    
    def analyze_stale_items(self, todo_items, max_age_days=30):
        """Identify stale TODO items based on age"""
        stale_items = []
        for item in todo_items:
            if item['age_days'] > max_age_days:
                stale_items.append(item)
        return stale_items
    
    def backup_projects(self, project_paths):
        """Create backups of project files before modification"""
        backup_dir = os.path.join(self.workspace_root, 'artifacts', 'cleanup', 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        backups = {}
        for project_path in project_paths:
            if os.path.exists(project_path):
                backup_path = os.path.join(backup_dir, f"{os.path.basename(project_path)}.bak")
                try:
                    with open(project_path, 'r', encoding='utf-8') as src:
                        content = src.read()
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(content)
                    backups[project_path] = backup_path
                except Exception as e:
                    print(f"Failed to backup {project_path}: {e}")
        return backups
    
    def remove_stale_todos(self, stale_items, dry_run=True):
        """Remove stale TODO items from projects"""
        modified_projects = set()
        
        for item in stale_items:
            project_path = item['path']
            if project_path not in modified_projects:
                modified_projects.add(project_path)
        
        if dry_run:
            print(f"[DRY RUN] Would modify {len(modified_projects)} projects:")
            for project in modified_projects:
                print(f"  - {project}")
            print(f"[DRY RUN] Would remove {len(stale_items)} stale TODO items")
            return stale_items
        
        # Create backups
        backups = self.backup_projects(list(modified_projects))
        
        # Actually remove the TODO items
        cleaned_items = []
        for item in stale_items:
            try:
                with open(item['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create backup before modification
                if item['path'] in backups:
                    self.backup_items.append({
                        'original_path': item['path'],
                        'backup_path': backups[item['path']],
                        'item': item
                    })
                
                # Remove the TODO task section
                task_pattern = rf'### {re.escape(item["id"])}:[\s\S]*?(?=###|\Z)'
                new_content = re.sub(task_pattern, '', content)
                
                # Clean up extra blank lines
                new_content = re.sub(r'\n\s*\n\s*\n', '\n\n', new_content)
                
                # Write back
                with open(item['path'], 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                cleaned_items.append({
                    'item': item,
                    'backup_path': backups[item['path']] if item['path'] in backups else None
                })
                
            except Exception as e:
                print(f"Error cleaning {item['id']}: {e}")
        
        return cleaned_items
    
    def generate_report(self, todo_items, stale_items, cleaned_items):
        """Generate a cleanup report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_todo_items': len(todo_items),
                'stale_items_count': len(stale_items),
                'cleaned_items_count': len(cleaned_items),
                'modified_projects': len(set(item['path'] for item in cleaned_items)) if cleaned_items else 0
            },
            'todo_distribution': {},
            'stale_items': stale_items,
            'cleaned_items': cleaned_items,
            'backup_items': self.backup_items
        }
        
        # Distribution by epic
        for item in todo_items:
            epic = item['epic']
            if epic not in report['todo_distribution']:
                report['todo_distribution'][epic] = {'total': 0, 'stale': 0}
            report['todo_distribution'][epic]['total'] += 1
            
            if item in stale_items:
                report['todo_distribution'][epic]['stale'] += 1
        
        return report
    
    def save_report(self, report, output_path):
        """Save cleanup report to file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
    
    def print_summary(self, todo_items, stale_items):
        """Print summary of TODO analysis"""
        print(f"\n=== TODO BACKUP SUMMARY ===")
        print(f"Total TODO items found: {len(todo_items)}")
        print(f"Stale items (>30 days): {len(stale_items)}")
        
        if todo_items:
            print(f"\nDistribution by epic:")
            epics = {}
            for item in todo_items:
                epics[item['epic']] = epics.get(item['epic'], 0) + 1
            
            for epic, count in sorted(epics.items()):
                stale_count = len([item for item in stale_items if item['epic'] == epic])
                print(f"  {epic}: {count} total ({stale_count} stale)")

def main():
    parser = argparse.ArgumentParser(description='Clean up stale TODO items')
    parser.add_argument('--directory', '-d', default='.', help='Workspace directory (default: current)')
    parser.add_argument('--max-age', '-a', type=int, default=30, help='Maximum age in days before considering TODO stale (default: 30)')
    parser.add_argument('--execute', '-x', action='store_true', help='Actually remove stale items (default: dry run)')
    parser.add_argument('--report', '-r', help='Output report file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    cleaner = TODOCleaner(args.directory)
    
    print(f"Scanning workspace: {os.path.abspath(args.directory)}")
    todo_items = cleaner.scan_for_todos()
    
    stale_items = cleaner.analyze_stale_items(todo_items, args.max_age)
    
    cleaner.print_summary(todo_items, stale_items)
    
    if stale_items:
        print(f"\nStale items to clean:")
        for item in stale_items:
            print(f"  {item['id']}: {item['title']} ({item['age_days']} days)")
        
        print(f"\n{'DRY RUN MODE' if not args.execute else 'EXECUTION MODE'}")
        if args.execute:
            confirm = input("Proceed with cleanup? (y/N): ")
            if confirm.lower() != 'y':
                print("Cleanup cancelled.")
                return
        
        cleaned_items = cleaner.remove_stale_todos(stale_items, dry_run=not args.execute)
        
        if cleaned_items:
            print(f"\nSuccessfully cleaned {len(cleaned_items)} items")
        
        # Generate report
        report = cleaner.generate_report(todo_items, stale_items, cleaned_items)
        
        if args.report:
            cleaner.save_report(report, args.report)
            print(f"\nReport saved to: {args.report}")
    else:
        print(f"\nNo stale TODO items found (max age: {args.max_age} days)")

if __name__ == '__main__':
    main()