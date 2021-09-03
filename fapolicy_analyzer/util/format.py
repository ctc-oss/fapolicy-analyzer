import re
from inspect import currentframe


def f(formatString):
    frame = currentframe().f_back
    return (
        eval(f'f"""{formatString}"""', frame.f_locals, frame.f_globals)
        if formatString
        else formatString
    )


def snake_to_camelcase(string):
    return (
        string[:1].lower()
        + re.sub(
            r"[\-_\.\s]([a-z])", lambda matched: matched.group(1).upper(), string[1:]
        )
        if string
        else string
    )
