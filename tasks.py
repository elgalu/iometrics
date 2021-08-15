"""
## Invoke tasks without needing a Makefile.

Configuration can found at invoke.yaml
https://github.com/pyinvoke/invoke

```sh
# See all available tasks
invoke --list
# Invoke a task
invoke hooks
```

:copyright: (c) 2021 by Leo Gallucci.
:license: Apache 2.0, see LICENSE for more details.
"""
import os

from invoke import run
from invoke import task
from invoke.exceptions import UnexpectedExit


# Ignoring all missing MyPy types until https://github.com/pyinvoke/invoke/issues/248
@task
def setup(c):  # type: ignore
    """Set this project up for Development."""
    c.run("ls -lah --color=yes .venv")
    c.run("poetry env info --path")
    c.run("poetry debug info")
    c.run("poetry run pre-commit install")


@task
def clean_build(c):  # type: ignore
    """Remove build artifacts."""
    c.run("rm -rf build dist .eggs")
    c.run("find . -name '*.egg-info' -exec rm -rf  {} +")
    c.run("find . -name '*.egg' -exec rm -f {} +")


@task
def clean_pyc(c):  # type: ignore
    """Remove Python file artifacts."""
    c.run("find . -name '*.pyc' -exec rm -f {} +")
    c.run("find . -name '*.pyo' -exec rm -f {} +")
    c.run("find . -name '*~' -exec rm -f {} +")
    c.run("find . -name '__pycache__' -exec rm -rf {} +")


@task
def clean_test(c):  # type: ignore
    """Remove test and coverage artifacts."""
    c.run("rm -rf .coverage .mypy_cache .pytest_cache .tox")
    c.run("rm -rf pylint-report.txt ut-report.xml")


@task
def clean_coverage(c):  # type: ignore
    """Cleanup test coverage files."""
    c.run("poetry run coverage erase")


@task(pre=[clean_build, clean_pyc, clean_test, clean_coverage])
def clean(c):  # type: ignore
    """Remove all build, test, coverage and Python artifacts."""
    pass


@task(aliases=["checks", "all-checks", "lint-all"])
def hooks(c):  # type: ignore
    """Run all pre-commit hooks on all files."""
    c.run("poetry run pre-commit run --all-files")


@task(aliases=["upgrade"])
def update(c):  # type: ignore
    """Upgrade/update packages and hooks."""
    c.run("poetry update")
    c.run("pre-commit autoupdate --freeze")


@task(aliases=["pylint"])
def lint(c):  # type: ignore
    """Lint files and save report."""
    c.run("poetry run pylint --rcfile pyproject.toml -j 0 iometrics > pylint-report.txt")


@task(aliases=["tests"])
def test(c):  # type: ignore
    """Run tests quickly with the default Python."""
    c.run("PYTHONPATH=./iometrics poetry run pytest -v")


@task
def pre_checks(c):  # type: ignore
    """Check checks without pytest/pylint."""
    # https://pre-commit.com/#usage-in-continuous-integration
    c.run("SKIP=pytest,pylint poetry run pre-commit run --origin HEAD --source origin/HEAD")


@task(pre=[clean_coverage])
def coverage(c):  # type: ignore
    """Check code coverage quickly with the default Python."""
    c.run(
        """
        poetry run coverage run --branch --source=iometrics \
            -m pytest --junitxml=ut-report.xml tests/
    """.strip()
    )
    c.run("poetry run pylint --rcfile pyproject.toml iometrics -r n")


@task(pre=[clean_coverage])
def enforce_coverage_render_tests(c):  # type: ignore
    """Check code coverage above threshold and generate reports."""
    c.run(
        """
        poetry run pytest --cov=iometrics --cov-fail-under=80 --cov-branch \
            --junit-xml xunit-reports/xunit-result-ut.xml \
            --cov-report xml:coverage-reports/coverage-ut.xml
    """.strip()
    )


@task
def linter_and_qc(c):  # type: ignore
    """Run linter, keep exit code."""
    pylint_output_file_name = "pylint-report.txt"
    try:
        c.run(
            """
            poetry run pylint --rcfile pyproject.toml \
                -j 0 iometrics > {pylint_output_file_name}
        """.strip()
        )
    except UnexpectedExit:
        raise
    finally:
        recipes = ",".join(
            [
                "master-dashboard",
                "pr-issues-as-comments",
                "pr-quality-gate",
                "pr-vs-master-cov",
            ]
        )
        c.run(
            f"""
          echo recipes="{recipes}" \
               reportPath="{pylint_output_file_name}"
        """.strip()
        )


@task
def build_and_upload_documentation(c):  # type: ignore
    """Build and upload project's documentation."""

    def docs_have_changed() -> bool:
        """Check if documentation changed using git diff."""
        try:
            run("git diff --exit-code --quiet ${GITHUB_REF##*/} docs")
        except UnexpectedExit:
            # git diff returns exit code 1 if there were changes
            return True
        else:
            return False

    def disable_indexing_for_PRs() -> None:
        with open("site/robots.txt", "w") as robots_file:
            print(
                """
                User-agent: *
                Disallow: /pr
                """.strip(),
                file=robots_file,
            )

    docs_name = os.environ.get("DOCS_NAME")
    # https://stackoverflow.com/a/62436027/511069
    pr_number = os.getenv("CI_PULL_REQUEST_NUMBER", False)
    url = f"https://{docs_name}.tbd.com/pr/${pr_number}/index.html"

    if pr_number:
        # pull request
        c.run("mkdir -p /workspace/site")
        c.run(f"poetry run mkdocs build --site-dir /workspace/site/pr/{pr_number}")

        if docs_have_changed():
            c.run(
                f"""
                git gh-status --url "{url}" \
                    "custom/guild-python/docs" \
                    "success" \
                    "Documentation generated."
            """.strip()
            )
        else:
            c.run("poetry run mkdocs build --site-dir /workspace/site")

        disable_indexing_for_PRs()
    else:
        print("No PR number, no need to re-generate docs at /pr/")
