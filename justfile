# generated: 2025-12-16
# System Auto: last updated on: 2026-02-02T14:12:53
# HAIOS Justfile - Claude's Execution Toolkit
# E2-080: Wraps PowerShell scripts into clean `just <recipe>` invocations
# Pattern: "Slash commands are prompts, just recipes are execution"

# Default recipe - show help
default:
    @just --list

# =============================================================================
# GOVERNANCE RECIPES
# =============================================================================

# Validate a markdown file against HAIOS templates (E2-252: via cli.py)
validate file:
    python .claude/haios/modules/cli.py validate {{file}}

# Scaffold a new document from template (E2-252: via cli.py, E2-179: optional --spawned-by)
# Types: checkpoint, implementation_plan, investigation, report, architecture_decision_record
# Usage: just scaffold work_item E2-999 "Title" --spawned-by INV-033
scaffold type id title *args:
    python .claude/haios/modules/cli.py scaffold {{type}} {{id}} "{{title}}" {{args}}

# Aliases for common scaffold types (E2-179: pass optional args through)
plan id title *args:
    just scaffold implementation_plan {{id}} "{{title}}" {{args}}

inv id title *args:
    just scaffold investigation {{id}} "{{title}}" {{args}}

adr id title:
    just scaffold architecture_decision_record {{id}} "{{title}}"

# E2-179: work recipe accepts optional args like --spawned-by
work id title *args:
    just scaffold work_item {{id}} "{{title}}" {{args}}

checkpoint session title:
    just scaffold checkpoint {{session}} "{{title}}"

# Alias: scaffold-checkpoint for consistency with scaffold-observations (WORK-079)
scaffold-checkpoint session title:
    just checkpoint {{session}} "{{title}}"

# Move work item to a DAG node (E2-162, E2-250: Uses WorkEngine)
node id node:
    python .claude/haios/modules/cli.py transition {{id}} {{node}}

# Link a document to a work item (E2-162, E2-250: Uses WorkEngine)
link id type path:
    python .claude/haios/modules/cli.py link {{id}} {{type}} {{path}}

# Link spawned items to parent with optional milestone (E2-188, E2-250: Uses WorkEngine)
# Usage: just link-spawn INV-035 M8-SkillArch E2-180 E2-181 E2-182
link-spawn parent milestone +ids:
    python .claude/haios/modules/cli.py link-spawn {{parent}} {{milestone}} {{ids}}

# Close work item atomically (E2-215, E2-250: Uses WorkEngine)
# Combines: status update, closed date, archive move, cascade, status refresh
close-work id:
    python .claude/haios/modules/cli.py close {{id}}
    just cascade {{id}} complete
    just update-status

# Validate observation capture gate for work item (E2-217)
validate-observations id:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from observations import validate_observations; r = validate_observations('{{id}}'); print(f'Valid: {r[\"valid\"]}'); print(f'Message: {r[\"message\"]}'); sys.exit(0 if r['valid'] else 1)"

# Scaffold observations.md for work item (E2-217)
scaffold-observations id:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from observations import scaffold_observations; r = scaffold_observations('{{id}}'); print(f'Created: {r}') if r else (print('Failed: Work directory not found'), sys.exit(1))"

# Scan for work items with uncaptured observations (E2-217)
scan-observations:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from observations import scan_uncaptured_observations; r = scan_uncaptured_observations(); [print(f'{i[\"work_id\"]}: {i[\"status\"]} - {i[\"message\"]}') for i in r] if r else print('All observations captured.')"

# Triage archived observations (E2-218)
# Scans archived work items for untriaged observations and reports them
triage-observations:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from observations import scan_archived_observations; r = scan_archived_observations(); print(f'Found {len(r)} archived items with untriaged observations:'); [print(f'  {i[\"work_id\"]}: {len(i[\"observations\"])} observations') for i in r] if r else print('No untriaged observations found.')"

