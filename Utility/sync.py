import subprocess


def sync_files():
    rsync_command = [
        "rsync",
        "-avz",
        "--delete",  # Add this line
        "/Users/theokoester/dev/projects/python/CWA/cableops/",  # Source directory on Mac
        "theokoester@raspi:/home/theokoester/dev/cableops/"  # Destination directory on Raspberry Pi
    ]
    try:
        print('rsync')
        result = subprocess.run(rsync_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Rsync completed successfully")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error occurred while running rsync")
        print(e.stderr.decode())