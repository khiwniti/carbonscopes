import pytest


def test_init_project():
    from core.carbon.brightway.engine import init_project

    proj = init_project("TestProject")
    assert proj is not None
    # Reset to default after test
    from brightway2 import projects

    projects.set_current("CarbonBIM-Thailand")
