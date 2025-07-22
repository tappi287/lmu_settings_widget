from typing import Optional

import eel

from lmu.app import app_launch_fn


@eel.expose
def get_last_launch_method():
    return app_launch_fn.get_last_launch_method()


@eel.expose
def run_rfactor(server_info: Optional[dict] = None, method: Optional[int] = 0):
    return app_launch_fn.run_rfactor(server_info, method)


@eel.expose
def run_steamvr():
    return app_launch_fn.run_steamvr()


@eel.expose
def get_open_kneeboard_location():
    return app_launch_fn.get_open_kneeboard_location()


@eel.expose
def run_open_kneeboard():
    return app_launch_fn.run_open_kneeboard()


def expose_launch_methods():
    """empty method we import to have the exposed methods registered"""
    pass
