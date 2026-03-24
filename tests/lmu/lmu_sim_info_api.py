import logging
import time

from lmu.sim_info_api import SimInfoAPI
from lmu.log import setup_logging

setup_logging(__name__)


def test_sim_info_api():
    sim_info_api = SimInfoAPI()
    logging.info("Starting test.")
    timeout = 120
    test_start_time = time.time()

    while True:
        start_time = time.time()
        logging.info(f"Is Running: {sim_info_api.is_lmu_running()} "
                     f"Shared Mem exists: {sim_info_api._check_shared_memory_exists()}")
        logging.info(f"Took {time.time() - start_time:.4f}s")
        time.sleep(1)

        if time.time() - test_start_time > timeout:
            logging.info("Timeout reached. Exiting.")
            break
