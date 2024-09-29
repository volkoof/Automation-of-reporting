def normalizing_paths(input_path: str, output_path: str, check_is_file: bool=True):
    """Нормализует входной и выходной пути

    Args:
        input_path (str): входной путь.
        output_path (str): выходной путь.
        check_is_file (bool): проверка на то, что путь ведет к файлу. По стандарту: True.
    """
    
    from os.path import normpath
    from pathlib import Path
    
    
    input_path = Path(normpath(input_path))
    if not input_path.exists():
        raise IsADirectoryError(f"Переданный путь '{str(input_path)}' не существует")
    if check_is_file and (not input_path.is_file()):
        raise IsADirectoryError(f"Переданный путь '{str(input_path)}' не является файлом")
    
    output_path = Path(normpath(output_path))
    if not output_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
    
    return input_path, output_path


def convert_to_csv(input_path: str="", output_path: str="", filename: str="data"):
    """Конвертирует .xlsx в .csv

    Args:
        input_path (str): путь к .xlsx файлу. По стандарту: "".
        output_path (str): путь к выходному .csv файлу. По стандарту: "".
        filename (str): имя выходного файла. По стандарту: "data".
    """
    
    from pandas import read_excel
    
    
    input_path, output_path = normalizing_paths(input_path, output_path)
    
    needed_columns = ["Создано", "Кем_решен_(группа)", "Статус", "Тип_запроса"]
    data = read_excel(input_path, header=0, usecols=needed_columns)
    data.to_csv(output_path.joinpath(filename + ".csv"), index=False)


def generate_data(dataframe, output_path: str, year: int, month: str):
    """Генерирует аггрегационные таблицы за один период

    Args:
        dataframe (DataFrame): данные.
        output_path (str): путь к папке с отчетами.
        year (int): год.
        month (str): месяц.
    """
    
    from programs.generate import Report_generator
    
    
    generator = Report_generator(data=dataframe, output_path=output_path, year=year, month=month)
    generator.first_list()
    generator.second_list()
    generator.third_list()
    
    
def get_reports_data(input_path: str="", output_path: str="./Reports/", pruning: bool=True):
    """Генерирует аггрегационные таблицы

    Args:
        input_path (str): путь к .csv файлу. По стандарту "".
        output_path (str): путь к папке с отчетами. По стандарту "./Reports/".
        pruning (bool): обрезка данных по последнему месяцу. По стандарту: True.
    """
    
    from pandas import read_csv, to_datetime
    
    
    # НОРМАЛИЗУЕМ ПУТИ
    input_path, output_path = normalizing_paths(input_path, output_path)
    
    # ПЕРВИЧНАЯ ПРЕДОБРАБОТКА
    data = read_csv(input_path, header=0)
    data["Создано"] = to_datetime(data["Создано"])
    data = data.sort_values(by="Создано")
    
    assert data["Создано"].isnull().sum() == 0
    
    data["Год"] = data["Создано"].dt.year
    data["Месяц"] = data["Создано"].dt.month_name()
    data = data.drop(columns="Создано")
    
    data["Тип группы"] = data["Кем_решен_(группа)"].apply(lambda x: 1 if x == "Горячая Линия ЦИСиТ" else 2)
    data = data.drop(columns="Кем_решен_(группа)")
    
    if pruning:
        last_row = data.tail(1)
        last_year, last_month = last_row["Год"].item(), last_row["Месяц"].item()
        data = data[(data["Год"] == last_year) & (data["Месяц"] == last_month)]
    
    points = (data["Год"].astype(str) + ' ' + data["Месяц"]).unique()
    
    for point in points:
        year, month = point.split()
        year = int(float(year))
        dataframe = data[(data["Год"] == year) & (data["Месяц"] == month)]
        dataframe = dataframe.drop(columns=["Год", "Месяц"])
        generate_data(dataframe=dataframe, output_path=output_path, year=year, month=month)