# Mark observation files as triaged (S205)
# Usage: just mark-triaged E2-303 E2-302 E2-301
# Adds triage_status: triaged and triage_session to frontmatter
mark-triaged +work_ids:
    python -c "import sys, json; sys.path.insert(0, '.claude/haios/lib'); from observations import mark_triaged; data = json.load(open('.claude/haios-status.json')); session = str(data.get('session_delta', {}).get('current_session', 'unknown')); [print(f'{wid}: {mark_triaged(wid, session)}') for wid in '{{work_ids}}'.split()]"

# Show governance metrics from cycle events (E2-108)
governance-metrics:
    python -c "import sys, json; sys.path.insert(0, '.claude/haios/lib'); from governance_events import get_governance_metrics; m = get_governance_metrics(); print(json.dumps(m, indent=2))"

# Update haios-status.json with current system state (Python - E2-125)
# Runs full status then slim status to keep both in sync
update-status:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from status import generate_full_status, write_full_status; full = generate_full_status(); write_full_status(full, '.claude/haios-status.json'); print('Full status updated')"
    just update-status-slim

# Update haios-status.json (dry run - preview without writing)
update-status-dry:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from status import generate_full_status; import json; full = generate_full_status(); print(json.dumps(full, indent=2)[:3000]); print('... (truncated)')"

# Update slim status only (Python - E2-120)
update-status-slim:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from status import generate_slim_status, write_slim_status; slim = generate_slim_status(); write_slim_status(slim, '.claude/haios-status-slim.json'); print('Slim status updated')"

# Cascade status change to dependent items (E2-251: Uses WorkEngine)
cascade id status:
    python .claude/haios/modules/cli.py cascade {{id}} {{status}}

# Backfill single work item from backlog (E2-251: Uses WorkEngine)
backfill id:
    python .claude/haios/modules/cli.py backfill {{id}}

# Backfill all work items from backlog (E2-251: Uses WorkEngine)
backfill-all:
    python .claude/haios/modules/cli.py backfill-all

# Force re-backfill all work items (overwrites existing content)
backfill-force:
    python .claude/haios/modules/cli.py backfill-all --force

# =============================================================================
# ETL RECIPES
# =============================================================================

# Show ETL pipeline status
status:
    python -m haios_etl.cli status

# Run memory synthesis pipeline (quick run with defaults)
synthesis:
    python -m haios_etl.cli synthesis run

# Show synthesis statistics (E2-168)
synthesis-status:
    python -m haios_etl.cli synthesis stats

# Full synthesis run for overnight/batch processing (E2-168)
# Processes ALL concepts, creates up to 500 bridges, includes cross-pollination
synthesis-full:
    python -m haios_etl.cli synthesis run --concept-sample 0 --max-bridges 500

# Run full ETL process
process:
    python -m haios_etl.cli process

# Ingest files into memory (E2-169)
ingest path:
    python -m haios_etl.cli ingest "{{path}}"

# Ingest directory recursively (E2-169)
ingest-r path:
    python -m haios_etl.cli ingest "{{path}}" -r

# Backfill synthesis embeddings (E2-169)
embeddings-backfill:
    python scripts/backfill_synthesis_embeddings.py

# Generate missing embeddings (E2-169)
embeddings-generate:
    python scripts/generate_embeddings.py

# Migrate backlog entries to work files (E2-169)
migrate-backlog:
    python scripts/migrate_backlog.py --dry-run

# Execute backlog migration (after dry-run review)
migrate-backlog-execute:
    python scripts/migrate_backlog.py

# =============================================================================
# LOADER RECIPES (WORK-007: Configuration Arc)
# =============================================================================

# Load identity context from manifesto files (CH-004)
# Extracts ~50 lines of mission, principles, constraints, epoch
identity:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from identity_loader import IdentityLoader; print(IdentityLoader().load())"

# Coldstart context loading for injection (WORK-009)
# Outputs identity content for /coldstart skill to consume
# Usage: just coldstart
coldstart:
    python .claude/haios/modules/cli.py context-load

