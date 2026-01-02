"""To view the github user activity via CLI."""

import urllib.request
import json
import sys
from urllib.error import HTTPError, URLError


class GitHubActivityCLI:
    """Class to fetch and display GitHub user activity."""

    def __init__(self, user: str):
        self.username = user

    def fetch_activity(self) -> list:
        """Fetch user activity from GitHub API.

        Args:
            None

        Returns:
            list: List of repositories event raw data.
        """
        try:
            github_api_url = f"https://api.github.com/users/{self.username}/events"
            headers = {"User-Agent": "github-user-activity-cli"}
            request = urllib.request.Request(github_api_url, headers=headers)

            with urllib.request.urlopen(request) as response:
                repos_data = json.loads(response.read().decode("utf-8"))

            return repos_data
        except HTTPError as http_error:
            if http_error.code == 404:
                print(f"User '{self.username}' not found on GitHub.")
                return []
            if http_error.code == 403:
                print("API rate limit exceeded. Please try again later.")
                return []
            print(f"HTTP Error: {http_error.code}")
            return []
        except URLError as url_error:
            print(f"URL Error: {url_error.reason}")
            return []
        except Exception as error:
            print(f"Error fetching data from GitHub API: {error}")
            return []

    def _handle_create_event(self, event: dict) -> str:
        """Handle CreateEvent type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string for CreateEvent.
        """
        repo_name = event.get("repo", {}).get("name", "unknown_repository")
        payload = event.get("payload", {})
        ref = payload.get("ref", "unknown_ref")
        ref_type = event.get("payload", {}).get("ref_type", "unknown_ref_type")

        if ref_type == "repository":
            return f"Created a new repository '{repo_name}'"
        if ref_type == "tag":
            return f"Created a new tag '{ref}' in '{repo_name}'"
        if ref_type == "branch":
            return f"Created a new branch '{ref}' in '{repo_name}'"
        return f"Created a new '{ref}' in '{repo_name}'"

    def _handle_push_event(self, event: dict) -> str:
        """Handle PushEvent type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string for PushEvent.
        """
        repo_name = event.get("repo", {}).get("name", "unknown_repository")
        payload = event.get("payload", {})
        ref = payload.get("ref", "unknown_ref")
        if ref.startswith("refs/heads/"):
            branch = ref.replace("refs/heads/", "")
            return f"Pushed commit(s) to branch '{branch}' of '{repo_name}'"
        if ref.startswith("refs/tags/"):
            tag = ref.replace("refs/tags/", "")
            return f"Pushed commit(s) to tag '{tag}' of '{repo_name}'"
        return f"Pushed commit(s) to '{ref}' of '{repo_name}'"

    def _handle_delete_event(self, event: dict) -> str:
        """Handle DeleteEvent type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string for DeleteEvent.
        """
        repo_name = event.get("repo", {}).get("name", "unknown_repository")
        payload = event.get("payload", {})
        ref = (
            payload.get("ref", "unknown_ref")
            .removeprefix("refs/heads/")
            .removeprefix("refs/tags/")
        )
        ref_type = payload.get("ref_type", "unknown_ref_type")
        return f"Deleted {ref_type} '{ref}' from '{repo_name}'"

    def _handle_fork_event(self, event: dict) -> str:
        """Handle ForkEvent type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string for ForkEvent.
        """
        repo_name = event.get("repo", {}).get("name", "unknown_repository")
        forkee = event.get("payload", {}).get("forkee", {}).get("full_name")

        if forkee:
            return f"Forked '{repo_name}' to '{forkee}'"

        return f"Forked the repository '{repo_name}'"

    def _handle_watch_event(self, event: dict) -> str:
        """Handle WatchEvent type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string for WatchEvent.
        """
        repo_name = event.get("repo", {}).get("name", "unknown_repository")
        return f"Starred the repository '{repo_name}'"

    def _handle_issues_event(self, event: dict) -> str:
        """Handle IssuesEvent type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string for IssuesEvent.
        """
        repo_name = event.get("repo", {}).get("name", "unknown_repository")
        payload = event.get("payload", {})
        action = payload.get("action", "performed an action")
        issue_number = payload.get("issue", {}).get("number", "unknown_issue")
        user = event.get("actor", {}).get("login", "unknown_user")
        assignee_data = payload.get("issue", {}).get("assignee")
        assignee = (
            assignee_data.get("login", "unknown_assignee")
            if assignee_data
            else "unknown_assignee"
        )
        labels = payload.get("issue", {}).get("labels", [])
        label = labels[0].get("name", "unknown_label") if labels else "unknown_label"

        if action in [
            "opened",
            "edited",
            "deleted",
            "closed",
            "reopened",
            "transferred",
            "pinned",
            "unpinned",
            "locked",
            "unlocked",
        ]:
            return f"Issue #{issue_number} was {action} by {user} in {repo_name}"
        if action in ["assigned"]:
            return f"Issue #{issue_number} was {action} to {assignee} by {user} in {repo_name}"
        if action == "unassigned":
            return f"Issue #{issue_number} was {action} from {assignee} by {user} in {repo_name}"
        if action in ["labeled", "unlabeled"]:
            return (
                f"Issue #{issue_number} was {action} {label} by {user} in {repo_name}"
            )
        return (
            f"Performed an action {action} on issue {issue_number} of repo {repo_name}"
        )

    def _handle_pull_request_event(self, event: dict) -> str:
        """Handle PullRequestEvent type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string for PullRequestEvent.
        """
        repo_name = event.get("repo", {}).get("name", "unknown_repository")
        payload = event.get("payload", {})
        action = payload.get("action", "performed an action")
        pr_number = payload.get("number", "unknown_pr")
        title = payload.get("pull_request", {}).get("title", "unknown_title")
        actor = (
            payload.get("pull_request", {}).get("user", {}).get("login", "unknown_user")
        )
        return f"PR #{pr_number} '{title}' was {action} in {repo_name} by {actor}"

    def handle_output(self, event: dict) -> str:
        """Handle output based on event type.

        Args:
            event (dict): Event data.

        Returns:
            str: Formatted string based on event type.
        """
        event_type = event.get("type")

        handlers = {
            "CreateEvent": self._handle_create_event,
            "PushEvent": self._handle_push_event,
            "DeleteEvent": self._handle_delete_event,
            "ForkEvent": self._handle_fork_event,
            "WatchEvent": self._handle_watch_event,
            "IssuesEvent": self._handle_issues_event,
            "PullRequestEvent": self._handle_pull_request_event,
        }

        handler = handlers.get(event_type)

        if handler:
            return handler(event)

        return f"Unhandled event type: {event_type}"


def main():
    """Main function to run the CLI application."""

    if len(sys.argv) == 3:
        github_username = sys.argv[1]
        github_activity = GitHubActivityCLI(github_username)
        events = github_activity.fetch_activity()

        try:
            number_of_events = int(sys.argv[2])

            if number_of_events <= 0:
                raise ValueError("Number of events must be greater than zero")
        except ValueError:
            print("Please enter a valid integer for number of events.")
            return

        print("-" * 40)
        for event in events[:number_of_events]:
            display_string = github_activity.handle_output(event)
            print(display_string.strip())
        print("-" * 40)
    else:
        print(
            "Usage : python github_user_activity.py <github-username> <number of events>"
        )


if __name__ == "__main__":
    main()
