### README_site_creation.md 
# An overview of how to create a new agromanagement file for use in the WOFOST simulator

1. To create a new agromanagement file, copy the template below into a <file_name>.yaml file
in the current directory
2. Fill out all fields marked with angle brackets < > 
3. Latitude, Longitude, and Year specify the historical weather to be drawn from
the NASA Power historical database. Ensure that 1984 <= year <= 2018 to avoid
missing data. Latitude must be in (-90, 90) and Longitude must be in (-180, 180)
4. Ensure that <crop_name> is registered in the ../crop_config/crops.yaml file
5. Ensure that <site_name> is registered in the ../site_conig/sites.yaml file
6. Ensure that <crop_variety> is a valid variety in the <crop_name>.yaml file
6. Ensure that <site_variation> is a valid variation in the <crop_name>.yaml file
7. Ensure that crop_start_date <= crop_end_date
8. To test the agromanagement file with inputted crop and site, run 
python test_wofost.py --agro_fpath <filename>.yaml

<yyyy-mm-dd - datetime>:
    Site:
        LATITUDE: < int >
        LONGITUDE: < int >
        YEAR: <int 1994 - 2018>
    CropCalendar:
        crop_name: <crop_name>
        crop_variety: <crop_variety>
        site_name: <site_name>
        site_variation: <site_variation>
        crop_start_date: <yyyy-mm-dd>
        crop_start_type: <sowing, emergence>
        crop_end_date: <yyyy-mm-dd>
        crop_end_type: <harvest, maturity, death>
        max_duration: <int>
    StateEvents:
    TimedEvents:
