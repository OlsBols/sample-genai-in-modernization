"""Wave Runbook Agent prompt — generates operational runbook for Wave 1, 1 app."""


def get_wave_runbook_prompt(
    assessment_json: str,
    strategy_json: str,
    landing_zone_json: str,
) -> str:
    return f"""You are an AWS Migration Specialist. Generate a concise Wave 1 Runbook.

## Context

Assessment: {assessment_json}
Strategy: {strategy_json}
Landing Zone: {landing_zone_json}

## Rules

- Focus on Wave 1 only
- Pick the FIRST application from Wave 1 for detailed steps
- Keep each section SHORT — 5-10 bullet points max
- Use markdown tables where appropriate (3-5 rows max)
- Use simple bullet lists (- item), NOT checkbox lists
- Do NOT use #### sub-headings — keep content flat under each ## section
- Do NOT use bold markers (**text**) excessively — only for app names
- Keep total output under 2000 words

## Output — use exactly these ## headings

## Inventory Summary
5 bullet points Data driven executive summary from provided assessment report

## Migration and Modernization Strategy
 5 bullet points Data driven executive summary from provided Strategy

## Pre-Migration Checklist

5 bullet points covering environment readiness, backups, sign-offs.

## Replication and Staging

3-5 steps for the selected app: DMS setup, staging config, validation.

## Test Cutover

5 numbered steps with expected duration per step. Include Go/No-Go criteria.

## Cutover Execution

5 numbered steps with timestamps (T+0, T+30min, etc). DNS changes, service switchover.

## Rollback Plan

3-5 bullet points: triggers, steps, max rollback window.

## Post-Migration Validation

5 bullet points: health checks, performance, data integrity, integration tests.

## Cleanup and Optimization

3-5 bullet points: decommission source, DNS finalize, cost optimization.

## Communication Plan

Simple table: Phase | Audience | Channel | Timing

## Timeline

Simple table: Activity | Start | End | Owner
"""
