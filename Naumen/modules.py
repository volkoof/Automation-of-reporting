def __normalizing_paths(input_path: str, output_path: str, check_is_file: bool=True):
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


def convert_to_csv(input_path: str, output_path: str=""):
    """Конвертирует .xlsx в .csv

    Args:
        input_path (str): путь к .xlsx файлу.
        output_path (str): путь к выходному .csv файлу. По стандарту: "".
    """
    
    from pandas import read_excel
    import warnings
    
    
    needed_columns = ["Дата регистрации", "Системный статус", "Услуга", "Тип запроса", "Процент использования SLA", "Фактическая длительность выполнения запроса (SLA)",
        "Кем решен (группа)", "Качество проведения работ по Запросу (оценка пользователя)", "Результат работ"
    ]
    
    input_path, output_path = __normalizing_paths(input_path, output_path)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        data = read_excel(input_path, header=0, engine="openpyxl", usecols=needed_columns, sheet_name="Запросы")
        data.to_csv(output_path.joinpath(input_path.stem + ".csv"), index=False)


def __convert_to_datetime(data: str):
    """Конвертирует дату в удобный формат

    Args:
        data (str): дата.
    """
    
    from pandas import to_datetime, NaT
    from datetime import datetime, timedelta
    
    
    try:
        return to_datetime(data)
    except:
        try:
            init_epoch = datetime(1899, 12, 30)
            delta = timedelta(days=float(data))
            return init_epoch + delta
        except:
            NaT
        
        
def __get_month_name(month_name: str) -> str:
    """Переводит названия месяцов с английского на русский язык

    Args:
        month_name (str): название месяца на английском языке

    Returns:
        str: название месяца на русском языке
    """
    
    english_to_russian = {
        "January": "Январь",
        "February": "Февраль",
        "March": "Март",
        "April": "Апрель",
        "May": "Май",
        "June": "Июнь",
        "July": "Июль",
        "August": "Август",
        "September": "Сентябрь",
        "October": "Октябрь",
        "November": "Ноябрь",
        "December": "Декабрь"
    }
    
    return english_to_russian[month_name]


def __transform_group(group: str) -> str:
    """Переводит указанную группу в другую в соответствии со спецификой отчета

    Args:
        group (str): входная группа

    Returns:
        str: выходная группа
    """
    
    if group in ["IT__L2_B2B", "IT__Центр компетенций"]:
        return "IT__2-БП-ФАЦ"
    if group == "Менеджеры услуги Прочее_IT":
        return "IT__1-СД-ФАЦ"
    return group

        
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
    generator.incidents_and_service_requests()
    generator.services()
    generator.lifetimes()
    generator.metrics()
    generator.funnel_targets()
    generator.dynamic_of_KIAS()
    generator.funnel_dynamics()
    generator.dynamics_of_closing_orders()


def get_reports_data(input_path: str, output_path: str="./Reports/Data/", pruning: bool=True):
    """Формирует аггрегационные таблицы за все периоды

    Args:
        input_path (str): путь к .csv файлу.
        output_path (str): путь к папке с таблицами. По стаднарту: "./Reports/Data/".
        pruning (bool): обрезка данных по последнему месяцу. По стандарту: True.
    """
    
    from pandas import read_csv
    
    
    # НОРМАЛИЗУЕМ ПУТИ
    input_path, output_path = __normalizing_paths(input_path, output_path)
    
    # ПЕРВИЧНАЯ ПРЕДОБРАБОТКА
    data = read_csv(input_path, header=0)
    data["Дата регистрации"] = data["Дата регистрации"].apply(__convert_to_datetime)
    data = data.sort_values(by="Дата регистрации")
    
    assert data["Дата регистрации"].isnull().sum() == 0
    
    data["Год"] = data["Дата регистрации"].dt.year
    data["Месяц"] = data["Дата регистрации"].dt.month_name()
    data["Месяц"] = data["Месяц"].apply(__get_month_name)
    data = data.drop(columns="Дата регистрации")
    
    data["Кем решен (группа)"] = data["Кем решен (группа)"].apply(__transform_group)
    
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
            

def visualizate_reports(input_path: str="./Reports/Data/", output_path: str="./Reports/Charts/"):
    """Визуализирует статистические данные для отчета

    Args:
        input_path (str): путь к папке с отчетами. По стандарту: "./Reports/Data/".
        output_path (str): путь к папке с изображениями. По стандарту: "./Reports/Charts/".
    """
    
    from programs.visualizate import Visualizator
    
    
    input_path, output_path = __normalizing_paths(input_path, output_path, check_is_file=False)
    
    visualizator = Visualizator(input_path=input_path, output_path=output_path)
    visualizator.incidents_and_service_requests()
    visualizator.services()
    visualizator.lifetimes()
    visualizator.dynamic_of_KIAS()
    visualizator.funnel_dynamics()
    visualizator.dynamics_of_closing_orders()


def get_week_report(input_path: str="./Reports/Data/metrics/", output_path: str="./Reports/Weekly/"):
    """Формирует еженедельный отчет по метрикам SLA и CSI

    Args:
        input_path (str): путь к папке с отчетами по метрикам. По стандарту: "./Reports/Data/metrics/".
        output_path (str): путь к папке с таблицами. По стаднарту: "./Reports/Weekly/".
    """
    
    from programs.week import Week_Report
    
    
    input_path, output_path = __normalizing_paths(input_path, output_path, check_is_file=False)
    
    report = Week_Report(input_path=input_path, output_path=output_path)
    report.SLA()
    report.CSI()