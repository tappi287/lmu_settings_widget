import re
from pathlib import Path

from lxml import etree

from lmu.utils import JsonRepr

EMPTY_LAP_STRING = "-:--.---"


def to_lap_time_string(lap_time: float) -> str:
    if lap_time == 0.0:
        return EMPTY_LAP_STRING
    s, ms = divmod(lap_time * 1000, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{m:01.0f}:{s:02.0f}.{ms:03.0f}"


def get_text_from_element(element: etree._Element | etree._ElementTree, tag: str, default_value=str()):
    sub_element = element.find(tag)
    if sub_element is None:
        return default_value
    return sub_element.text


class ResultsJsonRepr(JsonRepr):
    def to_js_object(self, export: bool = False) -> dict:
        js_dict = super().to_js_object()
        for k, v in js_dict.items():
            if isinstance(v, list) and v:
                if isinstance(v[0], (ResultsDriverEntry, ResultsLapEntry, ResultStreamEntry)):
                    v = [lv.to_js_object() for lv in v]

            js_dict[k] = v

        return js_dict


class ResultsLapEntry(ResultsJsonRepr):
    def __init__(self, e: etree._Element):
        self.num = int()
        self.p = int()
        self.s1 = str()
        self.s2 = str()
        self.s3 = str()
        self.topspeed = float()
        self.pit = bool()
        self.fcompound = str()
        self.rcompound = str()
        self.laptime = float()
        self.laptime_formatted = str()

        if e is not None:
            self.num, self.p = int(e.get("num", 0)), int(e.get("p", 0))
            self.s1, self.s2, self.s3 = (
                to_lap_time_string(float(e.get("s1", 0.0))),
                to_lap_time_string(float(e.get("s2", 0.0))),
                to_lap_time_string(float(e.get("s3", 0.0))),
            )
            self.topspeed = float(e.get("topspeed", 0.0))
            self.pit = bool(e.get("pit", 0))
            self.fcompound = e.get("fcompound", "")
            self.rcompound = e.get("rcompound", "")
            if e.text.replace(".", "").isnumeric():
                self.laptime = float(e.text)
                self.laptime_formatted = to_lap_time_string(self.laptime)


class ResultsDriverEntry(ResultsJsonRepr):
    def __init__(self, e: etree._Element = None):
        self.name = str()
        self.grid_position = int()
        self.class_grid_position = int()
        self.position = int()
        self.class_position = int()
        self.laps = list()
        self.race_laps = int()
        self.car_class = str()
        self.car_type = str()
        self.car_number = int()
        self.fastest_lap = float()
        self.fastest_lap_formatted = str()
        self.finish_time = float()
        self.finish_time_formatted = str()
        self.finish_delta = float()
        self.finish_delta_formatted = str()
        self.finish_delta_laps = int()
        self.finish_delta_laps_formatted = str()
        self.purple_lap_formatted = str()
        self.purple_s1 = str()
        self.purple_s2 = str()
        self.purple_s3 = str()

        if e is not None:
            self.name = get_text_from_element(e, "Name")
            self.grid_position = int(get_text_from_element(e, "GridPos", "0"))
            self.position = int(get_text_from_element(e, "Position", "0"))
            self.class_grid_position = int(get_text_from_element(e, "ClassGridPos", "0"))
            self.class_position = int(get_text_from_element(e, "ClassPosition", "0"))
            self.car_class = get_text_from_element(e, "CarClass", "0")
            self.car_type = get_text_from_element(e, "CarType")
            self.car_number = int(get_text_from_element(e, "CarNumber", "0"))
            for e_lap in e.iterfind("Lap"):
                self.laps.append(ResultsLapEntry(e_lap))
            f_laps = sorted([l.laptime for l in self.laps if l.laptime > 0.0])
            if f_laps:
                self.fastest_lap = f_laps[0]
            self.fastest_lap_formatted = to_lap_time_string(self.fastest_lap)
            self.race_laps = int(get_text_from_element(e, "Laps", "0"))
            self.finish_time = float(get_text_from_element(e, "FinishTime", "0.0"))
            self.finish_time_formatted = to_lap_time_string(self.finish_time)


class ResultStreamEntry(ResultsJsonRepr):
    SUPPORTED_TYPES = ("Incident",)

    def __init__(self, e: etree._Element = None):
        self.et = 0.0
        self.type = ""
        self.text = ""
        self.drivers = list()

        if e is not None:
            self.et = e.get("et", 0.0)
            self.text = e.text
            self.type = e.tag
            self.read_details()

    def read_details(self):
        if self.type == "Incident":
            vehicle_match = re.search("with\sanother\svehicle\s", self.text)
            start_match = re.search("\(\d{1,3}\)", self.text)

            if start_match:
                self.drivers.append(self.text[: start_match.start()])

            if vehicle_match:
                remaining_str = self.text[vehicle_match.end() :]
                dm = re.search("\(\d{1,3}\)", remaining_str)
                if dm:
                    self.drivers.append(remaining_str[: dm.start()])


class RfactorResults(ResultsJsonRepr):
    def __init__(self, file: Path = None):
        self.entries = list()
        self.drivers = list()
        self.racelaps = int()
        self.racetime = int()

        self._read_result_file(file)

    def _read_result_file(self, file: Path):
        if file is None or not file.exists():
            return

        with open(file, "r") as f:
            et: etree._ElementTree = etree.parse(f)

        self.racelaps = int(get_text_from_element(et, "RaceResults/RaceLaps", "0"))
        self.racetime = int(get_text_from_element(et, "RaceResults/RaceTime", "0"))

        for idx, element in enumerate(et.iterfind(".//Driver")):
            self.drivers.append(ResultsDriverEntry(element))
        self._create_global_data()

        stream_element = et.find("RaceResults/Race/Stream")
        stream_element = stream_element if stream_element is not None else []

        for element in stream_element:
            if element.tag in ResultStreamEntry.SUPPORTED_TYPES:
                self.entries.append(ResultStreamEntry(element))

    def _create_global_data(self):
        lead_times = dict()
        all_laps, all_s1, all_s2, all_s3 = list(), list(), list(), list()
        for driver in self.drivers:
            if driver.class_position == 1:
                lead_times[driver.car_class] = (driver.finish_time, driver.race_laps)
            all_laps += [lap.laptime for lap in driver.laps if lap.laptime > 0.0]
            all_s1 += [lap.s1 for lap in driver.laps if lap.s1 != EMPTY_LAP_STRING]
            all_s2 += [lap.s2 for lap in driver.laps if lap.s2 != EMPTY_LAP_STRING]
            all_s3 += [lap.s3 for lap in driver.laps if lap.s3 != EMPTY_LAP_STRING]

        purple_lap, purple_s1, purple_s2, purple_s3 = -1.0, -1.0, -1.0, -1.0
        if all_laps and all_s1 and all_s2 and all_s3:
            purple_lap = sorted(all_laps)[0]
            purple_s1 = sorted(all_s1)[0]
            purple_s2 = sorted(all_s2)[0]
            purple_s3 = sorted(all_s3)[0]

        for driver in self.drivers:
            lead_time, lead_laps = lead_times.get(driver.car_class, (None, None))
            if not lead_time:
                continue
            driver.finish_delta = max(0.0, driver.finish_time - lead_time)
            driver.finish_delta_formatted = to_lap_time_string(driver.finish_delta)
            driver.finish_delta_laps = max(0, lead_laps - driver.race_laps)
            if driver.finish_delta_laps:
                driver.finish_delta_laps_formatted = f"+{driver.finish_delta_laps}L"

            # Set Purple laps and sectors
            for lap in driver.laps:
                if lap.laptime == purple_lap:
                    driver.purple_lap_formatted = to_lap_time_string(lap.laptime)
                if lap.s1 == purple_s1:
                    driver.purple_s1 = purple_s1
                if lap.s2 == purple_s2:
                    driver.purple_s2 = purple_s2
                if lap.s3 == purple_s3:
                    driver.purple_s3 = purple_s3