from argparse import ArgumentTypeError
import cli
import pytest

TEST_DATA = {
    "goals": {
        "12": {
            "goal_id": 12,
            "description": "Goal description",
            "employee": "User",
            "team": "One",
            "created_at": '2025-12-19 19:30:21.048146',
            "status": "In Progress",
        }
    },
    "team": {"One": [12]},
    "employee": {"User": [12]}
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
    employee = "User"
    description = "Smth To Do"
    team = "Group"
    goal = cli.create_goal(employee=employee, goal=description, team=team)
    assert goal.employee == employee
    assert goal.description == description
    assert goal.team == team
    assert goal.status.name == "NOT_STARTED"


def test_list_goals():
    data = {"team": {}}
    goals = cli._list_goals(data=data, task_target="One", target="team")
    assert len(goals) == 0

    data = TEST_DATA
    goals = cli._list_goals(data=data, task_target="One", target="team")
    assert len(goals) == 1


def test_update_goal():
    data = TEST_DATA
    updated = cli.update_goal_with_id(data=data, goal_id=12, new_status="COMPLETED")
    assert updated["goals"]["12"]["status"].name == "COMPLETED"

    data = {"goals": {}}
    updated = cli.update_goal_with_id(data=data, goal_id=12, new_status="COMPLETED")
    assert data == updated


def test_delete_goal():
    data = TEST_DATA
    updated = cli.delete_goal_with_id(data=data, goal_id=12)
    assert len(updated["goals"]) == 0
    assert len(updated["team"]) == 0
    assert len(updated["employee"]) == 0

    data = {"goals": {}}
    updated = cli.delete_goal_with_id(data=data, goal_id=12)
    assert data == updated
