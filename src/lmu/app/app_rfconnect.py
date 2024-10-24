import eel

from . import app_rfconnect_fn


def expose_rfconnect_methods():
    """empty method we import to have the exposed methods registered"""
    pass


@eel.expose
def quit_rfactor():
    return app_rfconnect_fn.quit_rfactor()
