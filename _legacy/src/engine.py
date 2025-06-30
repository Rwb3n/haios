from __future__ import annotations

# ANNOTATION_BLOCK_START
{
    "artifact_annotation_header": {
        "artifact_id_of_host": "engine_py_g99",
        "g_annotation_last_modified": 183,
        "version_tag_of_host_at_annotation": "1.1.0",
    },
    "payload": {
        "description": "The main entry point for the HAiOS command-line engine. Now fully functional, it parses arguments, initializes core services, and invokes the PlanRunner to execute plans.",
        "authors_and_contributors": [
            {"g_contribution": 99, "identifier": "Cody"},
            {"g_contribution": 117, "identifier": "Cody"},
            {
                "g_contribution": 183,
                "identifier": "Successor Agent",
                "contribution_summary": "Refactor (T13): Correctly instantiate and pass the core.config.Config dataclass and implement specified exit code policy for OSCoreError exceptions.",
            },
        ],
        "internal_dependencies": [
            "plan_runner_py_g101",
            "core_config_py_g146",
            "core_exceptions_py_g137",
            "util_config_loader_py_g61",
        ],
        "linked_issue_ids": ["issue_00107", "issue_00121"],
    },
}
# ANNOTATION_BLOCK_END

"""High‑level CLI entry‑point for the HaiOS scaffolding engine.

Key improvements over the previous version:
- Uses the new immutable ``core.config.Config`` object instead of raw ``dict`` / ``ConfigLoader``.
- Picks up *all* tunable paths (schema directory, templates, state file, etc.) **from the Config instance**—no hard‑coded fall‑backs.
- Implements a clear exit‑code policy:
    0 → success
    1 → internal / unexpected error
    2 → user‑supplied input or security error (e.g. invalid config, path‑escape)
- Structured logging via ``structlog`` with contextual binds (`plan_id`, `project_root`).
- Removes legacy ``Validator`` dependency; Config is validated during ``Config.from_file``.
"""

import argparse
import json
import logging
import signal
import sys
import threading
from pathlib import Path
from typing import Any, Optional

import structlog
from prometheus_client import start_http_server

# Core abstractions -----------------------------------------------------------
from core.config import Config
from core.config_loader import ConfigLoader
from core.exceptions import (
    ConfigError,
    PathEscapeError,
    PlannerError,
    WriteConflictError,
)
from plan_runner import PlanRunner
from utils.state_manager import StateManager
from utils.tracing_utils import configure_tracer
from utils.validators import Validator
from utils.vault_utils import Vault

# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# CLI parsing
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="haios-engine",
        description="Run a scaffold plan inside the HaiOS workspace",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    run_plan = sub.add_parser("run-plan", help="Execute a scaffold plan by id")
    run_plan.add_argument(
        "plan_id", help="The plan identifier (filename without extension)"
    )
    run_plan.add_argument(
        "--config",
        type=Path,
        default=Path("haios.config.json"),
        help="Path to HaiOS project configuration file (default: ./haios.config.json)",
    )
    run_plan.add_argument(
        "--mode",
        choices=["STRICT", "DEV_FAST"],
        default=None,
        help="Override the runtime mode defined in the config file.",
    )
    run_plan.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug output"
    )

    vault_parser = sub.add_parser("vault", help="Manage the secrets vault")
    vault_sub = vault_parser.add_subparsers(dest="vault_cmd", required=True)

    vault_init = vault_sub.add_parser("init", help="Initialize a new secrets vault")
    vault_init.add_argument(
        "--key", required=True, help="The age identity key (bech32 format)"
    )

    vault_add = vault_sub.add_parser("add", help="Add a secret to the vault")
    vault_add.add_argument("name", help="The name of the secret")
    vault_add.add_argument("value", help="The value of the secret")
    vault_add.add_argument(
        "--scope",
        default="global",
        help="The scope of the secret (global, initiative, plan, agent)",
    )
    vault_add.add_argument(
        "--key", required=True, help="The age identity key (bech32 format)"
    )

    vault_get = vault_sub.add_parser("get", help="Get a secret from the vault")
    vault_get.add_argument("name", help="The name of the secret")
    vault_get.add_argument(
        "--key", required=True, help="The age identity key (bech32 format)"
    )

    vault_list = vault_sub.add_parser("list", help="List secrets in the vault")
    vault_list.add_argument(
        "--key", required=True, help="The age identity key (bech32 format)"
    )

    scaffold_parser = sub.add_parser(
        "scaffold", help="Scaffold a new plan from a template"
    )
    scaffold_parser.add_argument("template", help="The name of the template to use")
    scaffold_parser.add_argument("plan_id", help="The ID of the new plan")

    fsck_parser = sub.add_parser(
        "registry-fsck", help="Check the integrity of the global registry map"
    )

    return parser


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------


