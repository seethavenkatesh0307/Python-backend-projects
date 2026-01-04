"""To view the github user activity via CLI."""

import urllib.request
import json
import sys

from pathlib import Path
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
import os
import getpass
import logging

# -------------------------------------
#   Configuration constants
# -------------------------------------

TIMEOUT_SECONDS = 10
CACHE_TTL_SECONDS = 900
MIN_CLI_ARGS_COUNT = 3
CLI_ARGS_COUNT_WITH_FILTER = 4
OUTPUT_SEPARATOR_WIDTH = 40
GITHUB_DEFAULT_EVENTS_PER_PAGE = 30


class GitHubAPIClient:
    """Class to fetch and display GitHub user activity."""

    def __init__(self, user: str):
        self.username = user
        self.headers = {"User-Agent": "github-user-activity-cli"}
        self.timeout = TIMEOUT_SECONDS
        self.timestamp: str | None = None

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
            logging.warning("No activity found for user '%s'.", self.username)

        self.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        return repos_data

    def _retry_request_with_token(self) -> list | None:
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
            return None

    def fetch_activity(self) -> list | None:
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
                return None
            logging.warning("HTTP Error: %d", http_error.code)
            return None
        except URLError as url_error:
            logging.warning("URL Error: %s", url_error.reason)
            return None
        except Exception as error:
            logging.warning("Error fetching data from GitHub API %s", error)
            return None


class GitHubEventHandler:
    """Class to formats different GitHub event types outputs."""

    HANDLERS = {
        "CreateEvent": "_handle_create_event",
        "PushEvent": "_handle_push_event",
        "DeleteEvent": "_handle_delete_event",
        "ForkEvent": "_handle_fork_event",
        "WatchEvent": "_handle_watch_event",
        "IssuesEvent": "_handle_issues_event",
        "PullRequestEvent": "_handle_pull_request_event",
    }

    @staticmethod
    def get_supported_events():
        """Get supported event types."""
        return set(GitHubEventHandler.HANDLERS.keys())

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

        handler_name = self.HANDLERS.get(event_type)

        if not handler_name:
            return f"Unhandled event type: {event_type}"

        handler = getattr(self, handler_name, None)

        if not callable(handler):
            return f"Handler not implemented for event type: {event_type}"

        return handler(event)


class EventsCacheHandler:
    """Class to handle caching of GitHub events."""

    @staticmethod
    def _get_cache_file_name(user: str) -> str:
        """Get cache file name for a user.

        Args:
            user (str): GitHub username.

        Returns:
            str: Cache file name.
        """
        return f".events_cache_{user}.json"

    def write_cache(self, user: str, cache: dict):
        """Writing events to cache file.

        Args:
            user (str): GitHub username.
        """
        cache_file = self._get_cache_file_name(user)
        try:
            with open(cache_file, "w", encoding="utf-8") as file:
                json.dump(cache, file, indent=4)
        except OSError as e:
            logging.warning("Failed to write cache file: %s", e)

    def _is_cache_expired(self, cached_at: str, ttl_seconds: int) -> bool:
        """Check if the cache is expired based on TTL.

        Args:
            cached_at (str): Timestamp when the cache was created.
            ttl_seconds (int): Time-to-live in seconds.

        Returns:
            bool: True if cache is expired, False otherwise.
        """
        try:
            cached_time = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            logging.warning("Invalid cache timestamp, treating cache as expired")
            return True
        now = datetime.now(timezone.utc)
        return (now - cached_time).total_seconds() > ttl_seconds

    def check_cache_usability(self, user: str) -> list | None:
        """Check if cache is usable and return cached events if valid.

        Args:
            user (str): GitHub username.

        Returns:
            list | None: Cached events if valid, None otherwise.
        """
        cache_file = self._get_cache_file_name(user)
        if not Path(cache_file).is_file():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as file:
                cached_data = json.load(file)
        except (OSError, json.JSONDecodeError) as e:
            logging.warning("Failed to read cache file: %s", e)
            return None

        timestamp = cached_data.get("timestamp")
        ttl = cached_data.get("ttl", CACHE_TTL_SECONDS)
        events = cached_data.get("events", [])

        if not isinstance(events, list):
            logging.warning("Invalid cache format, ignoring cache")
            return None

        if timestamp and not self._is_cache_expired(timestamp, ttl):
            return events

        return None


class CLIHandler:
    """Class to handle cli arguments and displaying output."""

    @staticmethod
    def parse_mandatory_cli_args() -> tuple[str | None, int | None]:
        """parse cli arguments.

        Returns:
            tuple[str, int] | None: github username and number of events
        """
        if len(sys.argv) < MIN_CLI_ARGS_COUNT:
            print(
                "Usage: python github_user_activity.py <github-username> <number of events> [event-type(optional)]"
            )
            return None, None

        github_username = sys.argv[1]

        try:
            number_of_events = int(sys.argv[2])
            if number_of_events <= 0:
                logging.error("Number of events must be greater than zero")
                return None, None

            if number_of_events > GITHUB_DEFAULT_EVENTS_PER_PAGE:
                logging.error(
                    "Number of events cannot exceed %s", GITHUB_DEFAULT_EVENTS_PER_PAGE
                )
                return None, None

        except ValueError:
            logging.error("Please enter a valid integer for number of events.")
            return None, None

        return github_username, number_of_events

    @staticmethod
    def parse_optional_cli_args(supported_events: set) -> str | None:
        """Parse optional cli arguments.

        Returns:
            str: event type if specified and valid, None otherwise.
        """
        if len(sys.argv) == CLI_ARGS_COUNT_WITH_FILTER:
            if sys.argv[3] in supported_events:
                return sys.argv[3]

            print("Invalid event type specified.")
            print("Supporting event types are: ", supported_events)

        return None


def main():
    """Main function to run the CLI application."""

    github_username, number_of_events = CLIHandler.parse_mandatory_cli_args()

    if not github_username or not number_of_events:
        return

    events_cache_handler = EventsCacheHandler()
    github_api_client = GitHubAPIClient(github_username)

    events = events_cache_handler.check_cache_usability(github_username)

    if not events:
        events = github_api_client.fetch_activity()
        if events:
            cache = {
                "timestamp": github_api_client.timestamp,
                "ttl": CACHE_TTL_SECONDS,
                "events": events,
            }
            events_cache_handler.write_cache(github_username, cache)

    if events:
        github_event_handler = GitHubEventHandler()
        supported_events = github_event_handler.get_supported_events()
        requested_event_type = CLIHandler.parse_optional_cli_args(supported_events)

        print("-" * OUTPUT_SEPARATOR_WIDTH)
        display_strings = []
        for event in events:
            if requested_event_type and event.get("type") != requested_event_type:
                continue
            display_strings.append(github_event_handler.handle_output(event))
            if len(display_strings) == number_of_events:
                break

        if display_strings:
            for display_string in display_strings:
                print(display_string)
        else:
            print("No events to display.")
        print("-" * OUTPUT_SEPARATOR_WIDTH)


if __name__ == "__main__":
    main()
