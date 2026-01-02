"""To view the github user activity via CLI."""

import urllib.request
import json
import sys
from urllib.error import HTTPError, URLError
import os
import getpass
import logging


class GitHubAPIClient:
    """Class to fetch and display GitHub user activity."""

    def __init__(self, user: str):
        self.username = user
        self.headers = {"User-Agent": "github-user-activity-cli"}
        self.timeout = 10

    def _get_github_token(self) -> str | None:
        """Get github token.

        Returns:
            str: GitHub token.
        """

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            try:
                token = getpass.getpass("Enter GitHub token: ")
            except (KeyboardInterrupt, EOFError):
                logging.warning("Input cancelled by user")
                return None
            except OSError as e:
                logging.warning("Cannot read input: %s", e)
                return None
        return token

    def _make_request(self, headers: dict) -> list:
        """Request github url without token.

        Args:
            headers (dict) : headers to be sent with request.

        Returns:
            list : List of repositories event raw data.
        """
        github_api_url = f"https://api.github.com/users/{self.username}/events"

        request = urllib.request.Request(github_api_url, headers=headers)

        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            repos_data = json.loads(response.read().decode("utf-8"))

        if not repos_data:
            logging.info("No activity found for user '%s'.", self.username)

        return repos_data

    def _retry_request_with_token(self) -> list:
        """Retry request with authentication token.

        Returns:
            list: List of repositories event raw data.
        """
        try:
            token = self._get_github_token()
            if not token:
                return []

            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {token}"

            return self._make_request(headers)
        except HTTPError as auth_error:
            logging.warning("Authentication failed or access denied: %s", auth_error)
            return []

    def fetch_activity(self) -> list:
        """Fetch user activity from GitHub API.

        Args:
            None

        Returns:
            list: List of repositories event raw data.
        """
        try:
            return self._make_request(self.headers)
        except HTTPError as http_error:
            if http_error.code == 401:
                return self._retry_request_with_token()

            if http_error.code == 403:
                logging.warning(
                    "Access forbidden or rate limit may have been exceeded. "
                    "Try again with a token or wait and retry."
                )
                # Optionally, retry for access issue
                return self._retry_request_with_token()

            if http_error.code == 404:
                logging.warning(
                    "User '%s' not found on GitHub or Access denied.", self.username
                )
                return []
            logging.warning("HTTP Error: %d", http_error.code)
            return []
        except URLError as url_error:
            logging.warning("URL Error: %s", url_error.reason)
            return []
        except Exception as error:
            logging.warning("Error fetching data from GitHub API %s", error)
            return []


class GitHubEventHandler:
    """Class to formats different GitHub event types outputs."""

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
        github_api_client = GitHubAPIClient(github_username)
        events = github_api_client.fetch_activity()

        try:
            number_of_events = int(sys.argv[2])
            if number_of_events <= 0:
                raise ValueError("Number of events must be greater than zero")
        except ValueError:
            logging.error("Please enter a valid integer for number of events.")
            return

        if events:
            github_event_handler = GitHubEventHandler()

            print("-" * 40)
            for event in events[:number_of_events]:
                display_string = github_event_handler.handle_output(event)
                print(display_string.strip())
            print("-" * 40)
    else:
        print(
            "Usage : python github_user_activity.py <github-username> <number of events>"
        )


if __name__ == "__main__":
    main()
