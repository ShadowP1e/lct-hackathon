from urllib.parse import urljoin, urlparse


def remove_query_params(url: str) -> str:
    return urljoin(url, urlparse(url).path)
