from datetime import datetime
from typing import List, Optional, Union

from lmu.app_settings import AppSettings
from lmu.preset.preset import BasePreset, GraphicsPreset
from lmu.preset.settings_model import BenchmarkSettings
from lmu.rf2command import Command, CommandQueue
from lmu.rf2connect import RfactorState


class BenchmarkRun:
    id_counter = 0

    def __init__(self, name: str = None, presets: List[BasePreset] = None, settings: BenchmarkSettings = None):
        BenchmarkRun.id_counter += 1
        self.id = BenchmarkRun.id_counter
        self.name = name or str()
        self.presets: List[Union[BasePreset, GraphicsPreset]] = presets or list()
        self.settings: BenchmarkSettings = settings or BenchmarkSettings()


class BenchmarkQueue:
    queue: List[BenchmarkRun] = list()

    @classmethod
    def is_empty(cls):
        return len(cls.queue) == 0

    @classmethod
    def append(cls, run: BenchmarkRun):
        cls.queue.append(run)

    @classmethod
    def remove(cls, entry_id: int):
        for run in cls.queue:
            if run.id == entry_id:
                cls.queue.remove(run)
                return True
        return False

    @classmethod
    def next(cls) -> Optional[BenchmarkRun]:
        if not cls.is_empty():
            run = cls.queue.pop(0)
            run.name = f'{datetime.now().strftime("%Y%m%d-%H-%M")}_rF2_benchmark'
            return run

    @classmethod
    def reset(cls):
        cls.queue = list()


def create_benchmark_commands(ai_key: str, fps_key: str, recording_timeout: int, replay: Optional[str] = None):
    # Wait for UI
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=120.0))

    if replay is None:
        # -- Set session settings
        CommandQueue.append(Command(Command.set_session_settings, data=AppSettings.session_selection, timeout=10.0))
        # -- Set Content
        CommandQueue.append(Command(Command.set_content, data=AppSettings.content_selected, timeout=10.0))
        # Start Race Session
        CommandQueue.append(Command(Command.start_race, timeout=10.0))

    # -- Reset Session Settings
    AppSettings.session_selection = dict()
    # -- Reset Content Selection
    AppSettings.content_selected = dict()

    if replay is not None:
        # -- Load Replay
        CommandQueue.append(Command(Command.play_replay, data=replay, timeout=30.0))

    # Wait UI Loading State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.loading, timeout=90.0))
    # Wait UI Ready State
    CommandQueue.append(Command(Command.wait_for_state, data=RfactorState.ready, timeout=800.0))

    if replay is not None:
        # 5. Switch FullScreen
        CommandQueue.append(Command(Command.nav_action, data="NAV_TO_FULL_EVENT_MONITOR", timeout=30.0))
    else:
        # Drive
        CommandQueue.append(Command(Command.drive, timeout=10.0))
        # Timeout
        CommandQueue.append(Command(Command.timeout_command, data=2, timeout=10.0))
        # Ai Control
        # CommandQueue.append(Command(Command.press_key, data=ai_key, timeout=12.0))
        CommandQueue.append(Command(Command.ai_take_control, timeout=10.0))

    # Recording Timeout
    CommandQueue.append(Command(Command.timeout_command, data=recording_timeout, timeout=12.0))
    # Present mon record
    CommandQueue.append(Command(Command.record_benchmark, timeout=20.0))
    """
    # FPS Measure
    CommandQueue.append(Command(Command.press_ctrl_key, data=fps_key, timeout=12.0))
    # Timeout
    CommandQueue.append(Command(Command.timeout_command, data=20, timeout=10.0))
    # Record Performance
    CommandQueue.append(Command(Command.press_shift_key, data='DIK_SPACE', timeout=10.0))
    """


def create_quit_commands():
    # Hit ESC
    CommandQueue.append(Command(Command.press_key, data="DIK_ESCAPE"))
    # Hit Alt+F4
    CommandQueue.append(Command(Command.press_alt_key, data="DIK_F4"))

    CommandQueue.append(Command(Command.to_race_menu, timeout=10.0))
    CommandQueue.append(Command(Command.quit, timeout=5.0))