# Load session context from latest checkpoint (CH-005)
# Extracts ~30 lines of prior session, memory refs, drift warnings, pending
session-context:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from session_loader import SessionLoader; print(SessionLoader().load())"

# Load work options context for coldstart Phase 3 (CH-006)
# Extracts ~20 lines of queue items, pending work, epoch alignment warning
work-options:
    python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from work_loader import WorkLoader; print(WorkLoader().load())"

# WORK-011: Unified coldstart with ColdstartOrchestrator
# Runs all three loaders (identity, session, work) with [BREATHE] markers
coldstart-orchestrator:
    python .claude/haios/modules/cli.py coldstart

# =============================================================================
# TESTING RECIPES
# =============================================================================

# Run all tests
test:
    pytest

# Run tests with coverage
test-cov:
    pytest --cov=haios_etl --cov-report=term-missing

# Run specific test file
test-file file:
    pytest "{{file}}" -v

# =============================================================================
# MEMORY RECIPES
# =============================================================================

# Get memory database stats
memory-stats:
    python -c "from haios_etl.database import DatabaseManager; db = DatabaseManager('haios_memory.db'); import json; print(json.dumps(db.get_stats(), indent=2))"

# Query memory via MemoryBridge (E2-253: Runtime consumer)
# Usage: just memory-query "implementation patterns"
# Modes: semantic, session_recovery, knowledge_lookup
memory-query query mode="semantic":
    python .claude/haios/modules/cli.py memory-query {{query}} --mode {{mode}}

# Load L0-L4 context via ContextLoader (E2-254: Runtime consumer)
# Usage: just context-load
context-load:
    python .claude/haios/modules/cli.py context-load

# Get phases for a cycle (E2-255: Runtime consumer)
# Usage: just cycle-phases implementation-cycle
cycle-phases cycle_id:
    python .claude/haios/modules/cli.py cycle-phases {{cycle_id}}

# Run doc-to-product pipeline (WORK-033, CH-006)
# Usage: just pipeline-run .claude/haios/config/corpus/haios-requirements.yaml
pipeline-run config:
    python .claude/haios/modules/cli.py pipeline-run {{config}}

# =============================================================================
# RHYTHM RECIPES (E2-081: Symphony - Heartbeat Scheduler)
# =============================================================================

# Heartbeat - external rhythm for the system
# Runs: synthesis, status update, event logging
# Triggered by: Windows Task Scheduler (hourly) or manually
heartbeat:
    @python -c "from datetime import datetime; print(f'HAIOS Heartbeat: {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}')"
    -python -m haios_etl.cli synthesis run --limit 20 --skip-cross
    just update-status
    @python -c "import json; from datetime import datetime; f=open('.claude/haios-events.jsonl','a'); f.write(json.dumps({'ts':datetime.now().isoformat(),'type':'heartbeat','synthesis':True})+'\n'); f.close()"
    @echo "Heartbeat complete"

# Show recent events from event log
events:
    @python -c "from pathlib import Path; p=Path('.claude/haios-events.jsonl'); print('\\n'.join(p.read_text(encoding='utf-8-sig').strip().split('\\n')[-20:]) if p.exists() else 'No events yet')"

# Clear event log (use with caution)
events-clear:
    @python -c "from pathlib import Path; p=Path('.claude/haios-events.jsonl'); p.write_text('') if p.exists() else None; print('Events cleared' if p.exists() else 'No events file')"

# Show events since a date (e.g., just events-since 2025-12-16)
events-since date:
    @python -c "import json; [print(l.strip()) for l in open('.claude/haios-events.jsonl', encoding='utf-8-sig') if json.loads(l)['ts'] >= '{{date}}']"

# Show event counts by type
events-stats:
    @python -c "import json,collections; c=collections.Counter(json.loads(l)['type'] for l in open('.claude/haios-events.jsonl', encoding='utf-8-sig')); print(dict(c))"

