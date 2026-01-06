"""CLI entry point using Click."""

from pathlib import Path

import click

from stfwb.utils.storage import (
    DEFAULT_STORE_DIR,
    delete_iteration,
    delete_project,
    list_iteration_ids,
    list_project_ids,
    load_all_iterations,
    load_all_projects,
    load_iteration,
    load_project,
    save_iteration,
    save_project,
)


@click.group()
@click.version_option(version="0.1.0-alpha")
def cli() -> None:
    """STF-WB: Reference implementation of STF-Workbench v0.2.0."""
    pass


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
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def project_create(name: str, target_uri: str, store_dir: Path) -> None:
    """Create a new project."""
    from stfwb.core.project import Project

    project = Project(name=name, target_uri=target_uri)  # pyright: ignore[reportCallIssue]
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
def project_list(store_dir: Path, output_json: bool) -> None:
    """List projects in the store."""
    import json

    projects = load_all_projects(store_dir)
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
def project_update(project_id: str, name: str | None, target_uri: str | None, store_dir: Path) -> None:
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
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def iteration_create(project_id: str, store_dir: Path) -> None:
    """Create a new iteration."""
    from stfwb.core.iteration import Iteration

    iteration = Iteration(project_id=project_id)  # pyright: ignore[reportCallIssue]
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
def iteration_list(store_dir: Path, output_json: bool) -> None:
    """List iterations in the store."""
    import json

    iterations = load_all_iterations(store_dir)
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
        click.echo(f"Error: Invalid state '{state_value}'. Valid: created, in_progress, frozen, archived", err=True)
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


@iteration.command(name="run")
@click.option("--iteration-id", required=True, help="Iteration ID")
@click.option(
    "--store-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path(DEFAULT_STORE_DIR),
    show_default=True,
    help="Local storage directory",
)
def iteration_run(iteration_id: str, store_dir: Path) -> None:
    """Run iteration (S0→S1→S2→S3→S4→S5)."""
    from stfwb.core.types import IterationState

    try:
        it = load_iteration(iteration_id, store_dir)
    except FileNotFoundError:
        click.echo(f"Error: Iteration {iteration_id} not found in {store_dir}", err=True)
        raise SystemExit(1)

    click.echo(f"Running iteration {it.id}...")

    if it.state == IterationState.CREATED:
        click.echo("Starting iteration...")
        it.start()
        save_iteration(it, store_dir)
        click.echo(f"State: {it.state.value}")
    elif it.state == IterationState.IN_PROGRESS:
        click.echo("Freezing iteration...")
        it.freeze()
        save_iteration(it, store_dir)
        click.echo(f"State: {it.state.value}")
    elif it.state == IterationState.FROZEN:
        click.echo("Archiving iteration...")
        it.archive()
        save_iteration(it, store_dir)
        click.echo(f"State: {it.state.value}")
    else:
        click.echo(f"Iteration is already in final state: {it.state.value}")

    click.echo("Iteration run complete.")


@cli.command()
@click.option("--iteration-id", required=True, help="Iteration ID")
@click.option("--repo", required=True, help="GitHub repo (owner/repo)")
@click.option("--token", required=True, help="GitHub PAT token")
def publish(iteration_id: str, repo: str, token: str) -> None:
    """Publish artifacts to GitHub."""
    click.echo(f"Publishing iteration {iteration_id} to {repo}...")


if __name__ == "__main__":
    cli()  # pragma: no cover
