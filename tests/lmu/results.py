from lmu.rf2results import RfactorResults


def test_result_read(set_test_install_location, test_data_output_dir):
    xml_file = test_data_output_dir.joinpath("Le Mans Ultimate/UserData/Log/Results/2024_10_24_23_38_59-61R1.xml")
    result = RfactorResults(xml_file)

    result_as_json = result.to_js_object()
    for entry in result_as_json["entries"]:
        print(entry)
