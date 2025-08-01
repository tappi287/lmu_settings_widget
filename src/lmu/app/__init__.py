from .app_main import expose_main_methods
from .app_launch import expose_launch_methods
from .app_presets import expose_preset_methods
from .app_controller import expose_controller_methods
from .app_dashboard import expose_dashboard_methods
from .app_rfconnect import expose_rfconnect_methods
from .app_replay import expose_replay_methods
from .app_results import expose_results_methods
from .app_benchmark import expose_benchmark_methods
from .app_content import expose_content_methods
from .performance_api import expose_performance_api_methods


def expose_app_methods():
    expose_main_methods()
    expose_launch_methods()
    expose_preset_methods()
    expose_controller_methods()
    expose_dashboard_methods()
    expose_rfconnect_methods()
    expose_replay_methods()
    expose_results_methods()
    expose_benchmark_methods()
    expose_content_methods()
    expose_performance_api_methods()