# Show recent cycle transitions (E2-097)
cycle-events:
    @python -c "import json; [print(f\"{e['backlog_id']}: {e.get('from_phase','?')} -> {e['to_phase']} (S{e.get('session',0)})\") for l in open('.claude/haios-events.jsonl', encoding='utf-8-sig') if (e:=json.loads(l))['type']=='cycle_transition'][-10:]"

# Start new session: write to .claude/session, update status.json, log event
# CH-002: Session Simplify - session number in simple file
# E2-306: Now calls log_session_start() for orphan detection support
session-start session:
    @python -c "import json,os,sys; sys.path.insert(0,'.claude/haios/lib'); from governance_events import log_session_start; sf='.claude/session'; jf='.claude/haios-status.json'; s={{session}}; lines=open(sf).readlines() if os.path.exists(sf) else []; hdr=[l for l in lines if l.startswith('#')]; open(sf,'w').write(''.join(hdr)+str(s)+chr(10)); j=json.load(open(jf)) if os.path.exists(jf) else {}; pr=j.get('session_delta',{}).get('current_session',s-1); j['session_delta']={'current_session':s,'prior_session':pr}; json.dump(j,open(jf,'w'),indent=2); log_session_start(s,'Hephaestus'); print(f'Session {s} start logged')"

# Log session end event
# E2-306: Now calls log_session_end() for orphan detection support
session-end session:
    @python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from governance_events import log_session_end; log_session_end({{session}},'Hephaestus'); print('Session {{session}} end logged')"

# Set session_state for cycle tracking (E2-288)
# Usage: just set-cycle implementation-cycle DO E2-288
set-cycle cycle phase work_id:
    @python -c "import json; from datetime import datetime; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']={'active_cycle':'{{cycle}}','current_phase':'{{phase}}','work_id':'{{work_id}}','entered_at':datetime.now().isoformat()}; json.dump(d,open(p,'w'),indent=4); print(f'Set: {{cycle}}/{{phase}}/{{work_id}}')"

# Get current cycle state (E2.4 CH-004 PreToolUseIntegration)
# Returns: cycle/phase/work_id or empty string if no cycle active
get-cycle:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); s=d.get('session_state',{}); c=s.get('active_cycle') or ''; p=s.get('current_phase') or ''; w=s.get('work_id') or ''; print(f'{c}/{p}/{w}' if c else '')"

# Clear session_state after cycle exit (E2-288, E2-293)
clear-cycle:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']={'active_cycle':None,'current_phase':None,'work_id':None,'entered_at':None,'active_queue':None,'phase_history':[]}; json.dump(d,open(p,'w'),indent=4); print('Cleared session_state')"

# Set active_queue in session_state (E2-293)
# Usage: just set-queue governance
set-queue queue_name:
    @python -c "import json; p='.claude/haios-status-slim.json'; d=json.load(open(p)); d['session_state']['active_queue']='{{queue_name}}'; json.dump(d,open(p,'w'),indent=4); print(f'Set queue: {{queue_name}}')"

# =============================================================================
# PLAN TREE RECIPES (E2-084)
# =============================================================================

# Show milestone progress and plan tree
tree:
    python scripts/plan_tree.py

# Show only current (active) milestone
tree-current:
    python -c "import sys, json; sys.path.insert(0, '.claude/haios/lib'); s=json.load(open('.claude/haios-status-slim.json')); m=s.get('milestone',{}); print(f'{m.get(\"id\",\"?\")}: {m.get(\"progress\",0)}%'); import subprocess; subprocess.run(['python', 'scripts/plan_tree.py', '--milestone', m.get('id','')])"

# Show what's ready to work on (unblocked items)
ready:
    python scripts/plan_tree.py --ready

