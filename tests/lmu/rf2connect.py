from lmu import rf2connect
from lmu.rf2sharedmem.sharedMemoryAPI import SimInfoAPI


def test_get_request():
    rfc = rf2connect.RfactorConnect()
    rfc.update_web_ui_port()
    response = rfc.get_request("/rest/strategy/pitstop-estimate")
    # Endpoint: "/rest/garage/getVehicleCondition"
    data = {
        "brakeCondition": [1.0, 1.0, 1.0, 1.0],
        "fuel": 86.48464399078746,
        "fuelCapacity": 110.0,
        "suspensionDamage": [0.0, 0.0, 0.0, 0.0],
        "tireCondition": [1.0, 1.0, 1.0, 1.0],
        "vehicleDamage": 0.0,
    }
    # Endpoint: /rest/strategy/pitstop-estimate
    data = {
        "damage": 0.0,
        "driverSwap": 0.0,
        "fuel": 2.001394271850586,
        "penalties": 0.0,
        "tires": 0.0,
        "total": 2.001394271850586,
        "ve": 0.0,
    }
    print(response.text)


def test_sm_info():
    sim_info = SimInfoAPI()
    telemetry = sim_info.playersVehicleTelemetry()
    print(telemetry)
