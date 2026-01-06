"""
Wave Planning Module
Generates migration waves based on application dependency analysis from IT Infrastructure Inventory
"""
import pandas as pd
import os
from typing import Dict, List, Tuple, Set
from strands import tool


def parse_it_inventory_dependencies(excel_file: str) -> Dict:
    """
    Parse dependency information from IT Infrastructure Inventory Excel
    
    Args:
        excel_file: Path to IT Infrastructure Inventory Excel file
    
    Returns:
        Dictionary containing all dependency data:
        {
            'servers': DataFrame,
            'applications': DataFrame,
            'databases': DataFrame,
            'server_to_app': DataFrame,
            'app_dependencies': DataFrame,
            'db_to_app': DataFrame,
            'server_communication': DataFrame,
            'has_dependencies': bool
        }
    """
    try:
        xl = pd.ExcelFile(excel_file)
        dependencies = {'has_dependencies': False}
        
        # Read all relevant sheets
        if 'Servers' in xl.sheet_names:
            dependencies['servers'] = pd.read_excel(excel_file, 'Servers')
        
        if 'Applications' in xl.sheet_names:
            dependencies['applications'] = pd.read_excel(excel_file, 'Applications')
        
        if 'Databases' in xl.sheet_names:
            dependencies['databases'] = pd.read_excel(excel_file, 'Databases')
        
        if 'Server to application' in xl.sheet_names:
            dependencies['server_to_app'] = pd.read_excel(excel_file, 'Server to application')
            if not dependencies['server_to_app'].empty:
                dependencies['has_dependencies'] = True
        
        if 'Application dependency' in xl.sheet_names:
            dependencies['app_dependencies'] = pd.read_excel(excel_file, 'Application dependency')
            if not dependencies['app_dependencies'].empty:
                dependencies['has_dependencies'] = True
        
        if 'Database to application' in xl.sheet_names:
            dependencies['db_to_app'] = pd.read_excel(excel_file, 'Database to application')
            if not dependencies['db_to_app'].empty:
                dependencies['has_dependencies'] = True
        
        if 'Server communication' in xl.sheet_names:
            dependencies['server_communication'] = pd.read_excel(excel_file, 'Server communication')
        
        return dependencies
        
    except Exception as e:
        print(f"Error parsing IT Inventory dependencies: {e}")
        return {'has_dependencies': False}


def build_dependency_graph(dependencies: Dict) -> Dict:
    """
    Build a directed graph of application dependencies
    
    Args:
        dependencies: Dictionary from parse_it_inventory_dependencies()
    
    Returns:
        Dictionary mapping app_id to dependency information:
        {
            'A1-CRM': {
                'depends_on': ['D1', 'A2-Auth'],
                'used_by': ['A11-Web'],
                'criticality': 'High',
                'servers': ['Server10', 'Server11'],
                'databases': ['D1']
            },
            ...
        }
    """
    graph = {}
    
    # Initialize with applications
    if 'applications' in dependencies and not dependencies['applications'].empty:
        for _, app in dependencies['applications'].iterrows():
            # Handle different possible column names
            app_id = app.get('Application ID') or app.get('AppID') or app.get('Application Name')
            if pd.isna(app_id):
                continue
                
            graph[str(app_id)] = {
                'depends_on': [],
                'used_by': [],
                'criticality': str(app.get('Criticality', 'Medium')),
                'servers': [],
                'databases': []
            }
    
    # Add application dependencies
    if 'app_dependencies' in dependencies and not dependencies['app_dependencies'].empty:
        for _, dep in dependencies['app_dependencies'].iterrows():
            src = str(dep.get('SRC App ID', ''))
            dest = str(dep.get('DEST App ID', ''))
            
            if not src or not dest or pd.isna(src) or pd.isna(dest):
                continue
            
            # Ensure both apps exist in graph
            if src not in graph:
                graph[src] = {'depends_on': [], 'used_by': [], 'criticality': 'Medium', 'servers': [], 'databases': []}
            if dest not in graph:
                graph[dest] = {'depends_on': [], 'used_by': [], 'criticality': 'Medium', 'servers': [], 'databases': []}
            
            # src depends on dest
            if dest not in graph[src]['depends_on']:
                graph[src]['depends_on'].append(dest)
            # dest is used by src
            if src not in graph[dest]['used_by']:
                graph[dest]['used_by'].append(src)
    
    # Add database dependencies
    if 'db_to_app' in dependencies and not dependencies['db_to_app'].empty:
        for _, dep in dependencies['db_to_app'].iterrows():
            db_id = str(dep.get('Database ID', ''))
            app_id = str(dep.get('Application ID', ''))
            
            if not db_id or not app_id or pd.isna(db_id) or pd.isna(app_id):
                continue
            
            if app_id in graph:
                if db_id not in graph[app_id]['depends_on']:
                    graph[app_id]['depends_on'].append(db_id)
                if db_id not in graph[app_id]['databases']:
                    graph[app_id]['databases'].append(db_id)
    
    # Add server mappings
    if 'server_to_app' in dependencies and not dependencies['server_to_app'].empty:
        for _, mapping in dependencies['server_to_app'].iterrows():
            app_id = str(mapping.get('appid', ''))
            server_id = str(mapping.get('serverId', ''))
            
            if not app_id or not server_id or pd.isna(app_id) or pd.isna(server_id):
                continue
            
            if app_id in graph and server_id not in graph[app_id]['servers']:
                graph[app_id]['servers'].append(server_id)
    
    return graph


