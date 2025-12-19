from argparse import ArgumentParser
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

DB = "data.json"
CMDS = ["add", "list", "update", "delete", "summary"]

class Status(int,Enum):
    NOT_STARTED=1
    IN_PROGRESS=2
    COMPLETED=3

@dataclass
class Goal():
    goal_id:int
    employee:str
    description:str
    team:str
    created_at:str
    status:Status

def add_goal(data:dict, employee:str, goal:str, team:str):
    goal_id = id(employee+goal+team)
    new_goal = Goal(
        goal_id=goal_id, employee=employee, description=goal,
        team=team, created_at=str(datetime.now()),status=Status.NOT_STARTED
    )
    data[goal_id] = asdict(new_goal)
    persist(data)

def persist(data:dict):
    with open(DB, "w") as f:
        data_str = json.dumps(data)
        f.write(data_str)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('cmd', nargs='*')
    args = parser.parse_args()

    # e.g: add "Employee Name" "Goal" "Team Name"
    cmd = args.cmd

    if cmd[0] in CMDS:
        # check for storage file or create new one
        with open(DB, "a") as f:
            try:
                data = json.load(f)
            except:
                data = dict()


        if cmd[0] == CMDS[0]:
            add_goal(data, *cmd[1:])
        if cmd[0] == CMDS[1]:
            pass # do smth
        if cmd[0] == CMDS[2]:
            pass # do smth
        if cmd[0] == CMDS[3]:
            pass # do smth
        if cmd[0] == CMDS[4]:
            pass # do smth
    else:
        pass # throw error
