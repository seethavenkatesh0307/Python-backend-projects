# Project Overview

Task tracker is a project used to track and manage your tasks.<br>
In this task, you will build a simple command line interface (CLI) to track<br>
what you need to do, what you have done, and what you are currently working on. <br>
This project will help you practice your programming skills, including working with the filesystem,<br>
handling user inputs, and building a simple CLI application.

**[Project page URL](https://roadmap.sh/projects/task-tracker)**

## Requirements

The application should run from the command line, accept user actions and inputs as arguments, and store the tasks in a JSON file. The user should be able to:

    1. Add, Update, and Delete tasks
    2. Mark a task as in progress or done
    3. List all tasks
    4. List all tasks that are done
    5. List all tasks that are not done
    6. List all tasks that are in progress

## Constraints

    1. You can use any programming language to build this project.
    2. Use positional arguments in command line to accept user inputs.
    3. Use a JSON file to store the tasks in the current directory.
    4. The JSON file should be created if it does not exist.
    5. Use the native file system module of your programming language to interact with the JSON file.
    6. Do not use any external libraries or frameworks to build this project.
    7. Ensure to handle errors and edge cases gracefully.

## How to Run

The list of commands and their usage is given below:

### Adding a new task
python task-cli.py add "Buy groceries"<br>
Output: Task added successfully (ID: 1)

### Updating and deleting tasks
python task-cli.py update 1 "Buy groceries and cook dinner"<br>
python task-cli.py delete 1

### Marking a task as in progress or done
python task-cli.py mark-in-progress 1<br>
python task-cli.py mark-done 1<br>
python task-cli.py mark-todo 1

### Listing all tasks
python task-cli.py list

### Listing tasks by status
python task-cli.py list done<br>
python task-cli.py list todo<br>
python task-cli.py list in-progress

## Task Properties

Each task should have the following properties:

**ID** : A unique identifier for the task <br>
**Description** : A short description of the task <br>
**Status** : The status of the task (todo, in-progress, done) <br>
**CreatedAt** : The date and time when the task was created <br>
**UpdatedAt**: The date and time when the task was last updated

Make sure to add these properties to the JSON file when adding a new task manually and update them when updating a task.<br>
The task_list.json file is initialized as an empty list if it does not exist.

## Future Enhancements
    1. Add multiple tasks in a single command
    2. Prevent duplicate task descriptions