def generate_migration_waves(dependency_graph: Dict, timeline_months: int = 18) -> List[Dict]:
    """
    Generate migration waves based on dependency graph
    
    Args:
        dependency_graph: Application dependency graph from build_dependency_graph()
        timeline_months: Total project timeline in months
    
    Returns:
        List of waves with applications grouped by dependencies:
        [
            {
                'name': 'Wave 1',
                'description': 'Independent applications',
                'applications': [...],
                'duration_months': 3,
                'start_month': 1,
                'end_month': 3
            },
            ...
        ]
    """
    if not dependency_graph:
        return []
    
    waves = []
    migrated = set()
    wave_num = 1
    
    # Calculate months per wave (divide timeline into roughly equal parts)
    # Reserve first portion for assessment/mobilize
    migration_months = max(timeline_months - 3, timeline_months * 0.7)
    
    # Wave 1: Independent applications (no dependencies)
    wave1_apps = []
    for app_id, app_data in dependency_graph.items():
        # Filter out database dependencies for independence check
        app_deps = [d for d in app_data['depends_on'] if d in dependency_graph]
        
        if not app_deps and app_id not in migrated:
            wave1_apps.append({
                'app_id': app_id,
                'criticality': app_data['criticality'],
                'servers': app_data['servers'],
                'databases': app_data['databases'],
                'used_by': app_data['used_by']
            })
            migrated.add(app_id)
    
    if wave1_apps:
        duration = max(2, int(migration_months / 4))  # At least 2 months
        waves.append({
            'name': 'Wave 1',
            'description': 'Independent applications with no dependencies',
            'applications': wave1_apps,
            'duration_months': duration,
            'start_month': 1,
            'end_month': duration
        })
    
    # Subsequent waves: Applications whose dependencies are migrated
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    
    while len(migrated) < len(dependency_graph) and iteration < max_iterations:
        iteration += 1
        wave_apps = []
        
        for app_id, app_data in dependency_graph.items():
            if app_id in migrated:
                continue
            
            # Get application dependencies (exclude databases)
            app_deps = [d for d in app_data['depends_on'] if d in dependency_graph]
            
            # Check if all application dependencies are migrated
            deps_migrated = all(dep in migrated for dep in app_deps)
            
            if deps_migrated:
                wave_apps.append({
                    'app_id': app_id,
                    'criticality': app_data['criticality'],
                    'servers': app_data['servers'],
                    'databases': app_data['databases'],
                    'depends_on': app_deps,
                    'used_by': app_data['used_by']
                })
                migrated.add(app_id)
        
        if not wave_apps:
            # Circular dependency or orphaned apps - add remaining to final wave
            for app_id in dependency_graph:
                if app_id not in migrated:
                    app_data = dependency_graph[app_id]
                    app_deps = [d for d in app_data['depends_on'] if d in dependency_graph]
                    wave_apps.append({
                        'app_id': app_id,
                        'criticality': app_data['criticality'],
                        'servers': app_data['servers'],
                        'databases': app_data['databases'],
                        'depends_on': app_deps,
                        'note': 'Circular dependency or complex integration'
                    })
                    migrated.add(app_id)
        
        if wave_apps:
            wave_num += 1
            prev_wave_end = waves[-1]['end_month'] if waves else 0
            duration = max(2, int(migration_months / 4))
            start = prev_wave_end + 1
            end = start + duration - 1
            
            waves.append({
                'name': f'Wave {wave_num}',
                'description': f'Applications with dependencies from previous waves',
                'applications': wave_apps,
                'duration_months': duration,
                'start_month': start,
                'end_month': end
            })
    
    # VALIDATION: Ensure all applications and servers are covered
    total_apps_in_waves = sum(len(wave['applications']) for wave in waves)
    total_servers_in_waves = sum(
        sum(len(app.get('servers', [])) for app in wave['applications'])
        for wave in waves
    )
    total_dbs_in_waves = sum(
        sum(len(app.get('databases', [])) for app in wave['applications'])
        for wave in waves
    )
    
    # Count total servers and databases from dependency graph
    all_servers = set()
    all_dbs = set()
    for app_data in dependency_graph.values():
        all_servers.update(app_data.get('servers', []))
        all_dbs.update(app_data.get('databases', []))
    
    total_servers_expected = len(all_servers)
    total_dbs_expected = len(all_dbs)
    
    # Add orphaned servers to final wave if any missing
    if total_servers_in_waves < total_servers_expected:
        orphaned_count = total_servers_expected - total_servers_in_waves
        if waves:
            waves[-1]['orphaned_servers'] = orphaned_count
            waves[-1]['description'] += f" (includes {orphaned_count} orphaned servers)"
    
    # Add validation metadata
    for wave in waves:
        wave['validation'] = {
            'apps_in_wave': len(wave['applications']),
            'servers_in_wave': sum(len(app.get('servers', [])) for app in wave['applications']),
            'dbs_in_wave': sum(len(app.get('databases', [])) for app in wave['applications'])
        }
    
    return waves


