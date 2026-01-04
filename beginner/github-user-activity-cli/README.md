# GitHub User Activity CLI

## **Project Overview**
GitHub User Activity CLI is a command-line tool that allows you to fetch and display the recent activity of any GitHub user.
It shows events such as branch creation, commits, pull requests, issues, repository forks, tags, and more in a simple and readable format.
This project helps developers and learners understand GitHub activities programmatically and visualize user contributions.

---

## **Requirements**
- Python 3.8 or higher
- Internet connection
- Standard Python libraries (`urllib`, `json`, `sys`)
- No external dependencies required

---

## **Project Constraints**
- Only public repositories are supported; private repositories require authentication.
- GitHub API rate limits unauthenticated requests to 60 per hour.
- Only the most recent events (default API limit: 30) are fetched.
- Some GitHub events, like `MemberEvent` or `GollumEvent`, are not currently handled.
- Tags may not appear immediately in the API response after creation.

---

## **Implemented Features**
- Fetch recent GitHub events for a given user.
- Display formatted messages for the following events:
  - Branch creation and deletion
  - Commit pushes
  - Tag creation
  - Repository forks
  - Starred repositories
  - Issues (opened, closed, assigned, labeled, etc.)
  - Pull Requests (opened, merged, closed, etc.)
- Display a custom number of recent events via command-line argument.
- Handles common errors like invalid username, invalid input, API rate limits, and network errors.
- Support for adding GitHub Event Types in future
- Cache TTL: The CLI caches GitHub API responses for 15 minutes (900 seconds) to minimize unnecessary API requests while ensuring activity data remains sufficiently up to date for typical, low-frequency repository usage.

---

## **Requirements to Run the Tool**
- Python 3.8+ installed on your system
- Internet connection to fetch GitHub API data
- Access to public GitHub accounts

---

## **Installation**
1. Clone the repository:

    git clone <repo-url>
    cd github-user-activity-cli

2. Ensure Python is installed:

    python --version

3. How to Run

    python github_user_activity.py `github-username` `number-of-events`

    Parameters:<br>
        `github-username` – GitHub username to fetch activity for.
        `number-of-events` – Number of recent events to display (integer > 0).

    Example:<br>
        python github_user_activity.py seethavenkatesh0307 10

---

## Event Types Handled

Currently, the CLI handles the following GitHub events:

- CreateEvent – repository, branch, or tag creation
- PushEvent – commits pushed to branches or tags
- DeleteEvent – branch or tag deletion
- ForkEvent – repository forked
- WatchEvent – repository starred
- IssuesEvent – issue actions such as opened, closed, labeled, assigned
- PullRequestEvent – pull request actions such as opened, merged, closed
- Unhandled events will display: Unhandled event type: <EventType>

---

## Future Improvements

- Support pagination to fetch more than GitHub API’s default recent events.
    - GitHub APIs return data in pages. Pagination allows the CLI to fetch multiple pages to retrieve more than the default recent events limit.”

