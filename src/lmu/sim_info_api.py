"""
API wrapper for LMU shared memory.

This module provides a high-level API for accessing LMU's shared memory,
inheriting from the base SimInfo class in lmu_data.py.
"""
import ctypes
import logging
from typing import Optional

import psutil

from lmu.globals import GAME_EXECUTABLE
from lmu.pylmusharedmemory.lmu_data import LMUConstants


class SimInfoAPI:
    """Lightweight wrapper to check if LMU is running."""

    _last_known_pid = None

    @staticmethod
    def _check_shared_memory_exists():
        """
        Check if the LMU shared memory exists using Windows API.

        This is a cheap operation that doesn't create a new mapping.
        Uses OpenFileMappingW to check existence without creating the memory map.

        Returns:
            bool: True if shared memory exists, False otherwise.
        """
        try:
            kernel32 = ctypes.windll.kernel32
            OpenFileMappingW = kernel32.OpenFileMappingW
            OpenFileMappingW.argtypes = [ctypes.c_ulong, ctypes.c_bool, ctypes.c_wchar_p]
            OpenFileMappingW.restype = ctypes.c_void_p
            CloseHandle = kernel32.CloseHandle
            CloseHandle.argtypes = [ctypes.c_void_p]

            # FILE_MAP_READ = 4
            hMap = OpenFileMappingW(4, False, LMUConstants.LMU_SHARED_MEMORY_FILE)
            if hMap:
                CloseHandle(hMap)
                return True
            return False
        except Exception as e:
            logging.exception(e)
            return False

    ###########################################################
    @classmethod
    def is_game_running(cls):
        """
        Check if the game is currently running by enumerating processes.

        First checks the last known PID (fast), then falls back to full
        process enumeration (expensive) only if needed.

        Returns:
            bool: True if the game process is found, False otherwise.
        """
        # Fast path: check if last known PID is still valid
        if cls._last_known_pid is not None:
            try:
                p = psutil.Process(cls._last_known_pid)
                if p.name().lower() == GAME_EXECUTABLE.lower():
                    return True
            except psutil.NoSuchProcess:
                cls._last_known_pid = None

        # Slow path: enumerate all processes
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
                if p.name().lower() == GAME_EXECUTABLE.lower():
                    cls._last_known_pid = pid
                    return True
            except psutil.NoSuchProcess:
                continue

        cls._last_known_pid = None
        return False

    ###########################################################
    # Access functions
    @classmethod
    def get_last_known_pid(cls) -> Optional[int]:
        return cls._last_known_pid

    @classmethod
    def is_lmu_running(cls, check_process: bool = True):
        """
        Check if LMU is running.

        Uses fast shared memory existence check first, falls back to process
        enumeration only if shared memory is not available.

        is_lmu_running()
          ├─ Shared Memory Check (Windows API, ~0ms)
          └─ is_game_running()
              ├─ Last Known PID Check (fast, ~1ms)
              └─ Full Process Enumeration (slow, ~50-100ms)

        Returns:
            bool: True if LMU is running, False otherwise.
        """
        # Fast path: check if shared memory exists (Windows API, very cheap)
        if cls._check_shared_memory_exists():
            return True

        # Slow path: check if game process is running
        if check_process:
            return cls.is_game_running()
        else:
            return False
