"""Click CLI for chronovault administration and operations."""

from __future__ import annotations

import json

import click
from rich.console import Console
from rich.table import Table

import chronovault as cv

console = Console()


def _db(org: str, token: str, path: str) -> cv.ChronoVault:
    return cv.connect(token=token, org_id=org, path=path)


@click.group()
def main() -> None:
    """ChronoVault CLI entrypoint."""


@main.command("init")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
def init_cmd(org: str, token: str, path: str) -> None:
    """Initialize a tenant workspace."""
    db = _db(org=org, token=token, path=path)
    console.print({"status": "ok", "tenant": db.tenant_info()})


@main.command("status")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
def status_cmd(org: str, token: str, path: str) -> None:
    """Show tenant info and collection count."""
    db = _db(org=org, token=token, path=path)
    payload = db.tenant_info()
    payload["collections"] = db.list_collections()
    console.print(payload)


@main.group("collections")
def collections_group() -> None:
    """Collection commands."""


@collections_group.command("list")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
def collections_list_cmd(org: str, token: str, path: str) -> None:
    """List tenant collections."""
    db = _db(org=org, token=token, path=path)
    for name in db.list_collections():
        console.print(name)


@main.group("audit")
def audit_group() -> None:
    """Audit commands."""


@audit_group.command("tail")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
@click.option("--n", type=int, default=50)
def audit_tail_cmd(org: str, token: str, path: str, n: int) -> None:
    """Tail N audit entries."""
    db = _db(org=org, token=token, path=path)
    entries = db.audit_log.tail(n=n)
    table = Table(title="Audit Tail")
    table.add_column("timestamp")
    table.add_column("event")
    table.add_column("result")
    for item in entries:
        table.add_row(str(item.get("timestamp")), str(item.get("event")), str(item.get("result")))
    console.print(table)


@audit_group.command("verify")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
def audit_verify_cmd(org: str, token: str, path: str) -> None:
    """Verify audit hash chain integrity."""
    db = _db(org=org, token=token, path=path)
    console.print({"integrity": db.audit_log.verify_integrity()})


@main.group("token")
def token_group() -> None:
    """Token commands."""


@token_group.command("issue")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
@click.option("--name", required=True)
@click.option("--role", default="viewer")
def token_issue_cmd(org: str, token: str, path: str, name: str, role: str) -> None:
    """Issue tenant token."""
    db = _db(org=org, token=token, path=path)
    secret = db.issue_token(name=name, role=role)
    console.print({"name": name, "secret": secret})


@token_group.command("revoke")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
@click.option("--name", required=True)
def token_revoke_cmd(org: str, token: str, path: str, name: str) -> None:
    """Revoke tenant token."""
    db = _db(org=org, token=token, path=path)
    db.revoke_token(name)
    console.print({"revoked": name})


@main.command("rotate")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
@click.option("--collection", required=False)
def rotate_cmd(org: str, token: str, path: str, collection: str | None) -> None:
    """Rotate one collection key or all collection keys."""
    db = _db(org=org, token=token, path=path)
    if collection:
        getattr(db, collection).rotate_key()
    else:
        db.rotate_all_keys()
    console.print({"rotated": collection or "*"})


@main.command("serve")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
@click.option("--port", default=8471)
@click.option("--host", default="0.0.0.0")
def serve_cmd(org: str, token: str, path: str, port: int, host: str) -> None:
    """Run access-link HTTP server."""
    db = _db(org=org, token=token, path=path)
    db.serve(port=port, host=host)


@main.command("export-report")
@click.option("--org", required=True)
@click.option("--token", required=True)
@click.option("--path", default="~/.chronovault")
@click.option("--output", required=True)
def export_report_cmd(org: str, token: str, path: str, output: str) -> None:
    """Export compliance report JSON."""
    db = _db(org=org, token=token, path=path)
    db.export_compliance_report(output)
    with open(output, "r", encoding="utf-8") as fh:
        console.print(json.load(fh))


if __name__ == "__main__":
    main()