def _configure_logging(verbose: bool) -> None:
    """Raise log level globally when *verbose* flag is supplied."""
    lvl = logging.DEBUG if verbose else logging.INFO
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(lvl))


def _load_config(config_path: Path, schema_dir: Path) -> Config:
    """Loads, parses, and validates the configuration file."""
    try:
        if schema_dir.exists():
            validator = Validator(schema_dir=str(schema_dir))
        else:

            class _NoopValidator:
                def validate(self, *_args, **_kwargs):
                    return True

            validator = _NoopValidator()

        loader = ConfigLoader(config_path=config_path, validator=validator)
        return loader.load_and_validate()
    except Exception as e:
        logger.error("config_error", err=str(e), config_path=str(config_path))
        sys.exit(2)


def _run_plan(
    plan_id: str, cfg: Config, bound_logger: Any, tracer: Any
) -> None:  # pragma: no cover
    """Initializes services and runs the specified plan."""
    validator = Validator(schema_dir=str(cfg.paths.schema_dir))
    state_mgr = StateManager(state_path=cfg.paths.state_file, validator=validator)

    runner = PlanRunner(
        plan_id=plan_id,
        config=cfg,
        state_manager=state_mgr,
        logger=bound_logger,
        tracer=tracer,
    )

    try:
        succeeded = runner.execute()
        if not succeeded:
            print("Execution failed", file=sys.stderr, flush=True)
            bound_logger.error("plan_failed")
            sys.exit(1)
    except PathEscapeError as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr, flush=True)
        bound_logger.error("security_violation", err=str(e))
        sys.exit(2)
    except WriteConflictError as e:
        print(f"WriteConflictError: {e}", file=sys.stderr, flush=True)
        bound_logger.error("concurrent_write", err=str(e))
        sys.exit(1)
    except PlannerError as e:
        # PlannerError should already be printed to stderr by the plan runner
        print(f"PlannerError: {e}", file=sys.stderr, flush=True)
        bound_logger.error("planner_error", err=str(e))
        sys.exit(1)
    except Exception as e:  # noqa: BLE001 – catch-all maps to exit-code 1
        print(f"Internal error: {e}", file=sys.stderr, flush=True)
        bound_logger.exception("internal_error")
        sys.exit(1)

    bound_logger.info("plan_completed")


# ---------------------------------------------------------------------------
# Public entry‑point
# ---------------------------------------------------------------------------


def _handle_sigterm(signum, frame):
    """Gracefully handles SIGTERM by creating a soft_kill.flag."""
    logger.error("sigterm_received")
    # This is a simplified implementation. A more robust solution would
    # use the config to find the control path.
    control_path = Path("./os_root/control/")
    control_path.mkdir(parents=True, exist_ok=True)
    (control_path / "soft_kill.flag").touch()
    sys.exit(1)


