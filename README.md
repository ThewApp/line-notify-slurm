# line-notify-slurm
Python script to monitor Slurm job and send a notification through LINE Notify

## Usage

1. Get LINE Notify personal token from https://notify-bot.line.me/
1. Set `LINE_NOTIFY` environment variable.
    ```sh
    export LINE_NOTIFY="Bearer <access_token>"
    ```
1. Start monitoring `jobID`
    ```sh
    python notify.py <jobID>
    ```
