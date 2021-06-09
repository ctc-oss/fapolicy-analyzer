from inspect import currentframe


def f(formatString):
    frame = currentframe().f_back
    return eval(f'f"""{formatString}"""', frame.f_locals, frame.f_globals)