def format_wave_plan_markdown(waves: List[Dict], total_apps: int, total_servers: int) -> str:
    """
    Format wave plan as markdown for business case
    
    Args:
        waves: List of waves from generate_migration_waves()
        total_apps: Total number of applications
        total_servers: Total number of servers
    
    Returns:
        Markdown string with wave plan table and details
    """
    if not waves:
        return ""
    
    markdown = "## Migration Wave Plan (Based on Dependency Analysis)\n\n"
    
    # Calculate totals from waves
    total_apps_in_waves = sum(len(wave['applications']) for wave in waves)
    total_servers_in_waves = sum(
        sum(len(app.get('servers', [])) for app in wave['applications'])
        for wave in waves
    )
    total_dbs_in_waves = sum(
        sum(len(app.get('databases', [])) for app in wave['applications'])
        for wave in waves
    )
    
    markdown += f"**Total Applications**: {total_apps_in_waves} / {total_apps} | "
    markdown += f"**Total Servers**: {total_servers_in_waves} / {total_servers}"
    if total_dbs_in_waves > 0:
        markdown += f" | **Total Databases**: {total_dbs_in_waves}"
    markdown += "\n\n"
    
    # Summary table
    markdown += "| Wave | Timeline | Applications | Servers | Key Dependencies |\n"
    markdown += "|------|----------|--------------|---------|------------------|\n"
    
    for wave in waves:
        app_count = len(wave['applications'])
        server_count = sum(len(app.get('servers', [])) for app in wave['applications'])
        timeline = f"Months {wave['start_month']}-{wave['end_month']}"
        
        # Get key dependencies
        key_deps = set()
        for app in wave['applications']:
            if 'depends_on' in app and app['depends_on']:
                key_deps.update(app['depends_on'][:2])  # First 2 deps
        deps_str = ', '.join(list(key_deps)[:3]) if key_deps else 'None'
        if len(key_deps) > 3:
            deps_str += ', ...'
        
        markdown += f"| {wave['name']} | {timeline} | {app_count} | {server_count} | {deps_str} |\n"
    
    markdown += "\n### Wave Details\n\n"
    
    # Detailed breakdown
    for wave in waves:
        markdown += f"#### {wave['name']}: {wave['description']}\n"
        markdown += f"**Timeline**: Months {wave['start_month']}-{wave['end_month']}\n\n"
        
        # Count by criticality
        criticality_counts = {}
        for app in wave['applications']:
            crit = app.get('criticality', 'Medium')
            criticality_counts[crit] = criticality_counts.get(crit, 0) + 1
        
        if criticality_counts:
            markdown += "**Criticality Distribution**: "
            markdown += ", ".join([f"{k}: {v}" for k, v in criticality_counts.items()])
            markdown += "\n\n"
        
        markdown += "**Applications** (showing first 10):\n"
        
        for app in wave['applications'][:10]:
            app_line = f"- **{app['app_id']}**"
            app_line += f" (Criticality: {app.get('criticality', 'Medium')}"
            
            if app.get('servers'):
                app_line += f", Servers: {len(app['servers'])}"
            
            if app.get('databases'):
                app_line += f", Databases: {', '.join(app['databases'][:2])}"
            
            if app.get('depends_on'):
                app_line += f", Depends on: {', '.join(app['depends_on'][:2])}"
            
            app_line += ")"
            markdown += app_line + "\n"
        
        if len(wave['applications']) > 10:
            markdown += f"- ... and {len(wave['applications']) - 10} more applications\n"
        
        markdown += "\n"
    
    markdown += "**Note**: Wave plan generated from IT Infrastructure Inventory dependency analysis. "
    markdown += "Dependencies validated and applications grouped to minimize migration risk.\n\n"
    
    return markdown


