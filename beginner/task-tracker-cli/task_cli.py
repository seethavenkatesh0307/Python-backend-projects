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

    def print_item(self, task_item: dict):
        """Printing task item.
        Args:
            task_item (dict): Task item to be printed.

        Returns:
            None
        """
        print(f"ID : {task_item['id']}")
        print(f"Description : {task_item['description']}")
        print(f"Status : {task_item['status']}")
        print(f"Created At : {task_item['createdAt']}")
        print(f"Updated At : {task_item['updatedAt']}")
        print("-" * 40)


class CommandHandler:
    """Handles different types of input commands."""
    def __init__(self, task_manager:TaskManager):
        self.task_manager = task_manager

    def handle_add_command(self) -> bool:
        """Handling add task item.
        
        Returns:
            bool: True if task is added successfully, False otherwise.
        """
        try:
            if len(sys.argv) != ADD_COMMAND_LENGTH or sys.argv[2] == "":
                print("Error: 'add' requires exactly 1 argument and cannot be empty string.")
                print("Usage: python task_cli.py add <description>")
                return False

            addition_status = self.task_manager.add_item(str(sys.argv[2]))
            if addition_status:
                print(f" Task '{sys.argv[2]}' is added successfully")
            return addition_status
        except IndexError:
            print("Error: Missing arguments or command.\nUsage: python task_cli.py add <description>")
            return False

    def handle_del_command(self) -> bool:
        """Handling delete task item.
        
        Returns:
            bool: True if task is deleted successfully, False otherwise.
        """
        try:
            if len(sys.argv) != DELETE_COMMAND_LENGTH:
                print("Error: 'delete' requires exactly 1 argument.")
                print("Usage: python task_cli.py delete <id>")
                return False

            deletion_status = self.task_manager.delete_item(int(sys.argv[2]))
            if not deletion_status:
                print(f"Error: Task with ID {sys.argv[2]} not found.")
            else:
                print(f"Task with ID: {sys.argv[2]} deleted successfully.")
            return deletion_status
        except IndexError:
            print("Error: Missing arguments or command.\nUsage: python task_cli.py delete <id>")
            return False
        except ValueError:
            print("Error: Invalid ID format. ID should be an integer.")
            return False

    def handle_update_command(self) -> bool:
        """Handling update task item.
        
        Returns:
            bool: True if task is updated successfully, False otherwise.
        """
        try:
            if len(sys.argv) != UPDATE_COMMAND_LENGTH:
                print("Error: 'update' requires exactly 2 arguments.")
                print("Usage: python task_cli.py update <id> <description>")
                return False

            if sys.argv[3] != "":
                updation_status = self.task_manager.update_item(int(sys.argv[2]), sys.argv[3])
                if not updation_status:
                    print(f"Error: Task with ID: {sys.argv[2]} not found.")
                else:
                    print(f"Task with ID: {sys.argv[2]} updated successfully")
                return updation_status

            print("Error: Description cannot be an empty string.")
            return False
        except IndexError:
            print("Error: Missing arguments or command.\nUsage: python task_cli.py update <id> <description>")
            return False
        except ValueError:
            print("Error: Invalid ID format. ID should be an integer.")
            return False

    def handle_mark_in_progress_command(self) -> bool:
        """Handling mark-in-progress task item.
        
        Returns:
            bool: True if task is marked successfully, False otherwise.
        """
        try:
            if len(sys.argv) != MARK_STATUS_COMMAND_LENGTH:
                print("Error: 'mark-in-progress' requires exactly 1 argument.")
                print("Usage: python task_cli.py mark-in-progress <id>")
                return False

            mark_status = self.task_manager.mark_status(int(sys.argv[2]), "in-progress")
            if not mark_status:
                print(f"Error: Task with ID: {sys.argv[2]} not found.")
            else:
                print(f"Task with ID: {sys.argv[2]} marked as in-progress successfully.")
            return mark_status
        except IndexError:
            print("Error: Missing arguments or command.\nUsage: python task_cli.py mark-in-progress <id>")
            return False
        except ValueError:
            print("Error: Invalid ID format. ID should be an integer.")
            return False

    def handle_mark_done_command(self) -> bool:
        """Handling mark-done task item.
        
        Returns:
            bool: True if task is marked successfully, False otherwise.
        """
        try:
            if len(sys.argv) != MARK_STATUS_COMMAND_LENGTH:
                print("Error: 'mark-done' requires exactly 1 argument.")
                print("Usage: python task_cli.py mark-done <id>")
                return False

            mark_status = self.task_manager.mark_status(int(sys.argv[2]), "done")
            if not mark_status:
                print(f"Error: Task with ID: {sys.argv[2]} not found.")
            else:
                print(f"Task with ID: {sys.argv[2]} marked as done successfully.")
            return mark_status
        except IndexError:
            print("Error: Missing arguments or command.\nUsage: python task_cli.py mark-done <id>")
            return False
        except ValueError:
            print("Error: Invalid ID format. ID should be an integer.")
            return False

    def handle_mark_todo_command(self) -> bool:
        """Handling mark-todo task item.
        
        Returns:
            bool: True if task is marked successfully, False otherwise.
        """
        try:
            if len(sys.argv) != MARK_STATUS_COMMAND_LENGTH:
                print("Error: 'mark-todo' requires exactly 1 argument.")
                print("Usage: python task_cli.py mark-todo <id>")
                return False

            mark_status = self.task_manager.mark_status(int(sys.argv[2]), "todo")
            if not mark_status:
                print(f"Error: Task with ID: {sys.argv[2]} not found.")
            else:
                print(f"Task with ID: {sys.argv[2]} marked as todo successfully.")
            return mark_status
        except IndexError:
            print("Error: Missing arguments or command.\nUsage: python task_cli.py mark-todo <id>")
            return False
        except ValueError:
            print("Error: Invalid ID format. ID should be an integer.")
            return False

    def handle_list_command(self) -> bool:
        """Handling list task items.
        
        Returns:
            bool: True if tasks are listed successfully, False otherwise.
        """
        try:
            found_any_task = False
            if len(sys.argv) == LIST_WITHOUT_ARGUMENT_LENGTH:
                for item in self.task_manager.tasks:
                    self.task_manager.print_item(item)
                    found_any_task = True
                if not found_any_task:
                    print("No tasks found.")
                    return False
                return True
            if len(sys.argv) == LIST_WITH_ARGUMENT_LENGTH:
                if sys.argv[2] in ["todo", "in-progress", "done"]:
                    for item in self.task_manager.tasks:
                        if item["status"] == str(sys.argv[2]):
                            self.task_manager.print_item(item)
                            found_any_task = True
                    if not found_any_task:
                        print(f"No tasks found with status {sys.argv[2]}")
                        return False
                    return True

                print(f"Error: Unknown status '{sys.argv[2]}' list requested")
                print("Usage: python task_cli.py list [todo|in-progress|done]")
                return False

            print("Error: list takes 0 or 1 argument.")
            print("Usage: python task_cli.py list [todo|in-progress|done]")
            return False
        except IndexError:
            print("Error: Missing arguments or command.\nUsage: python task_cli.py list [todo|in-progress|done]")
            return False

