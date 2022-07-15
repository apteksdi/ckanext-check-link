from __future__ import annotations

import ckan.model as model
import ckan.plugins.toolkit as tk
import click


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
@click.argument("ids", nargs=-1)
def check_packages(include_draft: bool, include_private: bool, ids: tuple[str, ...]):
    """Check every resource inside each package.

    Scope can be narrowed via arbitary number of arguments, specifying
    package's ID or name.

    """
    user = tk.get_action("get_site_user")({"ignore_auth": True}, {})
    context = {"user": user["name"]}

    check = tk.get_action("check_link_package_check")
    states = ["active"]

    if include_draft:
        states.append("draft")

    q = model.Session.query(model.Package.id).filter(model.Package.state.in_(states))

    if not include_private:
        q = q.filter(model.Package.private == False)

    if ids:
        q = q.filter(model.Package.id.in_(ids) | model.Package.name.in_(ids))

    with click.progressbar(q, length=q.count()) as bar:
        for pkg in bar:
            check(
                context.copy(),
                {
                    "id": pkg.id,
                    "save": True,
                    "clear_available": True,
                    "include_drafts": include_draft,
                    "include_private": include_private,
                },
            )

    click.secho("Done", fg="green")
