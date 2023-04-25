from textwrap import dedent as dedent_base


def get_extension(path: str):
    path_components = path[::-1].split('.')

    if len(path_components) > 0:
        return path_components[0][::-1]

    return None


def dedent(string: str):
    return dedent_base(string).replace('\n', ' ').strip()
