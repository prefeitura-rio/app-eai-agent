import argparse
import sys

import requests

REQUEST_TIMEOUT_SECONDS = 30


def delete_agent_version(version_number: int, agent_type: str) -> None:
    from src.config import env

    url = f"{env.EAI_AGENT_URL_PROD}api/v1/unified-delete"
    headers = {"Authorization": f"Bearer {env.EAI_AGENT_TOKEN_PROD}"}
    params = {
        "version_number": version_number,
        "agent_type": agent_type,
    }

    try:
        response = requests.delete(
            url, headers=headers, params=params, timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        print(response.text)
    except requests.exceptions.Timeout:
        print(
            f"Error: request timed out after {REQUEST_TIMEOUT_SECONDS} seconds.", file=sys.stderr
        )
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        print(f"Error: HTTP {exc.response.status_code} – {exc.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete an agent version from the PROD environment."
    )
    parser.add_argument(
        "--version-number", type=int, required=True, help="Version number to delete (integer)."
    )
    parser.add_argument(
        "--agent-type", type=str, required=True, help="Agent type to delete (e.g. agentic_search)."
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required flag to confirm the deletion. Without this flag the script will not run.",
    )
    args = parser.parse_args()

    if not args.confirm:
        print(
            "Aborted: pass --confirm to execute the DELETE request against PROD.",
            file=sys.stderr,
        )
        sys.exit(1)

    delete_agent_version(version_number=args.version_number, agent_type=args.agent_type)