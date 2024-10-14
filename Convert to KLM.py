import pandas as pd
import simplekml
import tkinter as tk
from tkinter import filedialog, messagebox

# Функция для преобразования CSV в KML
def convert_csv_to_kml(csv_file, output_file):
    df = pd.read_csv(csv_file, delimiter=';', on_bad_lines='skip')
    df.columns = df.columns.str.upper()  # Приводим все заголовки к верхнему регистру
    print("Заголовки столбцов в CSV файле:", df.columns.tolist())

    # Сортируем данные по частоте по возрастанию
    df = df.sort_values(by='FREQUENCY')

    # Создаем объект KML
    kml = simplekml.Kml()

    # Создаем словарь папок для каждого класса
    folders = {}
    unique_classes = df['CLASS'].unique()
    for class_name in unique_classes:
        folders[class_name] = kml.newfolder(name=f"Class {class_name}")

    # Создаем основную папку для городов
    city_main_folder = kml.newfolder(name="Cities")

    # Создаем словарь папок для каждого города внутри основной папки
    city_folders = {}
    unique_cities = sorted(df['CITY'].unique())  # Сортируем города по алфавиту
    for city_name in unique_cities:
        city_folders[city_name] = city_main_folder.newfolder(name=f"{city_name}")

    # Проходим по каждой строке и добавляем точку в соответствующую папку KML
    for _, row in df.iterrows():
        # Определяем мощность в зависимости от поляризации и типа антенны
        ant_mode = row['ANT_MODE'].lower() if 'ANT_MODE' in row else 'unknown'
        if ant_mode == 'o':
            # Круговая антенна
            if 'ERPHAV' in row and not pd.isna(row['ERPHAV']):
                power_kw = row['ERPHAV'] / 1000  # Используем горизонтальную среднюю мощность
                ant_mode_short = 'H'
            elif 'ERPVAV' in row and not pd.isna(row['ERPVAV']):
                power_kw = row['ERPVAV'] / 1000  # Используем вертикальную среднюю мощность
                ant_mode_short = 'V'
            ant_mode_desc = 'ДН: Круговая'
        elif ant_mode == 'd':
            # Направленная антенна
            azimuth = row['RAD_CENTER'] if 'RAD_CENTER' in row else 'N/A'
            ant_mode_desc = f'ДН: Направленная. Азимут: {azimuth}°'
            if 'ERPVPK' in row and not pd.isna(row['ERPVPK']):
                power_kw = row['ERPVPK'] / 1000  # Используем пиковую мощность в вертикальной поляризации
            else:
                power_kw = 0.0  # Если данных нет, мощность устанавливается в 0
            ant_mode_short = 'D'  # Указываем направленную антенну
        else:
            power_kw = 0.0
            ant_mode_short = 'Unknown'
            ant_mode_desc = 'ДН: Неизвестная поляризация'

        # Формируем название точки: [FREQUENCY]: [CALL_SIGN] - [Power в кВт]
        frequency = row['FREQUENCY']
        call_sign = row['CALL_SIGN']
        azimuth = row['RAD_CENTER'] if 'RAD_CENTER' in row else 'N/A'
        name = f"{frequency}: {call_sign} (V/H(kW): {round(row['ERPVPK']/1000, 2)}/{round(row['ERPHPK']/1000, 2)} | Azm: {azimuth}°)"

        # Формируем описание из остальных данных
        class_mapping = {
            'A': "CLASS: A. \nERP: < 6 kW. Зона обслуживания: небольшие сообщества или пригородные районы.",
            'A1': "CLASS: A1. \nERP: < 0.25 kW. \nЗона обслуживания: ограничена географическими областями и для покрытия небольших сообществ.",
            'B': "CLASS: B. \nERP: от 6 kW до 50 kW. \nЗона обслуживания: используется в небольших городах и крупных населённых пунктах.",
            'C': "CLASS: C. \nERP: > 50 kW. \nЗона обслуживания: большие географические области, крупные города и прилегающие регионы. Это радиостанции, которые имеют региональное или национальное покрытие.",
            'C1': "CLASS: C1. \nERP: < 100 kW и высота антенны (EHAAT) до 299 м. \nЗона обслуживания: большие географические области, крупные города и прилегающие регионы. Это радиостанции, которые имеют региональное или национальное покрытие.",
            'C2': "CLASS: C2. \nERP: < 50 kW и высота антенны (EHAAT) до 150 м. \nЗона обслуживания: большие географические области, крупные города и прилегающие регионы. Это радиостанции, которые имеют региональное или национальное покрытие.",
            'D': "CLASS: D. Это маломощные или вспомогательные передатчики, которые работают как повторители основной станции. Зона обслуживания: обычно не имеют фиксированного покрытия и могут изменяться в зависимости от условий лицензии.",
            'LP': "CLASS: LP. ERP: < 0.25 kW. Зона обслуживания: ограниченная и специализированная на локальной или узкой аудитории.",
            'VLP': "CLASS: VLP. ERP: < 0.01 kW. Зона обслуживания: применяется в учебных заведениях или внутри помещений."
        }
        class_desc = class_mapping.get(row['CLASS'], f"CLASS: {row['CLASS']} - информация о классе отсутствует.")
        beam_tilt = f"BEAM_TILT: {row['BEAM_TILT']}°"
        ehaatt = f"EHAATT: {row['EHAATT']} м"
        coordinates = f"Координаты: {row['LAT_NEW']} {row['LON_NEW']}"
        description = f"{class_desc} {ant_mode_desc} {beam_tilt} {ehaatt} {coordinates}"

        # Широта и долгота
        latitude = float(row['LAT_NEW'].replace(',', '.'))
        longitude = float(row['LON_NEW'].replace(',', '.'))

        # Добавляем точку в соответствующую папку KML
        folder = folders.get(row['CLASS'], kml)
        city_folder = city_folders.get(row['CITY'], kml)

        # Добавляем точку в папки по классу и городу
        folder.newpoint(name=name, description=description, coords=[(longitude, latitude)])
        city_folder.newpoint(name=name, description=description, coords=[(longitude, latitude)])

    # Сохраняем в KML файл
    kml.save(output_file)
    messagebox.showinfo("Готово", "Преобразование завершено!")

