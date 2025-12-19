"""
Requires Python >=3.10
"""

from argparse import Namespace, ArgumentParser, ArgumentTypeError
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
from shlex import split as split_shell_arguments

DB = "data.json"


def print_welcome():
    print("""\
Command Options
- add "Employee Name" "Goal Description" "Team Name"
- list "Employee Name"
- update GoalId "Status"
- delete GoalId
- summary "Team Name"

To exit press enter without any input.""")


def get_new_data() -> dict:
    return {
        "goals": {},  # dict of goals by goal_id
        "team": defaultdict(list),  # dict of task id list per team
        "employee": defaultdict(list),  # dict of task id list per employee
    }


def load_data(filename: str) -> dict:
    """
    load_data opens the specified json file and returns it's content.
    In case the file does not exist, an empty dictionary is returned.
    """
    try:
        with open(filename, "r") as f:
            data = json.load(f)
            # convert team and employee sub-dicts to dicts with default
            data["team"] = defaultdict(list, data["team"])
            data["employee"] = defaultdict(list, data["employee"])
    except FileNotFoundError:
        data = get_new_data()
    return data


def persist_data(filename: str, data: dict):
    """
    persist_data writes the dictionary provided to the speciefied file.
    If the file already exists, it is overwritten.
    """
    with open(filename, "w") as f:
        f.write(json.dumps(data))


def _is_status(value: str):
    """
    Helper function to determine the provided value is of type 'Status'
    """
    escaped_value = value.upper().replace(" ", "_")
    if escaped_value not in [
        Status.NOT_STARTED.name,
        Status.IN_PROGRESS.name,
        Status.COMPLETED.name,
    ]:
        raise ArgumentTypeError(f"`{value}` is not a valid status.")
    return escaped_value


def get_input_parser() -> ArgumentParser:
    """
    User input argument parser.
    Expects one command of 'add', 'list', 'update', 'delete', 'summary' with their respective arguments.
    """
    parser = ArgumentParser()
    command_subparsers = parser.add_subparsers(dest="user_command")

    # parser for 'add' command and arguments
    add_parser = command_subparsers.add_parser("add")
    add_parser.add_argument("employee", type=str)
    add_parser.add_argument("description", type=str)
    add_parser.add_argument("team", type=str)

    # parser for 'list' command and arguments
    list_parser = command_subparsers.add_parser("list")
    list_parser.add_argument("employee", type=str)

    # parser for 'update' command and arguments
    update_parser = command_subparsers.add_parser("update")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("status", type=_is_status)

    # parser for 'delete' command and arguments
    delete_parser = command_subparsers.add_parser("delete")
    delete_parser.add_argument("id", type=int)

    # parser for 'summary' command and arguments
    summary_parser = command_subparsers.add_parser("summary")
    summary_parser.add_argument("team", type=str)

    return parser


class Status(str, Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


@dataclass
class Goal:
    goal_id: int
    employee: str
    description: str
    team: str
    created_at: str
    status: Status


def create_goal(employee: str, goal: str, team: str) -> Goal:
    goal_id = id(employee + goal + team)
    new_goal = Goal(
        goal_id=goal_id,
        employee=employee,
        description=goal,
        team=team,
        created_at=str(datetime.now()),
        status=Status.NOT_STARTED,
    )
    return new_goal


def _list_goals(data: dict, task_target: str, target: str):
    """
    list_tasks is an abstraction that supports task retrieval per team or employee
    """
    if task_target not in data[target].keys():
        print(f"No tasks for {target}: `{task_target}`")
        goals = []
    else:
        goals = defaultdict(list)
        targets = data[target].get(task_target, list())
        for goal_id in targets:
            goal = Goal(**data["goals"][str(goal_id)])
            goals[Status[_is_status(goal.status)]].append(goal)
    return goals


def list_tasks_of(data: dict, employee: str):
    employee_goals = _list_goals(data=data, task_target=employee, target="employee")
    if len(employee_goals) > 0:
        for state in [Status.NOT_STARTED, Status.IN_PROGRESS, Status.COMPLETED]:
            if len(employee_goals[state]) > 0:
                print(f"{state.name}:")
            for goal in employee_goals[state]:
                print(f"- ({goal.goal_id}) {goal.description}, {goal.team}")


def update_goal_with_id(data: dict, goal_id: int, new_status: Status) -> dict:
    # if goal_id in list of goals set new status
    if data["goals"].get(str(goal_id), None):
        data["goals"][str(goal_id)]["status"] = Status[new_status]
    return data


def delete_goal_with_id(data: dict, goal_id: int) -> dict:
    # if goal_id in list of goals
    if data["goals"].get(str(goal_id), None):
        # remove goal from goal list
        deletedGoal = Goal(**data["goals"].pop(str(goal_id)))

        # remove goal_id from employee goal list and remove employee if no more goals
        data["employee"][deletedGoal.employee].remove(deletedGoal.goal_id)
        if len(data["employee"][deletedGoal.employee]) < 1:
            data["employee"].pop(deletedGoal.employee)

        # remove goal_id from team goal list and remove team if no more goals
        data["team"][deletedGoal.team].remove(deletedGoal.goal_id)
        if len(data["team"][deletedGoal.team]) < 1:
            data["team"].pop(deletedGoal.team)

    return data


def summarize_goals_for_team(data: dict, team: str):
    team_goals = _list_goals(data=data, task_target=team, target="team")
    if len(team_goals) > 0:
        for state in [Status.NOT_STARTED, Status.IN_PROGRESS, Status.COMPLETED]:
            print(state.name)
            if len(team_goals[state]) < 1:
                print("- N/A")
            for goal in team_goals[state]:
                print(f"- {goal.description}, {goal.employee}")


if __name__ == "__main__":
    data = load_data(DB)
    parser = get_input_parser()
    print_welcome()
    while True:
        # get user input
        user_input = input("$: ")
        if len(user_input) < 1:
            # exit loop
            break

        # parse input and keep extra arguments
        try:
            cmd, extra_args = parser.parse_known_args(split_shell_arguments(user_input))
        except:
            extra_args = []
            cmd = Namespace(user_command="")

        if len(extra_args) > 0:
            # inform user of ignored command
            print(
                f"\033[31mReceived too many arguments `{user_input}`.\nIgnoring last command.\n\033[0m"
            )
            execute = False
        else:
            execute = True

        if execute:
            print_data = False
            match cmd.user_command:
                case "add":
                    new_goal = create_goal(
                        employee=cmd.employee, goal=cmd.description, team=cmd.team
                    )
                    data["goals"][str(new_goal.goal_id)] = asdict(new_goal)
                    data["team"][cmd.team].append(new_goal.goal_id)
                    data["employee"][cmd.employee].append(new_goal.goal_id)

                    print_data = True
                case "list":
                    list_tasks_of(data=data, employee=cmd.employee)
                case "update":
                    data = update_goal_with_id(
                        data=data, goal_id=cmd.id, new_status=cmd.status
                    )
                    print_data = True
                case "delete":
                    data = delete_goal_with_id(data=data, goal_id=cmd.id)
                    print_data = True
                case "summary":
                    summarize_goals_for_team(data=data, team=cmd.team)
                case _:
                    pass
            if print_data:
                print(data)
    persist_data(DB, data)
