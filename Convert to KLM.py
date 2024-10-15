import pandas as pd
import simplekml
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to convert CSV to KML
def convert_csv_to_kml(csv_file, output_file):
    df = pd.read_csv(csv_file, delimiter=';', on_bad_lines='skip')
    df.columns = df.columns.str.upper()  # Convert all headers to uppercase
    print("Column headers in CSV file:", df.columns.tolist())

    # Sort data by frequency in ascending order
    df = df.sort_values(by='FREQUENCY')

    # Create KML object
    kml = simplekml.Kml()

    # Create folder dictionary for each class
    folders = {}
    unique_classes = df['CLASS'].unique()
    for class_name in unique_classes:
        folders[class_name] = kml.newfolder(name=f"Class {class_name}")

    # Create main folder for cities
    city_main_folder = kml.newfolder(name="Cities")

    # Create folder dictionary for each city within the main folder
    city_folders = {}
    unique_cities = sorted(df['CITY'].unique())  # Sort cities alphabetically
    for city_name in unique_cities:
        city_folders[city_name] = city_main_folder.newfolder(name=f"{city_name}")

    # Iterate over each row and add point to corresponding KML folder
    for _, row in df.iterrows():
        # Determine power depending on polarization and antenna type
        ant_mode = row['ANT_MODE'].lower() if 'ANT_MODE' in row else 'unknown'
        if ant_mode == 'o':
            # Omnidirectional antenna
            if 'ERPHAV' in row and not pd.isna(row['ERPHAV']):
                power_kw = row['ERPHAV'] / 1000  # Use horizontal average power
                ant_mode_short = 'H'
            elif 'ERPVAV' in row and not pd.isna(row['ERPVAV']):
                power_kw = row['ERPVAV'] / 1000  # Use vertical average power
                ant_mode_short = 'V'
            ant_mode_desc = 'Radiation Pattern: Omnidirectional'
        elif ant_mode == 'd':
            # Directional antenna
            azimuth = row['RAD_CENTER'] if 'RAD_CENTER' in row else 'N/A'
            ant_mode_desc = f'Radiation Pattern: Directional. Azimuth: {azimuth}°'
            if 'ERPVPK' in row and not pd.isna(row['ERPVPK']):
                power_kw = row['ERPVPK'] / 1000  # Use peak power in vertical polarization
            else:
                power_kw = 0.0  # If no data, set power to 0
            ant_mode_short = 'D'  # Indicate directional antenna
        else:
            power_kw = 0.0
            ant_mode_short = 'Unknown'
            ant_mode_desc = 'Radiation Pattern: Unknown polarization'

        # Formulate point name: [FREQUENCY]: [CALL_SIGN] - [Power in kW]
        frequency = row['FREQUENCY']
        call_sign = row['CALL_SIGN']
        azimuth = row['RAD_CENTER'] if 'RAD_CENTER' in row else 'N/A'
        name = f"{frequency}: {call_sign} (V/H(kW): {round(row['ERPVPK']/1000, 2)}/{round(row['ERPHPK']/1000, 2)} | Azm: {azimuth}°)"

        # Formulate description from remaining data
        class_mapping = {
            'A': "CLASS: A. \nERP: < 6 kW. Service Area: small communities or suburban areas.",
            'A1': "CLASS: A1. \nERP: < 0.25 kW. \nService Area: geographically restricted and for small communities.",
            'B': "CLASS: B. \nERP: 6 kW to 50 kW. \nService Area: used in small towns and large populated areas.",
            'C': "CLASS: C. \nERP: > 50 kW. \nService Area: large geographic areas, major cities, regional or national coverage.",
            'C1': "CLASS: C1. \nERP: < 100 kW and antenna height (EHAAT) up to 299 m. \nService Area: large geographic areas, major cities, regional or national coverage.",
            'C2': "CLASS: C2. \nERP: < 50 kW and antenna height (EHAAT) up to 150 m. \nService Area: large geographic areas, major cities, regional or national coverage.",
            'D': "CLASS: D. Low-power or auxiliary transmitters acting as repeaters. \nService Area: usually do not have fixed coverage and may change based on licensing conditions.",
            'LP': "CLASS: LP. ERP: < 0.25 kW. \nService Area: limited and targeted for local or narrow audience.",
            'VLP': "CLASS: VLP. ERP: < 0.01 kW. \nService Area: used in educational institutions or indoors."
        }
        class_desc = class_mapping.get(row['CLASS'], f"CLASS: {row['CLASS']} - no information available.")
        beam_tilt = f"BEAM_TILT: {row['BEAM_TILT']}°"
        ehaatt = f"EHAATT: {row['EHAATT']} m"
        coordinates = f"Coordinates: {row['LAT_NEW']} {row['LON_NEW']}"
        description = f"{class_desc} {ant_mode_desc} {beam_tilt} {ehaatt} {coordinates}"

        # Latitude and longitude
        latitude = float(row['LAT_NEW'].replace(',', '.'))
        longitude = float(row['LON_NEW'].replace(',', '.'))

        # Add point to corresponding KML folder
        folder = folders.get(row['CLASS'], kml)
        city_folder = city_folders.get(row['CITY'], kml)

        # Add point to folders by class and city
        folder.newpoint(name=name, description=description, coords=[(longitude, latitude)])
        city_folder.newpoint(name=name, description=description, coords=[(longitude, latitude)])

    # Save to KML file
    kml.save(output_file)
    messagebox.showinfo("Done", "Conversion completed!")

# Function to select input file
def select_input_file():
    file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    input_path_entry.delete(0, tk.END)
    input_path_entry.insert(0, file_path)

# Function to select output file
def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Save KML file as", defaultextension=".kml", filetypes=[("KML files", "*.kml")])
    output_path_entry.delete(0, tk.END)
    output_path_entry.insert(0, file_path)

# Function to start conversion
def start_conversion():
    input_file = input_path_entry.get()
    output_file = output_path_entry.get()
    if not input_file or not output_file:
        messagebox.showwarning("Error", "Please select both input and output files.")
        return
    try:
        try:
            convert_csv_to_kml(input_file, output_file)
        except KeyError as ke:
            messagebox.showerror("Error", f"Missing column: {ke}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion: {e}")

# Create GUI
root = tk.Tk()
root.title("CSV to KML Converter")

# Interface elements
input_path_label = tk.Label(root, text="Select CSV file:")
input_path_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
input_path_entry = tk.Entry(root, width=50)
input_path_entry.grid(row=0, column=1, padx=10, pady=5)
input_path_button = tk.Button(root, text="Browse...", command=select_input_file)
input_path_button.grid(row=0, column=2, padx=10, pady=5)

output_path_label = tk.Label(root, text="Select path to save KML file:")
output_path_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
output_path_entry = tk.Entry(root, width=50)
output_path_entry.grid(row=1, column=1, padx=10, pady=5)
output_path_button = tk.Button(root, text="Browse...", command=select_output_file)
output_path_button.grid(row=1, column=2, padx=10, pady=5)

convert_button = tk.Button(root, text="Convert to KML", command=start_conversion)
convert_button.grid(row=2, column=1, pady=20)

# Start main application loop
root.mainloop()