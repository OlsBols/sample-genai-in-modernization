"""Dependency analysis tools — builds graph, finds clusters, scores complexity.

Deterministic graph operations called directly by the orchestrator.
"""

import json
import os
import sys

from strands import tool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------------------------
# Tools — deterministic graph operations
# ---------------------------------------------------------------------------


@tool
def build_dependency_graph(discovery_result_json: str) -> str:
    """Build a directed dependency graph from discovery result.

    Extracts app names and Integrated_Apps fields to create nodes and edges.

    Args:
        discovery_result_json: JSON string of the full discovery result.

    Returns:
        JSON string with nodes (list of app names) and edges (list of {from, to}).
    """
    data = json.loads(discovery_result_json)

    apps = data.get("app_analysis", {}).get("applications", [])
    nodes = [a["name"] for a in apps]
    node_set = set(nodes)

    # integrated_apps should be a list of app NAMES (resolved by discovery agent)
    edges = []
    for a in apps:
        app_name = a["name"]
        integrated = a.get("integrated_apps", [])
        if isinstance(integrated, str) and integrated.strip():
            integrated = [d.strip() for d in integrated.split(",")]
        elif not isinstance(integrated, list):
            integrated = []

        for dep_name in integrated:
            dep_name = dep_name.strip()
            if dep_name and dep_name in node_set:
                edges.append({"from": app_name, "to": dep_name})

    return json.dumps({"nodes": nodes, "edges": edges})


@tool
def identify_clusters(graph_json: str) -> str:
    """Identify clusters, circular dependencies, and high-risk chains.

    Uses simple graph traversal — no external libraries needed.

    Args:
        graph_json: JSON string with nodes and edges from build_dependency_graph.

    Returns:
        JSON with clusters, circular_dependencies, high_risk_chains.
    """
    data = json.loads(graph_json)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    # Build adjacency lists (directed and undirected)
    adj_directed = {n: [] for n in nodes}
    adj_undirected = {n: [] for n in nodes}
    for e in edges:
        src, dst = e["from"], e["to"]
        if src in adj_directed:
            adj_directed[src].append(dst)
        if src in adj_undirected:
            adj_undirected[src].append(dst)
        if dst in adj_undirected:
            adj_undirected[dst].append(src)

    # Connected components (undirected) → clusters
    visited = set()
    clusters = []
    for node in nodes:
        if node in visited:
            continue
        component = []
        stack = [node]
        while stack:
            n = stack.pop()
            if n in visited:
                continue
            visited.add(n)
            component.append(n)
            for neighbor in adj_undirected.get(n, []):
                if neighbor not in visited:
                    stack.append(neighbor)
        if len(component) > 1:
            clusters.append({"name": f"Cluster {len(clusters) + 1}", "apps": sorted(component)})

    # Cycle detection (directed) using DFS
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    cycles = []

    def dfs_cycle(node, path):
        color[node] = GRAY
        path.append(node)
        for neighbor in adj_directed.get(node, []):
            if color.get(neighbor) == GRAY:
                # Found cycle — extract it
                idx = path.index(neighbor)
                cycle = path[idx:] + [neighbor]
                cycles.append(cycle)
            elif color.get(neighbor) == WHITE:
                dfs_cycle(neighbor, path)
        path.pop()
        color[node] = BLACK

    for node in nodes:
        if color[node] == WHITE:
            dfs_cycle(node, [])

    return json.dumps(
        {
            "clusters": clusters,
            "circular_dependencies": cycles,
            "high_risk_chains": [],  # Agent will populate from criticality data
        }
    )


@tool
def score_migration_complexity(graph_json: str) -> str:
    """Compute migration complexity score for each application.

    Score factors:
    - Number of outgoing dependencies (apps it depends on)
    - Number of incoming dependencies (apps that depend on it)
    - Whether the app is in a cycle (adds penalty)

    Args:
        graph_json: JSON string with nodes and edges.

    Returns:
        JSON dict of app_name → complexity score (0-100).
    """
    data = json.loads(graph_json)
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    out_degree = {n: 0 for n in nodes}
    in_degree = {n: 0 for n in nodes}
    for e in edges:
        out_degree[e["from"]] = out_degree.get(e["from"], 0) + 1
        in_degree[e["to"]] = in_degree.get(e["to"], 0) + 1

    # Check which nodes are in cycles
    adj = {n: [] for n in nodes}
    for e in edges:
        adj[e["from"]].append(e["to"])

    in_cycle = set()
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}

    def dfs(node, path):
        color[node] = GRAY
        path.append(node)
        for nb in adj.get(node, []):
            if color.get(nb) == GRAY:
                idx = path.index(nb)
                in_cycle.update(path[idx:])
            elif color.get(nb) == WHITE:
                dfs(nb, path)
        path.pop()
        color[node] = BLACK

    for n in nodes:
        if color[n] == WHITE:
            dfs(n, [])

    max_degree = max(max(out_degree.values(), default=1), max(in_degree.values(), default=1), 1)
    scores = {}
    for n in nodes:
        dep_score = round(((out_degree[n] + in_degree[n]) / (2 * max_degree)) * 60, 1)
        cycle_penalty = 25 if n in in_cycle else 0
        base = 15
        total = round(min(base + dep_score + cycle_penalty, 100), 1)
        scores[n] = {
            "score": total,
            "breakdown": {
                "base": base,
                "out_degree": out_degree[n],
                "in_degree": in_degree[n],
                "dep_score": dep_score,
                "cycle_penalty": cycle_penalty,
                "explanation": (
                    f"Score {total} = Base({base}) + Dependencies({dep_score}:"
                    f" {out_degree[n]} out + {in_degree[n]} in)"
                    f" + Cycle Penalty({cycle_penalty})"
                ),
            },
        }

    return json.dumps(scores)