# Show work queue (E2-290: Priority ordered)
queue name="default":
    python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from work_engine import WorkEngine; from governance_layer import GovernanceLayer; e=WorkEngine(governance=GovernanceLayer()); items=e.get_queue('{{name}}'); print(f'Queue: {{name}} ({len(items)} items)'); [print(f'  {i+1}. {x.id}: {x.title} (priority={x.priority})') for i,x in enumerate(items[:10])]"

# Show next item from queue (E2-290)
queue-next name="default":
    python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from work_engine import WorkEngine; from governance_layer import GovernanceLayer; e=WorkEngine(governance=GovernanceLayer()); n=e.get_next('{{name}}'); print(f'Next: {n.id}: {n.title}' if n else 'Queue empty')"

# Check if cycle is allowed for queue (E2-290)
queue-check name cycle:
    python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from work_engine import WorkEngine; from governance_layer import GovernanceLayer; e=WorkEngine(governance=GovernanceLayer()); ok=e.is_cycle_allowed('{{name}}', '{{cycle}}'); print(f'{{cycle}} allowed on {{name}}: {ok}')"

# Check if cycle is allowed - returns ALLOWED/BLOCKED (E2-291)
is-cycle-allowed queue_name cycle_name:
    python -c "import sys; sys.path.insert(0, '.claude/haios/modules'); from work_engine import WorkEngine; from governance_layer import GovernanceLayer; e=WorkEngine(governance=GovernanceLayer()); allowed=e.is_cycle_allowed('{{queue_name}}', '{{cycle_name}}'); print('ALLOWED' if allowed else 'BLOCKED')"

# Show spawn tree for an ID (E2-251: Uses WorkEngine)
spawns id:
    python .claude/haios/modules/cli.py spawn-tree {{id}}

# =============================================================================
# UTILITY RECIPES
# =============================================================================

# Show git status
git-status:
    git status

# Show recent commits
git-log:
    git log --oneline -10

# Quick health check (tests + git status)
health:
    @echo "=== Tests ==="
    pytest -q
    @echo ""
    @echo "=== Git Status ==="
    git status -s

# Get most recent checkpoint filename (E2-205)
checkpoint-latest:
    @python -c "import os; files = [(f, os.path.getmtime(os.path.join('docs/checkpoints', f))) for f in os.listdir('docs/checkpoints') if f.endswith('.md') and 'SESSION' in f]; files.sort(key=lambda x: x[1], reverse=True); print(files[0][0] if files else 'None')"

# =============================================================================
# GIT COMMIT RECIPES (E2-167)
# =============================================================================

# Commit session checkpoint and related changes
# Usage: just commit-session 113 "M7a-Recipes progress"
commit-session session title:
    git add docs/checkpoints/ docs/work/ .claude/haios-status*.json justfile
    git commit -m "Session {{session}}: {{title}}"

# Commit work item closure (work file + plan + investigation)
# Usage: just commit-close E2-168
commit-close id:
    git add "docs/work/archive/WORK-{{id}}-*" "docs/plans/PLAN-{{id}}*" "docs/investigations/INVESTIGATION-{{id}}*" .claude/haios-status*.json
    git commit -m "Close {{id}}"

# Stage all HAIOS governance files
stage-governance:
    git add docs/work/ docs/plans/ docs/investigations/ docs/checkpoints/ .claude/haios-status*.json justfile

# =============================================================================
# AUDIT RECIPES (E2-143)
# =============================================================================

# Audit: Find investigations active but work archived
audit-sync:
    @python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from audit import audit_sync; [print(i) for i in audit_sync()]"

# Audit: Find work items with complete plans but still active
audit-gaps:
    @python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from audit import audit_gaps; [print(i) for i in audit_gaps()]"

# Audit: Find investigations older than 10 sessions
audit-stale:
    @python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from audit import audit_stale; [print(i) for i in audit_stale()]"

# Audit: Validate decision-to-chapter traceability (WORK-069)
audit-decision-coverage:
    @python .claude/haios/lib/audit_decision_coverage.py
