# CSV to KML Converter

This parser was created for converting data of Canadian FM radio stations.

This project is a simple Python script for converting a CSV file to a KML file using a GUI. It reads data from a CSV file, processes it, and generates a KML file that can be used in mapping tools like Google Earth.

## Features
- Designed specifically for data of Canadian FM radio stations.
- Converts CSV data to KML format.
- Sorts data by frequency and groups it into folders by class and city.
- Allows customization of input and output files through a user-friendly interface.

## Requirements
- Input CSV file must include columns like `FREQUENCY`, `CALL_SIGN`, `LAT_NEW`, `LON_NEW`, etc., in the correct format.
- Python 3
- pandas
- simplekml
- tkinter

Install dependencies using:
```
pip install pandas simplekml
```

## How to Use
5. Run the script from the terminal using `python script_name.py`.
### Example CSV Structure
Ensure your CSV file contains columns such as:
- `FREQUENCY`: Frequency of the station.
- `CALL_SIGN`: Call sign of the station.
- `LAT_NEW`, `LON_NEW`: Latitude and longitude in decimal degrees.

1. Run the script to open the GUI.
2. Select the CSV file you want to convert.
3. Choose the output location for the KML file.
4. Click "Convert to KML" to generate the KML file.

## License
MIT License