@tool
def think(thought: str) -> str:
    """Scratchpad for agent reasoning. Returns the thought as-is."""
    return thought


@tool
def generate_dependency_findings(
    graph_json: str, clusters_json: str, scores_json: str, shared_infra_json: str
) -> str:
    """Generate data-driven key findings from dependency analysis results.

    Produces 3-6 findings about standalone apps, tightly coupled clusters,
    circular dependency risks, high-complexity blockers, and shared infra.

    Args:
        graph_json: JSON string with nodes and edges.
        clusters_json: JSON string with clusters and circular_dependencies.
        scores_json: JSON string with complexity scores per app.
        shared_infra_json: JSON string with shared infrastructure mapping.

    Returns:
        JSON array of key findings with title, detail, severity, affected_apps.
    """
    return _compute_findings(graph_json, clusters_json, scores_json, shared_infra_json)


def _compute_findings(
    graph_json: str, clusters_json: str, scores_json: str, shared_infra_json: str
) -> str:
    """Core logic for generating dependency findings — callable without @tool."""
    graph = json.loads(graph_json)
    cluster_data = json.loads(clusters_json)
    scores = json.loads(scores_json)
    shared_infra = json.loads(shared_infra_json) if shared_infra_json else {}

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    clusters = cluster_data.get("clusters", [])
    cycles = cluster_data.get("circular_dependencies", [])
    total = len(nodes)
    findings = []

    if total == 0:
        return json.dumps(findings)

    # Compute degrees
    out_deg = {n: 0 for n in nodes}
    in_deg = {n: 0 for n in nodes}
    for e in edges:
        out_deg[e["from"]] = out_deg.get(e["from"], 0) + 1
        in_deg[e["to"]] = in_deg.get(e["to"], 0) + 1

    # 1. Standalone apps (0 deps)
    standalone = [n for n in nodes if out_deg[n] == 0 and in_deg[n] == 0]
    if standalone:
        pct = round(len(standalone) / total * 100)
        findings.append(
            {
                "title": "Standalone Applications — Early Migration Candidates",
                "detail": (
                    f"{len(standalone)} of {total} apps ({pct}%) have zero dependencies,"
                    " making them ideal candidates for early migration waves"
                    " with minimal coordination required."
                ),
                "severity": "Low",
                "affected_apps": standalone,
            }
        )

    # 2. Tightly coupled clusters
    large_clusters = [c for c in clusters if len(c.get("apps", [])) >= 3]
    if large_clusters:
        apps_in_clusters = []
        for c in large_clusters:
            apps_in_clusters.extend(c["apps"])
        pct = round(len(set(apps_in_clusters)) / total * 100)
        findings.append(
            {
                "title": "Tightly Coupled Application Clusters",
                "detail": (
                    f"{len(large_clusters)} cluster(s) contain 3 or more tightly connected apps,"
                    f" affecting {len(set(apps_in_clusters))} apps ({pct}% of portfolio)."
                    " These groups must be migrated together or with careful coordination."
                ),
                "severity": "Medium",
                "affected_apps": sorted(set(apps_in_clusters)),
            }
        )

    # 3. Circular dependencies
    if cycles:
        cycle_apps = set()
        for c in cycles:
            cycle_apps.update(c[:-1] if len(c) > 1 else c)
        findings.append(
            {
                "title": "Circular Dependencies Detected",
                "detail": (
                    f"{len(cycles)} circular dependency loop(s) found involving"
                    f" {len(cycle_apps)} apps. These create migration blockers —"
                    " you cannot migrate one app without the other."
                    " Requires parallel cutover or dependency-breaking refactoring."
                ),
                "severity": "High",
                "affected_apps": sorted(cycle_apps),
            }
        )

    # 4. High-complexity blockers
    high_complexity = [
        name
        for name, data in scores.items()
        if (data.get("score", 0) if isinstance(data, dict) else data) > 70
    ]
    if high_complexity:
        pct = round(len(high_complexity) / total * 100)
        findings.append(
            {
                "title": "High-Complexity Migration Blockers",
                "detail": (
                    f"{len(high_complexity)} app(s) ({pct}% of portfolio) scored above 70"
                    " in migration complexity. These require dedicated planning,"
                    " rollback strategies, and extended testing windows."
                ),
                "severity": "High",
                "affected_apps": high_complexity,
            }
        )

    # 5. Shared infrastructure concentration
    multi_app_servers = {
        s: apps for s, apps in shared_infra.items() if isinstance(apps, list) and len(apps) > 1
    }
    if multi_app_servers:
        all_affected = set()
        for apps in multi_app_servers.values():
            all_affected.update(apps)
        findings.append(
            {
                "title": "Shared Infrastructure Concentration Risk",
                "detail": (
                    f"{len(multi_app_servers)} server(s) host multiple applications,"
                    f" affecting {len(all_affected)} apps. Migrating one app on shared"
                    " infrastructure may impact others — coordinate maintenance windows."
                ),
                "severity": "Medium",
                "affected_apps": sorted(all_affected),
            }
        )

    # 6. Most connected hub
    total_deg = {n: out_deg[n] + in_deg[n] for n in nodes}
    if total_deg:
        hub = max(total_deg, key=total_deg.get)
        if total_deg[hub] >= 3:
            findings.append(
                {
                    "title": "Central Hub Application",
                    "detail": (
                        f"{hub} is the most connected app with {total_deg[hub]} total"
                        f" connections ({out_deg[hub]} outgoing, {in_deg[hub]} incoming)."
                        " Changes to this app during migration will ripple across"
                        " dependent systems."
                    ),
                    "severity": "Medium",
                    "affected_apps": [hub],
                }
            )

    return json.dumps(findings)
