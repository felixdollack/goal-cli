from argparse import ArgumentTypeError, Namespace
import cli
import pytest

TEST_DATA = {
    "goals": {
        "12": {
            "goal_id": 12,
            "description": "Goal description",
            "employee": "User",
            "team": "One",
            "created_at": "2025-12-19 19:30:21.048146",
            "status": "In Progress",
        }
    },
    "team": {"One": [12]},
    "employee": {"User": [12]},
}


def test_is_status():
    result = cli._is_status("not started")
    assert result == "NOT_STARTED"

    result = cli._is_status("in Progress")
    assert result == "IN_PROGRESS"

    result = cli._is_status("cOmPlEtEd")
    assert result == "COMPLETED"

    with pytest.raises(ArgumentTypeError):
        result = cli._is_status("unknown")


def test_create_goal():
    storage = cli.LocalStorage("")
    employee = "User"
    description = "Smth To Do"
    team = "Group"
    cli.add_goal(
        storage=storage,
        cmd=Namespace(employee=employee, description=description, team=team),
    )
    goal = cli.Goal(**storage.data["goals"][list(storage.data["goals"].keys())[0]])
    assert goal.employee == employee
    assert goal.description == description
    assert goal.team == team
    assert goal.status.name == "NOT_STARTED"


def test_list_goals():
    storage = cli.LocalStorage("")
    storage.data = {"team": {}}
    goals = storage.get_team_goals(team="One")
    assert len(goals) == 0

    storage.data = TEST_DATA
    goals = storage.get_team_goals(team="One")
    assert len(goals) == 1


def test_update_goal():
    storage = cli.LocalStorage("")
    storage.data = TEST_DATA
    cli.update_goal_status(storage=storage, cmd=Namespace(id=12, status="COMPLETED"))
    assert storage.data["goals"]["12"]["status"].name == "COMPLETED"

    storage.data = {"goals": {}}
    cli.update_goal_status(storage=storage, cmd=Namespace(id=12, status="COMPLETED"))
    assert len(storage.data) == 1
    assert len(storage.data["goals"]) == 0


def test_delete_goal():
    storage = cli.LocalStorage("")
    storage.data = TEST_DATA
    cli.delete_goal_by_id(storage=storage, goal_id=12)
    assert len(storage.data["goals"]) == 0
    assert len(storage.data["team"]) == 0
    assert len(storage.data["employee"]) == 0

    storage.data = {"goals": {}}
    cli.delete_goal_by_id(storage=storage, goal_id=12)
    assert len(storage.data) == 1
    assert len(storage.data["goals"]) == 0
