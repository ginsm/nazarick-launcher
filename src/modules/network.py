import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse
from collections import defaultdict
import threading

from modules import constants

DEFAULT_PER_HOST = 4
_per_host_semaphore_dict = defaultdict(lambda: threading.Semaphore(constants.MAX_CONNECTIONS_PER_HOST))


def make_session(pool_maxsize, total_retries=5, backoff_factor=0.5):
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods={"GET", "HEAD", "OPTIONS"},
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(
        max_retries=retry,
        pool_connections=32,
        pool_maxsize=max(1, pool_maxsize),
        pool_block=True
    )
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def per_host_semaphore(url):
    """
    Allows throttling concurrent downloads for each host
    """
    host = (urlparse(url).hostname or "").lower()
    return _per_host_semaphore_dict[host]