#!/usr/bin/env python3

import hashlib
import hmac
import http
import json
import os
import requests
import sys

from datetime import datetime, timezone

def perror(message: str) -> None:
    """
    Prints a message to stderr.

    :param message: The message to print
    :type message: :class:`str`
    """

    print(f"ERROR: {message}", file=sys.stderr)

def getenv(var: str) -> str:
    """
    Tries to get the value of an environment variable.
    If the variable is unset, exits with status 1.

    :param var: The environment variable to try getting a value for
    :type var: :class:`str`
    :return: The environment variable
    :rtype: :class:`str`
    """

    if (val := os.getenv(var)) is None:
        perror(f"{var} is unset")
        exit(1)

    return val

def gettime() -> str:
    """
    Gets the current time (UTC) in ISO 8601 format.

    :return: The current time in ISO 8601 format
    :rtype: :class:`str`
    """
    return datetime.now(
        timezone.utc
    ).isoformat()

def hmac_sha256(key: str, message: str) -> str:
    """
    Gets an HMAC-SHA256 digest for a given key and message.

    :param key: The key to use
    :type key: :class:`str`
    :param message: The message to digest
    :type message: :class:`str`
    """

    return hmac.new(
        key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

def main() -> None:
    # Try getting environment variables
    url       = getenv("APPLY_URL")
    secret    = getenv("APPLY_SECRET")
    name      = getenv("APPLY_NAME")
    email     = getenv("APPLY_EMAIL")
    cv_link   = getenv("APPLY_CV_LINK")

    repo_link = getenv("GIT_REPO_LINK")
    run_link  = getenv("GIT_RUN_LINK")

    payload = json.dumps({
        "timestamp": gettime(),
        "name": name,
        "email": email,
        "resume_link": cv_link,
        "repository_link": repo_link,
        "action_run_link": run_link,
    }, separators=(",", ":"))

    headers = {
        "X-Signature-256": f"sha256={hmac_sha256(secret, payload)}"
    }

    resp = requests.post(
        url=url,
        headers=headers,
        data=payload
    )

    if resp.ok is False:
        perror(
            f"Failed submitting: ({resp.status_code}) {resp.text}"
        )
        return

    print(
        "Successfully submitted\n"
        f"Response: {resp.text}"
    )

if __name__ == "__main__":
    try:
        main()

    except (EOFError, KeyboardInterrupt):
        pass
