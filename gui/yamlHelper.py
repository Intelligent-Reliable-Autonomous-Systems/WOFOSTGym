"""
yamlHelper.py

Written by Mason Schuster, 2025
"""
import yaml
from datetime import date

AGRO_FOLDER_PATH = "env_config/agro"

def getCropStartType(crop_name):
    if crop_name in ["grape"]:
        return "endodorm"
    return "sowing"

def createAgroYaml(agroInfo={}, create=False):
    crop_name = agroInfo.get("crop_name", "N/A")
    crop_start_type = getCropStartType(crop_name) if crop_name != "N/A" else "N/A"

    agroYaml = {
        "AgroManagement": {
            "SoilCalendar": {
                "latitude": agroInfo.get("latitude", "N/A"),
                "longitude": agroInfo.get("longitude", "N/A"),
                "year": agroInfo.get("year", "N/A"),
                "soil_name": agroInfo.get("soil_name", "N/A"),
                "soil_variation": agroInfo.get("soil_variation", "N/A"),
                "soil_start_date": agroInfo.get("soil_start_date", date(2020, 1, 1)),
                "soil_end_date": agroInfo.get("soil_end_date", date(2020, 12, 31)),
            },
            "CropCalendar": {
                "crop_name": crop_name,
                "crop_variety": agroInfo.get("crop_variety", "N/A"),
                "crop_start_date": agroInfo.get("crop_start_date", date(2020, 1, 1)),
                "crop_start_type": crop_start_type,
                "crop_end_date": agroInfo.get("crop_end_date", date(2020, 12, 31)),
                "crop_end_type": agroInfo.get("crop_end_type", "N/A"),
                "max_duration": agroInfo.get("max_duration", "N/A"),
            }
        }
    }

    if create:
        try:
            filePath = f"{AGRO_FOLDER_PATH}/{agroInfo["file_name"]}.yaml"
            
            with open(filePath, "w") as file:
                yaml.dump(agroYaml, file, default_flow_style=False, sort_keys=False)

        except Exception as e:
            print(f"-WOFOST- Error creating agro YAML file: {e}")
            return None
    else:
        filePath = "none"

    
    return {"file_path": filePath, "agro_yaml": agroYaml}