# Функция для выбора входного файла
def select_input_file():
    file_path = filedialog.askopenfilename(title="Выберите CSV файл", filetypes=[("CSV файлы", "*.csv")])
    input_path_entry.delete(0, tk.END)
    input_path_entry.insert(0, file_path)

# Функция для выбора выходного файла
def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Сохранить KML файл как", defaultextension=".kml", filetypes=[("KML файлы", "*.kml")])
    output_path_entry.delete(0, tk.END)
    output_path_entry.insert(0, file_path)

# Функция для запуска преобразования
def start_conversion():
    input_file = input_path_entry.get()
    output_file = output_path_entry.get()
    if not input_file or not output_file:
        messagebox.showwarning("Ошибка", "Пожалуйста, выберите входной и выходной файлы.")
        return
    try:
        try:
            convert_csv_to_kml(input_file, output_file)
        except KeyError as ke:
            messagebox.showerror("Ошибка", f"Отсутствует столбец: {ke}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка при преобразовании: {e}")

# Создаем графический интерфейс
root = tk.Tk()
root.title("CSV to KML Converter")

# Элементы интерфейса
input_path_label = tk.Label(root, text="Выберите CSV файл:")
input_path_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
input_path_entry = tk.Entry(root, width=50)
input_path_entry.grid(row=0, column=1, padx=10, pady=5)
input_path_button = tk.Button(root, text="Обзор...", command=select_input_file)
input_path_button.grid(row=0, column=2, padx=10, pady=5)

output_path_label = tk.Label(root, text="Выберите путь для сохранения KML файла:")
output_path_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
output_path_entry = tk.Entry(root, width=50)
output_path_entry.grid(row=1, column=1, padx=10, pady=5)
output_path_button = tk.Button(root, text="Обзор...", command=select_output_file)
output_path_button.grid(row=1, column=2, padx=10, pady=5)

convert_button = tk.Button(root, text="Преобразовать в KML", command=start_conversion)
convert_button.grid(row=2, column=1, pady=20)

# Запуск главного цикла приложения
root.mainloop()