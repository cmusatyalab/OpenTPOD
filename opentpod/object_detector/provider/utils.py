"""Uitlity functions for object detection providers.
"""
import shutil
import socket
from urllib import request

from django.conf import settings
from logzero import logger


def get_cache_entry(entry_name):
    cache_dir = settings.CACHE_DIR / entry_name
    if cache_dir.exists():
        return cache_dir
    else:
        return None


def download_and_extract_url_tarball_to_cache_dir(tarball_url, entry_name):
    """Download and extract tarball from url to a cache_dir
    entry_name: used as subdir name within the cache_dir. no '/' allowed
    """
    tarball_basename = tarball_url.split('/')[-1]
    download_to_file_path = settings.CACHE_DIR / tarball_basename
    with request.urlopen(tarball_url) as response, open(download_to_file_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    output_dir = settings.CACHE_DIR / entry_name
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.unpack_archive(download_to_file_path, output_dir)
    logger.info('downloading --> {} finished.'.format(output_dir))


def _find_open_port():
    """Use socket's built in ability to find an open port."""
    sock = socket.socket()
    sock.bind(('', 0))
    _, port = sock.getsockname()
    sock.close()
    return port
