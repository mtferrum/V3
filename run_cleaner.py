import os
from lib.basic_logger import log
from scope.cleaner import config


def get_files_and_size(path, extension):
    """
    Loads files inside a dir with specific extension into list, ordered by their
    respective date of creation. Oldest to newest. Computes size of all files by
    given path with respect to their file extension.

    :param path: Str containing full path to dir
    :param extension: Str. Only files with this extension will be processed
    :return: List [dir_size, [path1, path2, ...]]
    """
    size = 0
    files = []
    for entry in os.scandir(path):
        if entry.is_file and entry.name.endswith(extension) and not entry.name.startswith('.'):
            size += entry.stat().st_size
            files.append(entry.path)
    return [size / 10**9, sorted(files, key=lambda file: os.stat(file).st_mtime, reverse=True)]


if __name__ == '__main__':
    log.info('cleaner Start cleaning dir...')
    path = config.find('reader/videos_path')
    max_size = config.find('reader/max_videos_size')
    extension = config.find('reader/ext')
    log.info('cleaner Getting files list by path={}...'.format(path))
    try:
        size, files = get_files_and_size(path, extension)
        files_len_before = len(files)
        log.info('cleaner Got number of files={}'.format(files_len_before))
        log.info('cleaner Start removing old files...')
        log.info('cleaner Maximum dir size={} Gb, current size={} Gb'.format(max_size, size))
        while files and size > max_size:
            file = files.pop()
            size -= os.path.getsize(file) / 10**9  # Bytes to Gigabytes
            os.remove(file)
        files_len_after = len(files)
        log.info('cleaner Old files removed.')
        log.info('cleaner Number of files after cleaning={}'.format(files_len_after))
        log.info('cleaner Number of files deleted={}'.format(files_len_before - files_len_after))
        log.info('cleaner Current dir size={} Gb'.format(size))
    except OSError as e:
        log.exception(e)
    log.info('cleaner Finished cleaning.')