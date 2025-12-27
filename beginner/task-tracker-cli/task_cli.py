"""To track task via command line interface."""

import sys
import json
from pathlib import Path
from datetime import datetime

ADD_COMMAND_LENGTH = 3
DELETE_COMMAND_LENGTH = 3
UPDATE_COMMAND_LENGTH = 4
MARK_STATUS_COMMAND_LENGTH = 3
LIST_WITHOUT_ARGUMENT_LENGTH = 2
LIST_WITH_ARGUMENT_LENGTH = 3
TASK_FILE = "task_list.json"

class TaskManager:
    """Handling of task list operations."""
    def __init__(self, tasks: list):
        self.tasks = tasks

    def _fetch_current_time(self) -> str:
        """To fetch current time and format into human readable string.
        
        Args:
            None

        Returns:
            str: Current date and time in "DD-MM-YYYY HH:MM:SS" format.
        """

        current_datetime = datetime.now()
        return current_datetime.strftime("%d-%m-%Y %H:%M:%S")


    def mark_status(self, id:int, status:str) -> bool:
        """Mark status of existing item.

        Args:
            id (int): ID of the task to be marked.
            status (str): New status to be assigned to the task. 
        
        Returns:
            bool: True if task is found and updated, False otherwise.
        """

        for item in self.tasks:
            if item["id"] == id:
                item["status"] = status
                item["updatedAt"] = self._fetch_current_time()
                return True
        return False


    def update_item(self, id:int, description:str) -> bool:
        """Update the existing item decription.

        Args:
            id (int): ID of the task to be updated.
            description (str): New description for the task.
        
        Returns:
            bool: True if task is found and updated, False otherwise.
        """
        
        for item in self.tasks:
            if item["id"] == id:
                item["description"] = description
                item["updatedAt"] = self._fetch_current_time()
                return True
        return False


    def delete_item(self, id:int) -> bool:
        """Delete task from task list.
        
        Args:
            id (int): ID of the task to be deleted.

        Returns:
            bool: True if task is found and deleted, False otherwise.
        """

        for index, item in enumerate(self.tasks):
            if item["id"] == id:
                del self.tasks[index]
                return True
        return False


    def add_item(self, description:str) -> bool:
        """Add new task to the task list.
        
        Args:
            description (str): Description of the new task.

        Returns:
            bool: True if task is added successfully, False otherwise.
        """
        if not isinstance(self.tasks, list):
            raise TypeError("Invalid tasks data structure")

        if len(self.tasks) > 0:
            id = max(item["id"] for item in self.tasks) + 1
        else:
            id = 1
        
        current_datetime = self._fetch_current_time()

        self.tasks.append({
            "id": id, 
            "description": description, 
            "status": "todo", 
            "createdAt": current_datetime, 
            "updatedAt": current_datetime})
        
        return True

    def print_item(self, item: dict):
        """Printing task item."""
        print(f"ID : {item['id']}")
        print(f"Description : {item['description']}")
        print(f"Status : {item['status']}")
        print(f"Created At : {item['createdAt']}")
        print(f"Updated At : {item['updatedAt']}")
        print("-" * 40)


