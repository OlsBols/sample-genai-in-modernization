"""Graph-based orchestrator for Discovery → Dependency assessment."""

import json
import os
import re
import sys
from collections.abc import AsyncIterator

from strands.multiagent import GraphBuilder

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dependency_agent import (
    _compute_findings,
    build_dependency_graph,
    identify_clusters,
    score_migration_complexity,
)
from discovery_agent import (
    create_app_analysis_agent,
    create_infra_analysis_agent,
    create_summary_agent,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sse(event: str, data: str) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _extract_json(text: str) -> dict | None:
    """Extract first JSON object from text."""
    for attempt in [
        text.strip(),
        re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip(),
    ]:
        try:
            return json.loads(attempt)
        except json.JSONDecodeError:
            pass
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _build_shared_infrastructure(infra_analysis: dict | None) -> tuple[dict, str]:
    """Build shared_infrastructure map. Returns (dict, status)."""
    if not infra_analysis or not infra_analysis.get("components"):
        return {}, "no_infra_data"

    server_apps: dict[str, list[str]] = {}
    for comp in infra_analysis["components"]:
        srv = comp.get("server_name") or comp.get("name") or ""
        hosted = comp.get("hosted_apps", [])
        if isinstance(hosted, str):
            hosted = [h.strip() for h in hosted.split(",") if h.strip()]
        if srv and hosted:
            server_apps.setdefault(srv, [])
            for app in hosted:
                if app not in server_apps[srv]:
                    server_apps[srv].append(app)

    if not server_apps or all(len(v) <= 1 for v in server_apps.values()):
        return server_apps, "no_shared_servers"
    return server_apps, "found"


def _build_executive_summary(app_analysis: dict | None, infra_analysis: dict | None) -> dict:
    """Build executive_summary deterministically."""
    apps = (app_analysis or {}).get("applications", [])
    app_summary = (app_analysis or {}).get("app_summary", {})
    total_apps = len(apps)
    total_infra = len((infra_analysis or {}).get("components", []))

    has_high = any(a.get("criticality") == "High" and a.get("risk_signals") for a in apps)
    risk_level = (
        "High" if has_high else ("Medium" if app_summary.get("high_risk_count", 0) else "Low")
    )

    ready = sum(1 for a in apps if not a.get("risk_signals"))
    needs_work = sum(1 for a in apps if a.get("risk_signals") and a.get("criticality") != "High")
    high_risk = total_apps - ready - needs_work

    findings = []
    risk_apps = [a["name"] for a in apps if a.get("risk_signals")]
    if risk_apps:
        pct = round(len(risk_apps) / total_apps * 100) if total_apps else 0
        findings.append(
            {
                "title": "Applications with Risk Signals",
                "detail": f"{len(risk_apps)} of {total_apps} apps ({pct}%) have risk signals.",
                "severity": "High" if len(risk_apps) > total_apps * 0.3 else "Medium",
                "affected_apps": risk_apps,
            }
        )
    legacy = [a["name"] for a in apps if a.get("type") == "Legacy"]
    if legacy:
        findings.append(
            {
                "title": "Legacy Applications",
                "detail": f"{len(legacy)} legacy app(s) may need modernization.",
                "severity": "Medium",
                "affected_apps": legacy,
            }
        )

    return {
        "total_applications": total_apps,
        "total_infrastructure": total_infra,
        "overall_risk_level": risk_level,
        "key_findings": findings,
        "migration_readiness": {
            "summary": f"{ready} ready, {needs_work} need work, {high_risk} high-risk.",
            "ready_count": ready,
            "needs_work_count": needs_work,
            "high_risk_count": high_risk,
            "readiness_pct": round(ready / total_apps * 100) if total_apps else 0,
        },
    }


def _run_dependency_analysis(app_analysis: dict, infra_analysis: dict | None) -> dict:
    """Run all dependency tools and assemble result. Pure Python, no LLM."""
    discovery = {"app_analysis": app_analysis, "infra_analysis": infra_analysis}
    discovery_json = json.dumps(discovery)

    graph_json = build_dependency_graph(discovery_result_json=discovery_json)
    clusters_json = identify_clusters(graph_json=graph_json)
    scores_json = score_migration_complexity(graph_json=graph_json)

    shared_infra, shared_status = _build_shared_infrastructure(infra_analysis)

    findings_json = _compute_findings(
        graph_json, clusters_json, scores_json, json.dumps(shared_infra)
    )

    graph_data = json.loads(graph_json)
    clusters_data = json.loads(clusters_json)
    scores_data = json.loads(scores_json)

    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    out_deg = {n: 0 for n in nodes}
    in_deg = {n: 0 for n in nodes}
    for e in edges:
        out_deg[e["from"]] = out_deg.get(e["from"], 0) + 1
        in_deg[e["to"]] = in_deg.get(e["to"], 0) + 1

    cycles = clusters_data.get("circular_dependencies", [])
    cycle_apps = set()
    for c in cycles:
        cycle_apps.update(c[:-1] if len(c) > 1 else c)

    # Cluster risk + wave assignment
    clusters_out = []
    for cl in clusters_data.get("clusters", []):
        cl_apps = cl.get("apps", [])
        has_cycle = any(a in cycle_apps for a in cl_apps)
        has_high = any(
            isinstance(scores_data.get(a), dict) and scores_data[a].get("score", 0) > 70
            for a in cl_apps
        )
        if has_cycle or has_high:
            risk, wave = "High", "Wave 3"
        elif len(cl_apps) > 3:
            risk, wave = "Medium", "Wave 2"
        else:
            risk, wave = "Low", "Wave 1"
        clusters_out.append({**cl, "risk_level": risk, "suggested_wave": wave})

    total_deg = {n: out_deg[n] + in_deg[n] for n in nodes}
    return {
        "graph": graph_data,
        "clusters": clusters_out,
        "circular_dependencies": cycles,
        "complexity_scores": scores_data,
        "shared_infrastructure": shared_infra,
        "shared_infrastructure_status": shared_status,
        "key_findings": json.loads(findings_json),
        "dependency_summary": {
            "total_apps": len(nodes),
            "total_edges": len(edges),
            "standalone_count": sum(1 for n in nodes if out_deg[n] == 0 and in_deg[n] == 0),
            "avg_dependencies": round(len(edges) / len(nodes), 1) if nodes else 0,
            "most_connected_app": max(total_deg, key=total_deg.get) if total_deg else "",
            "migration_blockers": [
                n
                for n in cycle_apps
                if isinstance(scores_data.get(n), dict) and scores_data[n].get("score", 0) > 60
            ],
        },
    }


# ---------------------------------------------------------------------------
# SSE labels
# ---------------------------------------------------------------------------

_NODE_START = {
    "app_analysis": "📊 Analyzing applications...",
    "infra_analysis": "🖥️ Analyzing infrastructure...",
}
_NODE_STOP = {
    "app_analysis": "✅ Application analysis complete",
    "infra_analysis": "✅ Infrastructure analysis complete",
}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


async def run_assessment(app_csv_path: str, infra_csv_path: str | None) -> AsyncIterator[str]:
    """Run assessment with parallel discovery via GraphBuilder, then dependency in Python."""
    yield _sse("lifecycle", "📋 Starting assessment...")

    # Read CSVs
    try:
        with open(app_csv_path, encoding="utf-8") as f:
            app_csv = f.read()
    except Exception as e:
        yield _sse("error", f"Failed to read app CSV: {e}")
        return

    infra_csv = None
    if infra_csv_path:
        try:
            with open(infra_csv_path, encoding="utf-8") as f:
                infra_csv = f.read()
        except Exception as e:
            yield _sse("error", f"Failed to read infra CSV: {e}")
            return

    # Create agents
    app_agent = create_app_analysis_agent(app_csv)
    has_infra = infra_csv is not None

    # Build graph — parallel app + infra analysis
    builder = GraphBuilder()
    builder.add_node(app_agent, "app_analysis")
    builder.set_entry_point("app_analysis")

    if has_infra:
        infra_agent = create_infra_analysis_agent(infra_csv)
        builder.add_node(infra_agent, "infra_analysis")
        builder.set_entry_point("infra_analysis")

    builder.set_execution_timeout(300)
    graph = builder.build()

    # Stream graph and collect results
    app_analysis = None
    infra_analysis = None

    try:
        async for event in graph.stream_async(
            "Analyze the data in your system prompt and return the JSON result."
        ):
            etype = event.get("type", "")

            if etype == "multiagent_node_start":
                label = _NODE_START.get(event.get("node_id"))
                if label:
                    yield _sse("lifecycle", label)

            elif etype == "multiagent_node_stop":
                nid = event.get("node_id", "")
                nr = event.get("node_result")
                if nr:
                    data = _extract_json(str(nr.result))
                    if nid == "app_analysis":
                        app_analysis = data
                    elif nid == "infra_analysis":
                        infra_analysis = data

                label = _NODE_STOP.get(nid)
                if label:
                    yield _sse("lifecycle", label)

    except Exception as e:
        yield _sse("error", f"Discovery failed: {str(e)}")
        return

    if not app_analysis:
        yield _sse("error", "Could not parse app analysis result")
        return

    # Send partial result so IT Discovery tab populates immediately
    partial = {
        "discovery": {
            "app_analysis": app_analysis,
            "infra_analysis": infra_analysis,
            "executive_summary": _build_executive_summary(app_analysis, infra_analysis),
        },
        "dependency": None,
        "metadata": {"status": "partial"},
    }
    yield _sse("partial", json.dumps(partial))

    # Dependency analysis — pure Python
    yield _sse("lifecycle", "🔗 Building dependency graph...")
    try:
        dependency = _run_dependency_analysis(app_analysis, infra_analysis)
    except Exception as e:
        yield _sse("lifecycle", f"⚠️ Dependency analysis failed: {str(e)}")
        dependency = None
    yield _sse("lifecycle", "✅ Dependency analysis complete")

    # Summary agent — LLM enriches dependency with narrative content
    if dependency:
        try:
            summary_input = json.dumps(
                {
                    "app_analysis": app_analysis,
                    "infra_analysis": infra_analysis,
                    "dependency": dependency,
                }
            )
            summary_agent, summary_task = create_summary_agent(summary_input)

            summary_text = ""
            async for event in summary_agent.stream_async(summary_task):
                if "data" in event:
                    summary_text += event["data"]

            summary_data = _extract_json(summary_text)
            if summary_data:
                rationale = summary_data.get("migration_rationale", {})
                for app_name, text in rationale.items():
                    if app_name in dependency.get("complexity_scores", {}):
                        dependency["complexity_scores"][app_name]["migration_rationale"] = text

                if summary_data.get("circular_dependencies_detail"):
                    dependency["circular_dependencies_detail"] = summary_data[
                        "circular_dependencies_detail"
                    ]

                if summary_data.get("executive_summary"):
                    exec_summary = summary_data["executive_summary"]
                else:
                    exec_summary = _build_executive_summary(app_analysis, infra_analysis)
            else:
                exec_summary = _build_executive_summary(app_analysis, infra_analysis)
        except Exception:
            exec_summary = _build_executive_summary(app_analysis, infra_analysis)
    else:
        exec_summary = _build_executive_summary(app_analysis, infra_analysis)

    # Assemble final result
    assessment = {
        "discovery": {
            "app_analysis": app_analysis,
            "infra_analysis": infra_analysis,
            "executive_summary": exec_summary,
        },
        "dependency": dependency,
        "metadata": {"status": "complete" if dependency else "partial"},
    }

    yield _sse("done", json.dumps(assessment))
