import os


def parse_path(path):
    if ':' in path:
        package_name, name = path.split(':', 1)
        if not name:
            raise ValueError("Empty config file name")

        try:
            package = __import__(package_name, fromlist=package_name.split('.'))
        except ImportError as exc:
            raise ValueError from exc

        package_dir = os.path.dirname(package.__file__)
        return os.path.join(package_dir, name)
    else:
        return os.path.abspath(os.path.expanduser(path))
