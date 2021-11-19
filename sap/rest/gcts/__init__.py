"""gCTS REST calls"""

# ABAP Package: SCTS_ABAP_AND_VCS


def package_name_from_url(url):
    """Parse out Package name from a repo git url"""

    url_repo_part = url.split('/')[-1]

    if url_repo_part.endswith('.git'):
        return url_repo_part[:-4]

    return url_repo_part
