import json

import gevent

from ..rf2events import RfactorQuitEvent
from ..utils import capture_app_exceptions


@capture_app_exceptions
def quit_rfactor():
    result = False
    RfactorQuitEvent.set(True)
    try:
        result = RfactorQuitEvent.quit_result.get(timeout=20.0)
    except gevent.Timeout:
        pass

    if result:
        return json.dumps({'result': True})
    else:
        return json.dumps({'result': False})
