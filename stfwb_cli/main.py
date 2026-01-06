"""CLI entry point using Click."""

import click


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
def project_create(name: str, target_uri: str) -> None:
    """Create a new project."""
    click.echo(f"Creating project '{name}' targeting {target_uri}...")


@cli.group()
def iteration() -> None:
    """Manage iterations."""
    pass


@iteration.command(name="create")
@click.option("--project-id", required=True, help="Parent project ID")
def iteration_create(project_id: str) -> None:
    """Create a new iteration."""
    click.echo(f"Creating iteration for project {project_id}...")


@iteration.command(name="run")
@click.option("--iteration-id", required=True, help="Iteration ID")
def iteration_run(iteration_id: str) -> None:
    """Run iteration (S0→S1→S2→S3→S4→S5)."""
    click.echo(f"Running iteration {iteration_id}...")


@cli.command()
@click.option("--iteration-id", required=True, help="Iteration ID")
@click.option("--repo", required=True, help="GitHub repo (owner/repo)")
@click.option("--token", required=True, help="GitHub PAT token")
def publish(iteration_id: str, repo: str, token: str) -> None:
    """Publish artifacts to GitHub."""
    click.echo(f"Publishing iteration {iteration_id} to {repo}...")


if __name__ == "__main__":
    cli()  # pragma: no cover
