"""CLI entry point using Click."""

from pathlib import Path
from typing import Literal

import click

from stfwb.steps.runner import run_steps
from stfwb.utils.storage import (
    DEFAULT_STORE_DIR,
    delete_iteration,
    delete_project,
    load_all_iterations,
    load_all_projects,
    load_iteration,
    load_project,
    save_iteration,
    save_project,
)


@click.group()
@click.version_option(version="0.1.0-beta")
@click.option("-v", "verbose", count=True, help="Increase verbosity (-v=INFO, -vv=DEBUG)")
@click.option("--quiet", "-q", "quiet", is_flag=True, help="Quiet mode (errors only)")
@click.option(
    "--log-file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    help="Write logs to file",
)
@click.pass_context
def cli(ctx: click.Context, verbose: int, quiet: bool, log_file: Path | None) -> None:
    """STF-WB: Reference implementation of STF-Workbench v0.2.0."""
    from stfwb.utils.config import get_config
    from stfwb.utils.logging import setup_logging

    cfg = get_config()
    # Use provided flags first, then fall back to config file values
    eff_verbose = verbose if verbose > 0 else cfg.verbose
    eff_quiet = quiet or cfg.quiet
    eff_log_file = log_file or (Path(cfg.log_file) if cfg.log_file else None)

    if eff_quiet:
        setup_logging("ERROR", eff_log_file)
    elif eff_verbose >= 2:
        setup_logging("DEBUG", eff_log_file)
    elif eff_verbose == 1:
        setup_logging("INFO", eff_log_file)
    else:
        setup_logging("WARNING", eff_log_file)

    ctx.ensure_object(dict)
    ctx.obj["verbose"] = eff_verbose
    ctx.obj["quiet"] = eff_quiet
    ctx.obj["log_file"] = eff_log_file
    ctx.obj["config"] = cfg


def _get_log_level(ctx: click.Context, cmd_verbose: int | None, cmd_quiet: bool | None) -> str:
    """Compute effective log level from global and command-level overrides."""
    if cmd_quiet:
        return "ERROR"
    if cmd_verbose and cmd_verbose >= 2:
        return "DEBUG"
    if cmd_verbose == 1:
        return "INFO"

    global_verbose = ctx.obj.get("verbose", 0) if ctx.obj else 0
    global_quiet = ctx.obj.get("quiet", False) if ctx.obj else False
    if global_quiet:
        return "ERROR"
    if global_verbose >= 2:
        return "DEBUG"
    if global_verbose == 1:
        return "INFO"
    return "WARNING"


@cli.group()
def project() -> None:
    """Manage projects."""
    pass


@project.command(name="create")
@click.option("--name", required=True, help="Project name")
@click.option("--target-uri", required=True, help="Target specification URI")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Local storage directory",
)
@click.option("-v", "verbose", count=True, help="Override global verbosity")
@click.option("--quiet", "-q", "quiet", is_flag=True, help="Override to quiet")
@click.pass_context
def project_create(
    ctx: click.Context,
    name: str,
    target_uri: str,
    store_dir: Path | None,
    verbose: int,
    quiet: bool,
) -> None:
    """Create a new project."""
    from stfwb.core.project import Project
    from stfwb.utils.logging import setup_logging

    # Use provided store-dir or fall back to config
    if store_dir is None:
        cfg = ctx.obj.get("config") if ctx.obj else None  # pragma: no cover
        store_dir = (
            Path(cfg.store_dir) if cfg and cfg.store_dir else Path(DEFAULT_STORE_DIR)
        )  # pragma: no cover

    level = _get_log_level(ctx, verbose or None, quiet or None)
    log_file = ctx.obj.get("log_file") if ctx.obj else None
    setup_logging(level, log_file)  # type: ignore[arg-type]

    project = Project(name=name, target_uri=target_uri)  # type: ignore[call-arg]
    click.echo(f"Creating project '{name}' targeting {target_uri}")
    out_path = save_project(project, store_dir)
    click.echo(f"Created project '{name}' (id={project.id}) at {out_path}")


