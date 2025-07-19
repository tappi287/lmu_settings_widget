import psutil
from lmu.log import setup_logger

logger = setup_logger(__name__)


def getDrivesInfo():
    hdds = []
    logger.debug("Getting HDDs info...")
    for partition in psutil.disk_partitions():
        hdds.append(partition.mountpoint)

    return hdds
