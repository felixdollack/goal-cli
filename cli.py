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
from abc import ABC, abstractmethod

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


class Storage(ABC):
    """
    Abstract class (interface) over data storage
    """
    @abstractmethod
    def add_goal(self, goal: Goal):
        pass

    @abstractmethod
    def update_goal_status(self, goal_id: int, new_status: Status):
        pass

    @abstractmethod
    def delete_goal(self, goal_id: int):
        pass

    @abstractmethod
    def get_employee_goals(self, employee:str):
        pass

    @abstractmethod
    def get_team_goals(self, employee:str):
        pass


class LocalStorage(Storage):
    """
    Local data store (JSON) implementation
    """
    def __init__(self, filepath:str):
        print(type(self))
        self.DB = filepath
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """
        load_data opens the specified json file and returns it's content.
        In case the file does not exist, an empty dictionary is returned.
        """
        try:
            with open(self.DB, "r") as f:
                data = json.load(f)
                # convert team and employee sub-dicts to dicts with default
                data["team"] = defaultdict(list, data["team"])
                data["employee"] = defaultdict(list, data["employee"])
        except FileNotFoundError:
            data = get_new_data()
        return data

    def persist_data(self):
        """
        persist_data writes the dictionary provided to the speciefied file.
        If the file already exists, it is overwritten.
        """
        with open(self.DB, "w") as f:
            f.write(json.dumps(self.data))

    def add_goal(self, goal: Goal):
        self.data["goals"][str(goal.goal_id)] = asdict(goal)
        self.data["team"][goal.team].append(goal.goal_id)
        self.data["employee"][goal.employee].append(goal.goal_id)

    def update_goal_status(self, goal_id: int, new_status: Status):
        if self.data["goals"].get(str(goal_id), None):
            self.data["goals"][str(goal_id)]["status"] = Status[new_status]

    def delete_goal(self, goal_id: int):
        # if goal_id in list of goals
        if self.data["goals"].get(str(goal_id), None):
            # remove goal from goal list
            deletedGoal = Goal(**self.data["goals"].pop(str(goal_id)))

            # remove goal_id from employee goal list and remove employee if no more goals
            self.data["employee"][deletedGoal.employee].remove(deletedGoal.goal_id)
            if len(self.data["employee"][deletedGoal.employee]) < 1:
                self.data["employee"].pop(deletedGoal.employee)

            # remove goal_id from team goal list and remove team if no more goals
            self.data["team"][deletedGoal.team].remove(deletedGoal.goal_id)
            if len(self.data["team"][deletedGoal.team]) < 1:
                self.data["team"].pop(deletedGoal.team)

    def _list_goals(self, task_target: str, target: str):
        """
        list_tasks is an abstraction that supports task retrieval per team or employee
        """
        if task_target not in self.data[target].keys():
            print(f"No tasks for {target}: `{task_target}`")
            goals = []
        else:
            goals = defaultdict(list)
            targets =self.data[target].get(task_target, list())
            for goal_id in targets:
                goal = Goal(**self.data["goals"][str(goal_id)])
                goals[Status[_is_status(goal.status)]].append(goal)
        return goals

    def get_employee_goals(self, employee:str):
        return self._list_goals(task_target=employee, target="employee")

    def get_team_goals(self, team:str):
        return self._list_goals(task_target=team, target="team")


def add_goal(storage: Storage, cmd: Namespace):
    """
    Create a new goal and persist it to storage
    """
    goal_id = id(cmd.employee + cmd.description + cmd.team)
    new_goal = Goal(
        goal_id=goal_id,
        employee=cmd.employee,
        description=cmd.description,
        team=cmd.team,
        created_at=str(datetime.now()),
        status=Status.NOT_STARTED,
    )
    storage.add_goal(new_goal)


def print_employee_goals(employee_goals: dict):
    if len(employee_goals) > 0:
        for state in [Status.NOT_STARTED, Status.IN_PROGRESS, Status.COMPLETED]:
            if len(employee_goals[state]) > 0:
                print(f"{state.name}:")
            for goal in employee_goals[state]:
                print(f"- ({goal.goal_id}) {goal.description}, {goal.team}")


def update_goal_status(storage: Storage, cmd: Namespace):
    storage.update_goal_status(goal_id=cmd.id, new_status=cmd.status)


def delete_goal_by_id(storage: Storage, goal_id:int):
    storage.delete_goal(goal_id=goal_id)


def print_team_goals(team_goals: dict):
    if len(team_goals) > 0:
        for state in [Status.NOT_STARTED, Status.IN_PROGRESS, Status.COMPLETED]:
            print(state.name)
            if len(team_goals[state]) < 1:
                print("- N/A")
            for goal in team_goals[state]:
                print(f"- {goal.description}, {goal.employee}")


if __name__ == "__main__":
    storage = LocalStorage(filepath=DB)
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
            match cmd.user_command:
                case "add":
                    add_goal(storage=storage, cmd=cmd)
                case "list":
                    goals = storage.get_employee_goals(employee=cmd.employee)
                    print_employee_goals(employee_goals=goals)
                case "update":
                    update_goal_status(storage=storage, cmd=cmd)
                case "delete":
                    delete_goal_by_id(storage=storage, goal_id=cmd.id)
                case "summary":
                    goals = storage.get_team_goals(team=cmd.team)
                    print_team_goals(team_goals=goals)
                case _:
                    pass

    storage.persist_data()
