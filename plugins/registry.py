"""EPyMARL registry extension hooks.

Create your own learners/controllers/env wrappers inside ``plugins/`` and
import/register them in :func:`register_plugins`.  This module is imported by
utility scripts (for example ``scripts/run_once.py``) before executing the core
EPyMARL entrypoint so that your components are visible to the upstream
``REGISTRY`` tables.
"""

from __future__ import annotations

from typing import Callable

try:
    from controllers import REGISTRY as MACS
    from learners import REGISTRY as LEARNERS
    from envs import REGISTRY as ENVS
except ImportError:
    # When EPyMARL is not on the path yet (e.g. docs build), just provide
    # fallbacks so that importing this file does not crash.
    MACS = {}
    LEARNERS = {}
    ENVS = {}


def register_plugins(register: Callable[[], None] | None = None) -> None:
    """Entry point for custom registrations.

    Parameters
    ----------
    register:
        Optional callable for dependency injection in tests.  When ``None``
        (default) this function will look for inline registration code written
        by the user.  Keep your imports inside this function so that EPyMARL is
        only touched when the file is executed.
    """

    if register is not None:
        register()
        return

    # Example (to be filled in by the user once their components exist):
    # from plugins.algos.my_algo.learner import MyLearner
    # LEARNERS["my_learner"] = MyLearner
    #
    # from plugins.controllers.my_controller import MyController
    # MACS["my_controller"] = MyController
    #
    # from plugins.custom_envs.my_wrapper import MyEnvWrapper
    # ENVS["my_env"] = MyEnvWrapper
    pass


# Execute immediately so that simply importing this module registers
# everything.  Downstream scripts should ``import plugins.registry`` without
# touching register_plugins directly.
register_plugins()