@project.command(name="list")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--name-contains", "name_contains", help="Filter by name substring")
def project_list(store_dir: Path, output_json: bool, name_contains: str | None) -> None:
    """List projects in the store."""
    import json

    projects = load_all_projects(store_dir)
    if name_contains is not None:
        needle = name_contains.lower()
        projects = [p for p in projects if p.name.lower().find(needle) != -1]
    if output_json:
        data = [proj.to_dict() for proj in projects]
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not projects:
        click.echo(f"No projects found in {store_dir}")
        return
    for proj in projects:
        click.echo(f"{proj.id}  {proj.name}  {proj.target_uri}")


@project.command(name="show")
@click.option("--id", "project_id", required=True, help="Project ID")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def project_show(project_id: str, store_dir: Path, output_json: bool) -> None:
    """Show a project's details."""
    import json

    try:
        proj = load_project(project_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Project {project_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    if output_json:
        click.echo(json.dumps(proj.to_dict(), indent=2, sort_keys=True))
        return

    click.echo(f"Project {proj.name} (id={proj.id})")
    click.echo(f"Target: {proj.target_uri}")
    click.echo(f"Created: {proj.created_at}")


@project.command(name="update")
@click.option("--id", "project_id", required=True, help="Project ID")
@click.option("--name", help="New project name")
@click.option("--target-uri", help="New target URI")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def project_update(
    project_id: str, name: str | None, target_uri: str | None, store_dir: Path
) -> None:
    """Update a project's details."""
    try:
        proj = load_project(project_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Project {project_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    updated = False
    if name is not None:
        proj.name = name
        updated = True
    if target_uri is not None:
        proj.target_uri = target_uri
        updated = True

    if not updated:
        click.echo("No changes specified. Use --name or --target-uri.")
        return

    save_project(proj, store_dir)
    click.echo(f"Updated project {project_id}")


@project.command(name="delete")
@click.option("--id", "project_id", required=True, help="Project ID")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def project_delete(project_id: str, yes: bool, store_dir: Path) -> None:
    """Delete a project."""
    try:
        proj = load_project(project_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Project {project_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    if not yes:
        if not click.confirm(f"Delete project '{proj.name}' (id={project_id})?"):
            click.echo("Aborted.")
            return

    delete_project(project_id, store_dir)
    click.echo(f"Deleted project {project_id}")


@cli.group()
def iteration() -> None:
    """Manage iterations."""
    pass


@iteration.command(name="create")
@click.option("--project-id", required=True, help="Parent project ID")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Local storage directory",
)
@click.option("-v", "verbose", count=True, help="Override global verbosity")
@click.option("--quiet", "-q", "quiet", is_flag=True, help="Override to quiet")
@click.pass_context
def iteration_create(
    ctx: click.Context,
    project_id: str,
    store_dir: Path | None,
    verbose: int,
    quiet: bool,
) -> None:
    """Create a new iteration."""
    from stfwb.core.iteration import Iteration
    from stfwb.utils.logging import setup_logging
    from stfwb.utils.storage import load_project

    if store_dir is None:
        cfg = ctx.obj.get("config") if ctx.obj else None
        store_dir = Path(cfg.store_dir) if cfg and cfg.store_dir else Path(DEFAULT_STORE_DIR)

    level = _get_log_level(ctx, verbose or None, quiet or None)
    log_file = ctx.obj.get("log_file") if ctx.obj else None
    setup_logging(level, log_file)  # type: ignore[arg-type]

    proj = None
    try:
        proj = load_project(project_id, store_dir)
    except FileNotFoundError:
        # Allow iteration creation without existing project (legacy behavior)
        proj = None

    meta: dict[str, object] = {"target_uri": proj.target_uri} if proj else {}
    iteration = Iteration(project_id=project_id, metadata=meta)  # type: ignore[call-arg]
    click.echo(f"Creating iteration for project {project_id}")
    out_path = save_iteration(iteration, store_dir)
    click.echo(f"Created iteration {iteration.id} for project {project_id} at {out_path}")


@iteration.command(name="list")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option(
    "--state",
    "state_value",
    type=click.Choice(["created", "in_progress", "frozen", "archived"], case_sensitive=False),
    help="Filter by state",
)
@click.option("--project-id", "filter_project_id", help="Filter by project ID")
def iteration_list(
    store_dir: Path, output_json: bool, state_value: str | None, filter_project_id: str | None
) -> None:
    """List iterations in the store."""
    import json

    iterations = load_all_iterations(store_dir)
    if state_value is not None:
        from stfwb.core.types import IterationState

        target_state = IterationState(state_value)
        iterations = [it for it in iterations if it.state == target_state]

    if filter_project_id is not None:
        iterations = [it for it in iterations if it.project_id == filter_project_id]
    if output_json:
        data = [it.to_dict() for it in iterations]
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not iterations:
        click.echo(f"No iterations found in {store_dir}")
        return
    for it in iterations:
        click.echo(f"{it.id}  {it.project_id}  {it.state.value}")


@iteration.command(name="show")
@click.option("--id", "iteration_id", required=True, help="Iteration ID")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def iteration_show(iteration_id: str, store_dir: Path, output_json: bool) -> None:
    """Show an iteration's details."""
    import json

    try:
        it = load_iteration(iteration_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Iteration {iteration_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    if output_json:
        click.echo(json.dumps(it.to_dict(), indent=2, sort_keys=True))
        return

    click.echo(f"Iteration {it.id}")
    click.echo(f"Project: {it.project_id}")
    click.echo(f"State: {it.state.value}")


@iteration.command(name="update")
@click.option("--id", "iteration_id", required=True, help="Iteration ID")
@click.option("--state", "state_value", help="New state (created, in_progress, frozen, archived)")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def iteration_update(iteration_id: str, state_value: str | None, store_dir: Path) -> None:
    """Update an iteration's details."""
    from stfwb.core.types import IterationState

    try:
        it = load_iteration(iteration_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Iteration {iteration_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    if state_value is None:
        click.echo("No changes specified. Use --state.")
        return

    try:
        new_state = IterationState(state_value)
    except ValueError:
        click.echo(
            f"Error: Invalid state '{state_value}'. Valid: created, in_progress, frozen, archived",
            err=True,
        )
        raise SystemExit(1)

    it.state = new_state
    save_iteration(it, store_dir)
    click.echo(f"Updated iteration {iteration_id} state to {new_state.value}")


@iteration.command(name="delete")
@click.option("--id", "iteration_id", required=True, help="Iteration ID")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def iteration_delete(iteration_id: str, yes: bool, store_dir: Path) -> None:
    """Delete an iteration."""
    try:
        it = load_iteration(iteration_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Iteration {iteration_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    if not yes:
        if not click.confirm(f"Delete iteration {iteration_id} (project={it.project_id})?"):
            click.echo("Aborted.")
            return

    delete_iteration(iteration_id, store_dir)
    click.echo(f"Deleted iteration {iteration_id}")


@project.command(name="export")
@click.option("--id", "project_id", required=True, help="Project ID")
@click.option(
    "--output",
    "output_file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="Output JSON file path",
)
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def project_export(project_id: str, output_file: Path, store_dir: Path) -> None:
    """Export a project to a JSON file."""
    import json

    try:
        proj = load_project(project_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Project {project_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    output_file.write_text(json.dumps(proj.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    click.echo(f"Exported project {project_id} to {output_file}")


@project.command(name="import")
@click.option(
    "--file",
    "input_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="JSON file to import",
)
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def project_import(input_file: Path, store_dir: Path) -> None:
    """Import a project from a JSON file."""
    import json

    from stfwb.core.project import Project

    data = json.loads(input_file.read_text(encoding="utf-8"))
    proj = Project.from_dict(data)  # pyright: ignore[reportArgumentType]
    save_project(proj, store_dir)
    click.echo(f"Imported project {proj.id} (name={proj.name}) from {input_file}")


@iteration.command(name="export")
@click.option("--id", "iteration_id", required=True, help="Iteration ID")
@click.option(
    "--output",
    "output_file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="Output JSON file path",
)
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def iteration_export(iteration_id: str, output_file: Path, store_dir: Path) -> None:
    """Export an iteration to a JSON file."""
    import json

    try:
        it = load_iteration(iteration_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Iteration {iteration_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    output_file.write_text(json.dumps(it.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    click.echo(f"Exported iteration {iteration_id} to {output_file}")


@iteration.command(name="import")
@click.option(
    "--file",
    "input_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="JSON file to import",
)
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def iteration_import(input_file: Path, store_dir: Path) -> None:
    """Import an iteration from a JSON file."""
    import json

    from stfwb.core.iteration import Iteration

    data = json.loads(input_file.read_text(encoding="utf-8"))
    it = Iteration.from_dict(data)  # pyright: ignore[reportArgumentType]
    save_iteration(it, store_dir)
    click.echo(f"Imported iteration {it.id} (project={it.project_id}) from {input_file}")


@iteration.command(name="run")
@click.option("--iteration-id", required=True, help="Iteration ID")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
@click.option("-v", "verbose", count=True, help="Override global verbosity")
@click.option("--quiet", "-q", "quiet", is_flag=True, help="Override to quiet")
@click.option(
    "--skip",
    is_flag=True,
    help="Skip the next step instead of running it",
)
@click.option(
    "--redo",
    is_flag=True,
    help="Redo the last step instead of advancing",
)
@click.pass_context
def iteration_run(
    ctx: click.Context,
    iteration_id: str,
    store_dir: Path,
    verbose: int,
    quiet: bool,
    skip: bool,
    redo: bool,
) -> None:
    """Run iteration (S0→S1→S2→S3→S4→S5).

    By default, advances to the next step. Use --skip to skip the next step
    without executing it, or --redo to rerun the last completed step.
    """
    from stfwb.core.types import IterationState
    from stfwb.utils.logging import setup_logging

    if skip and redo:
        click.echo("Error: Cannot use both --skip and --redo", err=True)
        raise SystemExit(1)

    level = _get_log_level(ctx, verbose or None, quiet or None)
    log_file = ctx.obj.get("log_file") if ctx.obj else None
    setup_logging(level, log_file)  # type: ignore[arg-type]

    try:
        it = load_iteration(iteration_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Iteration {iteration_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    click.echo(f"Running iteration {it.id}...")

    # Determine the action: normal, skip, or redo
    action: Literal["normal", "skip", "redo"] = "normal"
    if skip:
        action = "skip"
    elif redo:
        action = "redo"

    if it.state == IterationState.CREATED:
        click.echo("Starting iteration...")
        it.start()
        # Execute initial steps (S0–S2) to keep 3-run behavior
        run_steps(it, 3, action=action)
        # Only transition state if normal action (not skip/redo)
        if action == "normal":
            pass  # State already set to IN_PROGRESS by it.start()
        save_iteration(it, store_dir)
        click.echo(f"State: {it.state.value}")
    elif it.state == IterationState.IN_PROGRESS:
        # Execute next steps (S3–S4), then freeze
        run_steps(it, 2, action=action)
        # Only freeze if normal action (not skip/redo)
        if action == "normal":
            click.echo("Freezing iteration...")
            it.freeze()
        save_iteration(it, store_dir)
        click.echo(f"State: {it.state.value}")
    elif it.state == IterationState.FROZEN:
        # Execute final step (S5), then archive
        run_steps(it, 1, action=action)
        # Only archive if normal action (not skip/redo)
        if action == "normal":
            click.echo("Archiving iteration...")
            it.archive()
        save_iteration(it, store_dir)
        click.echo(f"State: {it.state.value}")
    else:
        click.echo(f"Iteration is already in final state: {it.state.value}")

    click.echo("Iteration run complete.")


@cli.group()
def cleanup() -> None:
    """Archive and cleanup commands."""
    pass


@cleanup.command(name="archived-iterations")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def cleanup_archived_iterations(store_dir: Path, output_json: bool) -> None:
    """List archived iterations."""
    import json

    from stfwb.core.types import IterationState

    iterations = load_all_iterations(store_dir)
    archived = [it for it in iterations if it.state == IterationState.ARCHIVED]

    if output_json:
        data = [it.to_dict() for it in archived]
        click.echo(json.dumps(data, indent=2, sort_keys=True))
        return

    if not archived:
        click.echo(f"No archived iterations found in {store_dir}")
        return

    for it in archived:
        click.echo(f"{it.id}  project={it.project_id}  created={it.created_at}")


@cleanup.command(name="bulk-delete-iterations")
@click.option(
    "--project-id",
    "filter_project_id",
    help="Delete only iterations from this project",
)
@click.option("--state", help="Delete only iterations in this state")
@click.option("--yes", "-y", "yes", is_flag=True, help="Skip confirmation")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def cleanup_bulk_delete_iterations(
    filter_project_id: str | None, state: str | None, yes: bool, store_dir: Path
) -> None:
    """Delete multiple iterations matching criteria."""
    from stfwb.core.types import IterationState

    iterations = load_all_iterations(store_dir)

    # Apply filters
    if filter_project_id:
        iterations = [it for it in iterations if it.project_id == filter_project_id]
    if state:
        target_state = IterationState(state.lower())
        iterations = [it for it in iterations if it.state == target_state]

    if not iterations:
        click.echo("No iterations match the criteria")
        return

    click.echo(f"Found {len(iterations)} iteration(s) to delete")
    for it in iterations:
        click.echo(f"  {it.id}  project={it.project_id}  state={it.state.value}")

    if not yes:
        if not click.confirm("Delete these iterations?"):
            click.echo("Aborted.")
            return

    for it in iterations:
        delete_iteration(it.id, store_dir)

    click.echo(f"Deleted {len(iterations)} iteration(s)")


@cleanup.command(name="archive-to-file")
@click.option(
    "--output",
    "output_file",
    type=click.Path(file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="Output JSON file path",
)
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
@click.option("--delete-after", is_flag=True, help="Delete iterations after archiving")
def cleanup_archive_to_file(output_file: Path, store_dir: Path, delete_after: bool) -> None:
    """Export all archived iterations to a file."""
    import json

    from stfwb.core.types import IterationState

    iterations = load_all_iterations(store_dir)
    archived = [it for it in iterations if it.state == IterationState.ARCHIVED]

    if not archived:
        click.echo("No archived iterations to export")
        return

    # Export to file
    data = [it.to_dict() for it in archived]
    output_file.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    click.echo(f"Exported {len(archived)} archived iteration(s) to {output_file}")

    # Delete after export if requested
    if delete_after:
        for it in archived:
            delete_iteration(it.id, store_dir)
        click.echo(f"Deleted {len(archived)} archived iteration(s)")


@cli.command()
@click.option("--iteration-id", required=True, help="Iteration ID")
@click.option("--repo", help="GitHub repo (owner/repo). Falls back to config/env.")
@click.option("--token", help="GitHub PAT token. Falls back to config/env.")
@click.option("--dry-run", is_flag=True, help="Simulate publishing without making API calls")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Local storage directory (overrides config/env)",
)
@click.pass_context
def publish(
    ctx: click.Context,
    iteration_id: str,
    repo: str | None,
    token: str | None,
    dry_run: bool,
    store_dir: Path | None,
) -> None:
    """Publish artifacts to GitHub.

    Creates a GitHub issue with iteration details and artifacts.
    Use --dry-run to preview without making actual API calls.
    """
    from stfwb.publishers.github import GitHubPublisher
    from stfwb.utils.config import get_config

    cfg = ctx.obj.get("config") if ctx.obj else get_config()

    effective_store = store_dir
    if effective_store is None:
        effective_store = Path(cfg.store_dir) if cfg and cfg.store_dir else Path(DEFAULT_STORE_DIR)

    effective_repo = repo or (cfg.github_repo if cfg else None)
    effective_token = token or (cfg.github_token if cfg else None)

    try:
        iteration = load_iteration(iteration_id, effective_store)
    except FileNotFoundError:
        click.echo(f"Error: Iteration {iteration_id} not found in {effective_store}", err=True)
        raise SystemExit(1)

    if dry_run:
        target_repo = effective_repo or "(none configured)"
        click.echo(f"[DRY RUN] Would publish iteration {iteration_id} to {target_repo}")
        click.echo(f"  State: {iteration.state.value}")
        click.echo(f"  Steps: {len(iteration.steps)}")
        return

    if not effective_repo:
        click.echo(
            "Error: GitHub repo not provided. Use --repo or set STFWB_GITHUB_REPO or github_repo in config.",
            err=True,
        )
        raise SystemExit(1)

    if not effective_token:
        click.echo(
            "Error: GitHub token not provided. Use --token or set STFWB_GITHUB_TOKEN or github_token in config.",
            err=True,
        )
        raise SystemExit(1)

    click.echo(f"Publishing iteration {iteration_id} to {effective_repo}...")
    publisher = GitHubPublisher(token=effective_token, repo=effective_repo)
    result = publisher.publish(iteration, dry_run=dry_run)

    if result["success"]:
        click.echo(f"✓ Published successfully: {result['issue_url']}")
    else:
        click.echo(f"✗ Failed to publish: {result['error']}", err=True)
        raise SystemExit(1)