if __name__ == "__main__":

    if Path(TASK_FILE).exists():
        try:
            with open(TASK_FILE, "r") as file:
                tasks = json.load(file)
            if tasks is None:
                tasks = []
        except json.JSONDecodeError:
            print(f"Invalid JSON exist. Overwriting {TASK_FILE} with empty task list.")
            tasks = []
    else:
        with open(TASK_FILE, "w") as file:
            json.dump([], file)
        tasks = []

    task_manager = TaskManager(tasks)

    try:
        command = sys.argv[1]
        operation_success = False
        found_any_task = False

        if command == "add":
            if len(sys.argv) != ADD_COMMAND_LENGTH or sys.argv[2] == "":
                print("Error: 'add' requires exactly 1 argument and cannot be empty string.")
                print("Usage: python task_cli.py add <description>")
            else:
                operation_success = task_manager.add_item(str(sys.argv[2]))
                if operation_success:
                    print(f" Task '{sys.argv[2]}' is added successfully")
        elif command == "delete":
            if len(sys.argv) != DELETE_COMMAND_LENGTH:
                print("Error: 'delete' requires exactly 1 argument.")
                print("Usage: python task_cli.py delete <id>")
            else:
                operation_success = task_manager.delete_item(int(sys.argv[2]))
                if not operation_success:
                    print(f"Error: Task with ID {sys.argv[2]} not found.")
                else:
                    print(f"Task with ID: {sys.argv[2]} deleted successfully.")
        elif command == "update":
            if len(sys.argv) != UPDATE_COMMAND_LENGTH:
                print("Error: 'update' requires exactly 2 arguments.")
                print("Usage: python task_cli.py update <id> <description>")
            else:
                if sys.argv[3] != "":
                    operation_success = task_manager.update_item(int(sys.argv[2]), sys.argv[3])
                    if not operation_success:
                        print(f"Error: Task with ID: {sys.argv[2]} not found.")
                    else:
                        print(f"Task with ID: {sys.argv[2]} updated successfully")
                else:
                    print("Error: Description cannot be an empty string.")
                
        elif command == "mark-in-progress":
            if len(sys.argv) != MARK_STATUS_COMMAND_LENGTH:
                print("Error: 'mark-in-progress' requires exactly 1 argument.")
                print("Usage: python task_cli.py mark-in-progress <id>")
            else:
                operation_success = task_manager.mark_status(int(sys.argv[2]), "in-progress")
                if not operation_success:
                    print(f"Error: Task with ID: {sys.argv[2]} not found.")
                else:
                    print(f"Task with ID: {sys.argv[2]} marked as in-progress successfully.")

        elif command == "mark-done":
            if len(sys.argv) != MARK_STATUS_COMMAND_LENGTH:
                print("Error: 'mark-done' requires exactly 1 argument.")
                print("Usage: python task_cli.py mark-done <id>")
            else:
                operation_success = task_manager.mark_status(int(sys.argv[2]), "done")
                if not operation_success:
                    print(f"Error: Task with ID: {sys.argv[2]} not found.")
                else:
                    print(f"Task with ID: {sys.argv[2]} marked as done successfully.")
        elif command == "mark-todo":
            if len(sys.argv) != MARK_STATUS_COMMAND_LENGTH:
                print("Error: 'mark-todo' requires exactly 1 argument.")
                print("Usage: python task_cli.py mark-todo <id>")
            else:
                operation_success = task_manager.mark_status(int(sys.argv[2]), "todo")
                if not operation_success:
                    print(f"Error: Task with ID: {sys.argv[2]} not found.")
                else:
                    print(f"Task with ID: {sys.argv[2]} marked as todo successfully.")
        elif command == "list":
            if len(sys.argv) == LIST_WITHOUT_ARGUMENT_LENGTH:
                for item in tasks:
                    task_manager.print_item(item)
                    found_any_task = True
                if not found_any_task:
                        print("No tasks found.")
            elif len(sys.argv) == LIST_WITH_ARGUMENT_LENGTH:
                if sys.argv[2] in ["todo", "in-progress", "done"]:
                    for item in tasks:
                        if item["status"] == str(sys.argv[2]):
                            task_manager.print_item(item)
                            found_any_task = True
                    if not found_any_task:
                        print(f"No tasks found with status {sys.argv[2]}")
                else:
                    print(f"Error: Unknown status '{sys.argv[2]}' list requested")
                    print(f"Usage: python task_cli.py list [todo|in-progress|done]")
            else:
                print(f"Error: list takes 0 or 1 argument.")
                print(f"Usage: python task_cli.py list [todo|in-progress|done]")
        else:
            print(f"Error: Unknown command {command}")
            print(f"Usage: python task_cli.py [add|delete|update|mark-in-progress|mark-done|mark-todo|list] <args>")


        if sys.argv[1] in ["add", "delete", "update", "mark-in-progress", "mark-done", "mark-todo"] and operation_success:
            with open(TASK_FILE,"w") as file:
                    json.dump(tasks, file)

    except IndexError:
        print("Error: Missing arguments or command.\nUsage: python task_cli.py [add|delete|update|mark-in-progress|mark-done|list] <args>")
    except ValueError:
        print("Error: Invalid ID format. ID should be an integer.")