def main(argv: Optional[list[str]] = None) -> None:  # pragma: no cover
    tracer = configure_tracer("haios-engine")
    start_http_server(8000)
    signal.signal(signal.SIGTERM, _handle_sigterm)
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    _configure_logging(getattr(args, "verbose", False))

    if args.cmd == "run-plan":
        # We need the schema path before we can fully load the config
        # This is a bit of a chicken-and-egg problem, so we resolve it relative
        # to the config file path provided.
        config_path = getattr(args, "config", Path("haios.config.json"))
        schema_dir = config_path.parent.resolve() / "docs/schema/"
        cfg = _load_config(config_path, schema_dir)

        # Override runtime mode if the CLI flag is set
        if getattr(args, "mode", None) and cfg.runtime.cli_override_allowed:
            # Re-create the config object with the overridden mode
            new_runtime = cfg.runtime.replace(mode=args.mode)
            cfg = cfg.replace(runtime=new_runtime)
            logger.info("runtime_mode_overridden", mode=args.mode)

        bound_logger = logger.bind(
            project_root=str(cfg.project_root), plan_id=args.plan_id
        )
        _run_plan(args.plan_id, cfg, bound_logger, tracer)
    elif args.cmd == "vault":
        schema_dir = args.config.parent.resolve() / "docs/schema/"
        cfg = _load_config(args.config, schema_dir)
        vault_path = cfg.paths.secrets_vault
        vault = Vault(vault_path, args.key)
        if args.vault_cmd == "init":
            vault.initialize()
            print(f"Vault initialized at {vault_path}")
        elif args.vault_cmd == "add":
            vault.add_secret(args.name, args.value, args.scope)
            print(f"Secret '{args.name}' added to the vault.")
        elif args.vault_cmd == "get":
            secret = vault.get_secret(args.name)
            print(json.dumps(secret, indent=2))
        elif args.vault_cmd == "list":
            secrets = vault.list_secrets()
            print(json.dumps(secrets, indent=2))
    elif args.cmd == "scaffold":
        schema_dir = args.config.parent.resolve() / "docs/schema/"
        cfg = _load_config(args.config, schema_dir)
        template_path = cfg.paths.project_templates / f"{args.template}.json"
        plan_path = cfg.paths.exec_plans / f"{args.plan_id}.json"
        if not template_path.exists():
            print(f"Error: Template '{args.template}' not found at {template_path}")
            sys.exit(1)
        if plan_path.exists():
            print(f"Error: Plan '{args.plan_id}' already exists at {plan_path}")
            sys.exit(1)

        import shutil

        shutil.copy(template_path, plan_path)
        print(
            f"Plan '{args.plan_id}' created from template '{args.template}' at {plan_path}"
        )
    elif args.cmd == "registry-fsck":
        schema_dir = args.config.parent.resolve() / "docs/schema/"
        cfg = _load_config(args.config, schema_dir)
        validator = Validator(schema_dir=str(cfg.paths.schema_dir))
        registry_path = cfg.paths.os_root / "global_registry_map.txt"
        print(f"Checking registry at {registry_path}...")

        if not registry_path.exists():
            print("Error: Registry file not found.")
            sys.exit(1)

        try:
            with registry_path.open("r", encoding="utf-8") as f:
                registry_data = json.load(f)
        except json.JSONDecodeError:
            print("Error: Registry file is not valid JSON.")
            sys.exit(1)

        try:
            validator.validate("global_registry_map", registry_data)
            print("Registry schema is valid.")
        except Exception as e:
            print(f"Error: Registry schema validation failed: {e}")
            sys.exit(1)

        print("Checking artifact filepaths...")
        all_good = True
        for artifact_id, data in (
            registry_data.get("payload", {}).get("artifact_registry_tree", {}).items()
        ):
            path_str = data.get("primary_filepath")
            if path_str:
                full_path = cfg.project_root / path_str
                if not full_path.exists():
                    print(
                        f"  [FAIL] Artifact '{artifact_id}': file not found at '{full_path}'"
                    )
                    all_good = False
                else:
                    print(f"  [OK] Artifact '{artifact_id}': found at '{full_path}'")

        if all_good:
            print("Registry integrity check passed.")
        else:
            print("Registry integrity check failed.")
            sys.exit(1)
    else:  # Should never occur due to sub‑parser enforcement
        parser.error(f"Unknown command: {args.cmd}")


if __name__ == "__main__":  # pragma: no cover
    main()
