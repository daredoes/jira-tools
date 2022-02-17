import requests
from requests.auth import HTTPBasicAuth
import os
from datetime import timedelta, datetime
import typer

app = typer.Typer()

JIRA_ORG_BASE_API_URL = "https://yourorg.atlassian.net" ## Set This

SPRINT_CREATION_API_URL = f"{JIRA_ORG_BASE_API_URL}/rest/agile/1.0/sprint"
GET_SPRINTS_FOR_BOARD_API_URL = f"{JIRA_ORG_BASE_API_URL}/rest/agile/1.0/board/"
headers = {"Content-Type": "application/json"}

auth = None

class JiraAPIWrapper():
    auth = None

    def set_auth(self, email, api_token):
        if api_token and email:
            self.auth = HTTPBasicAuth(email, api_token)

    
    def hit_jira_api(self, api, payload):
        response = requests.request(
            "POST",
            api,
            json=payload,
            headers=headers,
            auth=self.auth,
        )
        status_code = response.status_code
        if status_code == 201:
            data = response.json()
            return data
        elif status_code == 400:
            print("The request is invalid", response.content)
        elif status_code == 401:
            print("The user is not logged in.")
        elif status_code == 403:
            print("The user does not a have valid license.")
        elif status_code == 404:
            print(
                "The board does not exist or the user does not have permission to view it."
            )


    # Sends a pre-formatted request to a given URL
    def get_all_sprints(self, payload):
        return self.hit_jira_api(GET_SPRINTS_FOR_BOARD_API_URL, payload)

    # Sends a pre-formatted request to a given URL
    def create_sprint(self, payload):
        return self.hit_jira_api(SPRINT_CREATION_API_URL, payload)


# WIP
# @app.command()
# def continue_sprints(
#     boardId=typer.Option(
#         None,
#         help="The ID number of the board. Example of ID 240: https://faircorp.atlassian.net/jira/software/c/projects/CFM/boards/240/backlog",
#     ),
#     sprints=typer.Option(
#         1,
#         help="The number of sprints we want to create, starting from our current active sprint",
#     ),
# ):
#     pass


@app.command(name="Create Sprint(s)", help="Creates one or more sprints.")
def create_sprints(
    email: str = typer.Option(
        None,
        help="The email you use to log into JIRA with your organization",
    ),
    api_token: str = typer.Option(
        os.environ.get("JIRA_API_TOKEN", None),
        help="An API token for your account. Get one here: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/",
    ),
    name: str = typer.Option(
        None,
        help="The first part of the name that will be given to the final sprint name",
    ),
    start_date=typer.Option(
        None,
        help="A string in the format MM/DD/YYYY representing the first day of the first sprint we will create",
    ),
    boardId=typer.Option(
        None,
        help="The ID number of the board. Example of ID 240: https://faircorp.atlassian.net/jira/software/c/projects/CFM/boards/240/backlog",
    ),
    sprints=typer.Option(
        None,
        help="The number of sprints we want to create, starting from our starting date",
    ),
    start_sprint_count=typer.Option(
        None,
        help="An integer representing what 'number' sprint we want to consider this Example of 15: CFM 22.15",
    ),
    days_delta=typer.Option(
        None,
        help="An integer representing the distance in days that a sprint lasts. E.g. 14 days = 2 week sprints.",
    ),
):
    while not email:
        email = input("The email you use to log into JIRA with your organization: ")
    while not api_token:
        api_token = input("https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/\nAn API token for your account: ")
    while not name:
        name = input("The first part of the name that will be given to the final sprint name (CFM): ")
    parsed_start_date = None
    while not start_date:
        start_date = input("A string in the format MM/DD/YYYY representing the first day of the first sprint we will create: ")
        try:
            parsed_start_date = datetime.strptime(start_date, "%m/%d/%Y")
        except Exception:
            print(f"Bad date: {start_date}")
            start_date = None
    while not boardId:
        boardId = input("Example of ID 240: https://faircorp.atlassian.net/jira/software/c/projects/CFM/boards/240/backlog\nThe ID number of the board: ")
        try:
            int(boardId)
        except Exception:
            print("Not a valid number")
            boardId = None
    while not sprints:
        sprints = input("The number of sprints we want to create, starting from our starting date: ")
        try:
            int(sprints)
        except Exception:
            print("Not a valid number")
            sprints = None
    while not days_delta:
        days_delta = input("An integer representing the distance in days that a sprint lasts: ")
        try:
            int(days_delta)
        except Exception:
            print("Not a valid number")
            days_delta = None
    created_sprints = []
    api = JiraAPIWrapper()
    api.set_auth(email, api_token)
    # Shouldn't be possible
    if parsed_start_date is None:
        exit(1)
    for count, i in enumerate(range(0, sprints), start=start_sprint_count):
        the_date = parsed_start_date + timedelta(days=(i * days_delta) + 1)
        the_next_date = the_date + timedelta(days=days_delta + 1)
        payload = {
            "name": f"{name} {the_date.strftime('%y')}.{count} ({the_date.strftime('%m/%d')} - {the_next_date.strftime('%m/%d')})",
            "startDate": f"{the_date.strftime('%Y-%m-%d')}",
            "endDate": f"{the_next_date.strftime('%Y-%m-%d')}",
            "originBoardId": boardId,
            "goal": "",
        }
        response = api.create_sprint(payload)
        if response:
            created_sprints.append(response)
    print(f"Created the following sprints:\n\n{'\n'.join(created_sprints)}")


if __name__ == "__main__":
    app()