# scopes allow you to switch between basic transport and other lib.* solutions
# to deploy on different architectural stacks.
# Every lib module used should implement a basic interface.

import sys


if len(sys.argv) > 1:
    scope_name = sys.argv[1]
    if scope_name == 'common':
        from .common import *
    elif scope_name == 'reader':
        from .reader import *
    elif scope_name == 'alerter':
        from .alerter import *
    elif scope_name == 'infer':
        from .infer import *
    elif scope_name == 'cleaner':
        from .cleaner import *
    elif scope_name == 'api':
        from .api import *
    elif scope_name == 'counter':
        from .counter import *
    elif scope_name == 'reporter':
        from .reporter import *
    elif scope_name == 'listener':
        from .listener import *
else:
    from .common import *
