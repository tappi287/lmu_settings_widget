import os

from lmu import rf2replays
from lmu.rf2results import RfactorResults


def test_set_test_result_files_mtime(set_test_install_location, test_data_output_dir):
    path = rf2replays.get_replays_location()
    replay_mtimes = list()
    for p in path.glob(f"*{rf2replays.REPLAY_FILE_SUFFIX}"):
        replay_mtimes.append(p.stat().st_mtime)

    results_path = test_data_output_dir.joinpath("Le Mans Ultimate/UserData/Log/Results")
    for p in results_path.glob("*.*"):
        if not p.is_file():
            continue
        if not replay_mtimes:
            break
        new_mtime = replay_mtimes.pop()
        os.utime(p, (p.stat().st_ctime, new_mtime))

    for p in results_path.glob("*.*"):
        print(p.name, p.stat().st_ctime, p.stat().st_mtime)


def test_result_read(set_test_install_location, test_data_output_dir):
    xml_file = test_data_output_dir.joinpath("Le Mans Ultimate/UserData/Log/Results/2024_10_24_23_38_59-61R1.xml")
    result = RfactorResults(xml_file)

    result_as_json = result.to_js_object()
    for entry in result_as_json["entries"]:
        print(entry)
