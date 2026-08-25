import subprocess 


def git_fetch():
    git_fetch = subprocess.run(['git', 'fetch'], capture_output=True, text=True)
    return git_fetch.stdout.strip()


def git_log(Type: str):
    if Type == "long_hash":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%H'], capture_output=True, text=True)
    elif Type == "commit_message":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%s'], capture_output=True, text=True)
    elif Type == "short_hash":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%h'], capture_output=True, text=True)
    elif Type == "short_hash_with_commit_message":
        git_log = subprocess.run(['git', 'log', 'HEAD..@{u}', '--format=%h %s'], capture_output=True, text=True)
    return git_log.stdout.strip()


def git_url_origin():
    git_url_origin = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    return git_url_origin.stdout.strip().removesuffix('.git')


def git_pull():
    git_pull = subprocess.run(['git', 'pull'], capture_output=True, text=True)
    return git_pull.stdout.strip()


def author_name():
    url_origin = git_url_origin()
    return url_origin.split('/')[-2]

def commit_links():
    git_url_origin = git_url_origin()
    long_hash = git_log("long_hash")
    return f"{git_url_origin}/commit/{long_hash}"