@tool(name="generate_wave_plan_from_dependencies", 
      description="Generate migration wave plan from IT Infrastructure Inventory dependencies")
def generate_wave_plan_from_dependencies(it_inventory_file: str, timeline_months: int = 18) -> str:
    """
    Generate migration wave plan from IT Infrastructure Inventory
    
    Args:
        it_inventory_file: Path to IT Infrastructure Inventory Excel file
        timeline_months: Total project timeline in months (default: 18)
    
    Returns:
        Markdown formatted wave plan or message if dependencies not available
    """
    try:
        from agents.utils.project_context import get_input_file_path
        
        # Get full path
        filename_only = os.path.basename(it_inventory_file)
        full_path = get_input_file_path(filename_only)
        
        # Parse dependencies
        dependencies = parse_it_inventory_dependencies(full_path)
        
        if not dependencies.get('has_dependencies', False):
            return ("**Wave Planning**: IT Infrastructure Inventory does not contain dependency information. "
                   "Detailed wave planning requires Application Dependency, Server to Application, and "
                   "Database to Application sheets. Recommend using AWS Application Discovery Service for "
                   "automated dependency mapping.")
        
        # Build dependency graph
        dependency_graph = build_dependency_graph(dependencies)
        
        if not dependency_graph:
            return ("**Wave Planning**: No applications found in dependency data. "
                   "Please ensure Applications sheet is populated in IT Infrastructure Inventory.")
        
        # Generate waves
        waves = generate_migration_waves(dependency_graph, timeline_months)
        
        if not waves:
            return ("**Wave Planning**: Unable to generate waves from dependency data. "
                   "Please verify dependency data quality in IT Infrastructure Inventory.")
        
        # Count totals
        total_apps = len(dependency_graph)
        total_servers = len(set(
            server 
            for app_data in dependency_graph.values() 
            for server in app_data.get('servers', [])
        ))
        
        # Format as markdown
        markdown = format_wave_plan_markdown(waves, total_apps, total_servers)
        
        return markdown
        
    except Exception as e:
        return f"**Wave Planning Error**: Unable to generate wave plan from IT Infrastructure Inventory: {str(e)}"


if __name__ == "__main__":
    # Test the wave planning functions
    print("Testing Wave Planning Module...")
    
    test_file = "sample-input/it-infrastructure-inventory.xlsx"
    
    if os.path.exists(test_file):
        print(f"\nTesting with: {test_file}")
        
        # Test dependency parsing
        deps = parse_it_inventory_dependencies(test_file)
        print(f"✓ Has dependencies: {deps.get('has_dependencies', False)}")
        
        if deps.get('has_dependencies'):
            # Test graph building
            graph = build_dependency_graph(deps)
            print(f"✓ Applications in graph: {len(graph)}")
            
            # Test wave generation
            waves = generate_migration_waves(graph, 18)
            print(f"✓ Waves generated: {len(waves)}")
            
            # Test markdown formatting
            total_servers = len(set(s for app in graph.values() for s in app.get('servers', [])))
            markdown = format_wave_plan_markdown(waves, len(graph), total_servers)
            print(f"✓ Markdown generated: {len(markdown)} characters")
            print("\nSample output:")
            print(markdown[:500] + "...")
    else:
        print(f"✗ Test file not found: {test_file}")