class JSONHandler:
    """Handles reading and writing tasks to JSON file."""
    def read_tasks_from_json(self) -> list:
        """Read tasks from JSON file.
        
        Returns:
            list: list of tasks from JSON if available, else empty list 
        """
        if Path(TASK_FILE).exists():
            try:
                with open(TASK_FILE, "r", encoding="utf-8") as file:
                    tasks_list = json.load(file)
                if tasks_list is None:
                    return []
                return tasks_list
            except json.JSONDecodeError:
                print(f"Invalid JSON exist. Overwriting {TASK_FILE} with empty task list.")
                return []
        else:
            with open(TASK_FILE, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
            return []
  
    def write_tasks_to_json(self, tasks_list: list):
        """Write tasks to JSON file.
        
        Args:
            tasks (list): List of tasks to be written to JSON file.
        """
        with open(TASK_FILE,"w", encoding="utf-8") as file:
            json.dump(tasks_list, file, indent=4)

if __name__ == "__main__":

    json_handler = JSONHandler()

    tasks = json_handler.read_tasks_from_json()

    task_manager = TaskManager(tasks)
    command_handler = CommandHandler(task_manager)

    try:
        command = sys.argv[1]
        operation_success = False

        if command == "add":
            operation_success = command_handler.handle_add_command()
        elif command == "delete":
            operation_success = command_handler.handle_del_command()
        elif command == "update":
            operation_success = command_handler.handle_update_command()           
        elif command == "mark-in-progress":
            operation_success = command_handler.handle_mark_in_progress_command()
        elif command == "mark-done":
            operation_success = command_handler.handle_mark_done_command()
        elif command == "mark-todo":
            operation_success = command_handler.handle_mark_todo_command()
        elif command == "list":
            operation_success = command_handler.handle_list_command()
        else:
            print(f"Error: Unknown command {command}")
            print("Usage: python task_cli.py [add|delete|update|mark-in-progress|mark-done|mark-todo|list] <args>")


        if command in ["add", "delete", "update", "mark-in-progress", "mark-done", "mark-todo"] and operation_success:
            json_handler.write_tasks_to_json(task_manager.tasks)

    except IndexError:
        print("Error: Missing arguments or command.")
        print("Usage: python task_cli.py [add|delete|update|mark-in-progress|mark-done|list] <args>")
