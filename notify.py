import os
import sys
import subprocess
import re
import time
import signal
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def sendMessage(message):
    url = 'https://notify-api.line.me/api/notify'
    post_fields = {'message': message}

    request = Request(url, urlencode(post_fields).encode())
    request.add_header("Authorization", os.environ['LINE_NOTIFY'])
    urlopen(request)


statePattern = re.compile("JobState=([\w]+)")
reasonPattern = re.compile("Reason=([\w]+)")
exitCodePattern = re.compile("ExitCode=([\w:]+)")


def get_job_info(job):
    output = subprocess.run(
        ["scontrol", "-o", "show", "job", job], capture_output=True, text=True)
    if (output.returncode != 0):
        return {
            "error": output.stderr
        }
    stdout = output.stdout
    return {
        "state": statePattern.search(stdout).group(1),
        "reason": reasonPattern.search(stdout).group(1),
        "exitCode": exitCodePattern.search(stdout).group(1)
    }


def info_message(current, prev=None):
    messages = []
    changed = False
    if prev is None:
        prev = current
    for key in current:
        if (key in prev and prev[key] != current[key]):
            changed = True
            messages.append(f"{key}: {jobInfo[key]} ← {prevJobInfo[key]}")
        elif key not in prev:
            changed = True
            messages.append(f"{key}: {jobInfo[key]}")
        else:
            messages.append(f"{key}: {jobInfo[key]}")
    return "\n".join(messages), changed


if __name__ == '__main__':
    assert os.environ.get('LINE_NOTIFY') is not None \
        and os.environ['LINE_NOTIFY'].startswith("Bearer "), \
        "\"LINE_NOTIFY\" environment variable must be set to \"Bearer <access_token>\""
    assert len(sys.argv) > 1, "JobID must be provided"

    job = sys.argv[1]

    jobInfo = get_job_info(job)
    message, *_ = info_message(jobInfo)
    sendMessage(f"Monitoring {job} started:\n{message}")

    def stop(*_):
        sendMessage(f"Monitoring {job} stopped")
        sys.exit(0)
    signal.signal(signal.SIGINT, stop)

    while True:
        time.sleep(60)
        prevJobInfo = jobInfo
        jobInfo = get_job_info(job)
        message, changed = info_message(jobInfo, prevJobInfo)

        if changed:
            sendMessage(f"Monitoring {job}:\n{message}")
