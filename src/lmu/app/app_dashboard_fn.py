import json

from ..lmu_game import RfactorPlayer
from ..utils import capture_app_exceptions


@capture_app_exceptions
def get_rf_driver():
    rf = RfactorPlayer()
    if rf.is_valid:
        return json.dumps({'result': rf.options.driver_options.to_js()})

    return json.dumps({'result': False, 'msg': rf.error})
