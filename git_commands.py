import subprocess 
import re 


def git_fetch():
    git_fetch = subprocess.run(['git', 'fetch'], capture_output=True, text=True)
    return git_fetch.stdout.strip()


def git_differences(Type: str):
    git_fetch()
    if Type == "long_hash":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%H'], capture_output=True, text=True)
    elif Type == "commit_message":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%s'], capture_output=True, text=True)
    elif Type == "short_hash":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%h'], capture_output=True, text=True)
    elif Type == "short_hash_with_commit_message":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%h %s'], capture_output=True, text=True)
    elif Type == "commit_count":
        git_log = subprocess.run(['git', 'rev-list', '--count', 'HEAD..@{u}'], capture_output=True, text=True)
    if Type != "commit_count":
        return git_log.stdout.strip().splitlines()
    return git_log.stdout.strip()

def git_url_origin():
    git_fetch()
    git_url_origin = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    return git_url_origin.stdout.strip().removesuffix('.git')

def git_show(file):
    git_fetch()
    git_show = subprocess.run(['git', 'show', file], capture_output=True, text=True)
    return git_show.stdout.strip()

def get_remote_version() -> str | None:
    try:
        git_fetch()
        Do_Not_Disturb_content = git_show("origin/main:Do_Not_Disturb.py")
        Version = re.search(r"__Version__\s*=\s*['\"]([^'\"]+)['\"]", Do_Not_Disturb_content).group(1)
        return Version
    except Exception:
        return None


def author_name():
    url_origin = git_url_origin()
    return url_origin.split('/')[-2]

def commit_links():
    url_origin = git_url_origin()
    long_hashes = git_differences("long_hash")
    return [f"{url_origin}/commit/{long_hash}" for long_hash in long_hashes]

def git_pull():
    git_fetch()
    git_pull = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    return git_pull.stdout.strip()

def parse_git_diff(diff_text: str) -> list:
    files = []
    current_file = None
    current_hunk = None

    for line in diff_text.splitlines():
        # Identify start of a file diff
        if line.startswith("diff --git"):
            if current_file:
                if current_hunk:
                    current_file["hunks"].append(current_hunk)
                    current_hunk = None
                files.append(current_file)

            match = re.search(r"diff --git a/(.*?) b/(.*)", line)
            file_a = match.group(1) if match else ""
            file_b = match.group(2) if match else ""

            current_file = {"file_a": file_a, "file_b": file_b, "hunks": []}

        # Identify start of a diff hunk (e.g., @@ -1,3 +1,4 @@)
        elif line.startswith("@@"):
            if current_file is not None:
                if current_hunk:
                    current_file["hunks"].append(current_hunk)

                current_hunk = {"header": line, "lines": []}

        # Collect lines inside the hunk
        elif current_hunk is not None:
            current_hunk["lines"].append(line)

    # Append last file and hunk
    if current_file:
        if current_hunk:
            current_file["hunks"].append(current_hunk)
        files.append(current_file)

    return files

def git_diff(type: str):
    if type == "stat":
        git_diff_stat = subprocess.run(['git', 'diff', '--stat', 'HEAD..@{u}'], capture_output=True, text=True)
        return git_diff_stat.stdout.strip()
    elif type == "Files":
        git_diff = subprocess.run(['git', 'diff', 'HEAD..@{u}'], capture_output=True, text=True)

        return parse_git_diff(git_diff.stdout.strip())