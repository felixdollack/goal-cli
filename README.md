# Simple command-line Goal-Setting & Progress Tracker.
A tool where employees can set goals, update progress and view team-wide completion metrics.

## Core Features
### Add a Goal
Command: `add <employee_name> <goal_description> <team_name>`

Creates a new goal record with:
- A unique goal ID
- Employee name
- Goal description
- Team name
- Creation date
- Status (`Not Started` by default)

### List Goals for an Employee
Command: `list <employee_name>`

### Update Goal Status
Command: `add <goal_id> <status>`

### Delete Goal
Command: `delete <goal_id>`

### Show Team Progress Summary
Command: `summary <team_name>`


## Examples
### Add
```
add "Sofi" "Schedule 1:1 meetings with the rest of the team" "Engineering"
```

Creates a Goal for the `Engineering` team and assigns it to `Sofi`

### List
```
list Sofi
```

Lists the goals assigned to `Sofi`:
```
Not Started:
"Schedule 1:1 meetings with the rest of the team", Engineering

In Progress:
"Set goals for the Engineering team", Engineering
```

### Update
```
update 2 "In Progress"
```

Updates Goal 2 status to `In Progress`
```
"Schedule 1:1 meetings with the rest of the team", Engineering, In Progress
```

### Delete
```
delete 1
```

Deletes Goal 1
```
"Set goals for the Engineering team", Engineering, In Progress
```

### Summary
```
summary Engineering
```

Returns the Engineering team Goals
```
Not Started:
- N/A
In Progress:
- "Schedule 1:1 meetings with the rest of the team"
Completed:
- N/A
```
