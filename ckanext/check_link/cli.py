from __future__ import annotations

import logging
from collections import Counter
from itertools import islice
from typing import Any, Iterable, TypeVar

import ckan.model as model
import ckan.plugins.toolkit as tk
import sqlalchemy as sa
import click

T = TypeVar("T")
log = logging.getLogger(__name__)

def get_commands():
    return [check_link]


@click.group(short_help="Check link availability")
def check_link():
    pass


@check_link.command()
@click.option(
    "-d", "--include-draft", is_flag=True, help="Check draft packages as well"
)
@click.option(
    "-p", "--include-private", is_flag=True, help="Check private packages as well"
)
@click.option(
    "-c", "--chunk", help="Number of packages that processed simultaneously", default=1, type=click.IntRange(1, )
)
@click.argument("ids", nargs=-1)
def check_packages(include_draft: bool, include_private: bool, ids: tuple[str, ...], chunk: int):
    """Check every resource inside each package.

    Scope can be narrowed via arbitary number of arguments, specifying
    package's ID or name.

    """
    user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}

    check = tk.get_action("check_link_search_check")
    states = ["active"]

    if include_draft:
        states.append("draft")

    q = model.Session.query(
        model.Package.id, sa.func.count(model.Resource.id)
    ).outerjoin(model.Resource, model.Package.resources_all).group_by(model.Package).filter(
        model.Package.state.in_(states),
        model.Resource.state == "active"
    )

    if not include_private:
        q = q.filter(model.Package.private == False)

    if ids:
        q = q.filter(model.Package.id.in_(ids) | model.Package.name.in_(ids))

    stats = Counter()
    with click.progressbar(q, length=q.count()) as bar:
        while True:
            buff = _take(bar, chunk)
            if not buff:
                break

            overview = ", ".join(f"{click.style(k,  underline=True)}: {click.style(str(v),bold=True)}" for k, v in stats.items()) or "not available"
            bar.label = f"Overview: {overview}"

            packages, counts = zip(*buff)

            result = check(
                context.copy(),
                {
                    "fq": "id:({})".format(" OR ".join(p for p in packages)),
                    "save": True,
                    "clear_available": True,
                    "include_drafts": include_draft,
                    "include_private": include_private,
                    "skip_invalid": True,
                    "rows": sum(c for c in counts)
                },
            )
            stats.update(r["state"] for r in result)


    click.secho("Done", fg="green")


def _take(seq: Iterable[T], size: int) -> list[T]:
    return list(islice(seq, size))
