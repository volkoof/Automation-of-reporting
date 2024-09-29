class Report_generator:
    
    
    def __init__(self, data, output_path: str, year: int, month: str):
        """Инициализатор класса

        Args:
            data (DataFrame): данные.
            output_path (str): путь к папке с отчетами.
            year (int):  год.
            month (str): месяц.
        """
        
        self.data = data
        self.output_path = output_path
        self.year = year
        self.month = month

    
    def get_type_of_duration(self, duration: str) -> str:
        """Определяет группу времени решения

        Args:
            duration (str): длительность обработки обращения.

        Returns:
            str: группа.
        """
        
        parts = duration.split(sep=':')
        parts = map(int, parts)
        seconds = parts.__next__() * 3600 + parts.__next__() * 60 + parts.__next__()
        if seconds <= (60*60):
            return "NBH"
        if seconds <= (24*60*60):
            return "NBD"
        if seconds <= (7*24*60*60):
            return "NBW"
        if seconds <= (30*24*60*60):
            return "NBM"
        return "NBY"
    
    
    def get_type_of_group(self, group: str) -> int:
        """Определяет тип группы

        Args:
            group (str): группа.

        Returns:
            int: тип группы.
        """
        
        if group in ["IT__1-B2B-ФАЦ", "IT__1-СД-ФАЦ"]:
            return 1
        if group in ["IT__2-БП-ФАЦ", "IT__2-ОРМ-Москва", "IT__2-СА-Системное администрирование", "IT__2-ОРМ-Иваново", "IT__2-ИБ-Информационная безопасность"]:
            return 2
        if group in ["IT__3-В2В", "IT__3-В2В-Интеграция", "IT__3-СА-Системное администрирование", "IT__3-Портал/Сайт", "IT__3_КИАС", "IT__3_1С", "IT__L3_MIS/WSS/FN"]:
            if group in ["IT__3-В2В", "IT__3-В2В-Интеграция", "IT__L4_Доктор Байт(Allianz)"]:
                return 4
            return 3
        return -1
    
    
    def type_service(self, service: str) -> str:
        """Определяет тип услуги

        Args:
            service (str): услуга.

        Returns:
            str: тип услуги.
        """
        if service in ["IT__1-B2B-ФАЦ", "IT__1-СД-ФАЦ", "IT__2-БП-ФАЦ", "IT__2-ИБ-Информационная безопасность", "IT__2-ОРМ-Иваново", "IT__2-ОРМ-Москва", 
                       "IT__2-СА-Системное администрирование", "IT__3_1С", "IT__3-В2В", "IT__3-В2В-Интеграция", "IT__3-СА-Системное администрирование", "IT__L3_MIS/WSS/FN", "IT__3-Портал/Сайт"]:
            return "Сводный показатель по централизованным услугам ИТ поддержки"
        if service in ["IT_Датафорт", "IT_Доктор байт", "IT__L4_Доктор Байт(Allianz)"]:
            return "Сводный показатель по децентрализованным услугам ИТ поддержки"
        return "NA"
    
    
    def get_type_of_result(self, result: str) -> str:
        """Определяет тип результата решения запроса

        Args:
            result (str): результат решения

        Returns:
            str: тип результата
        """
        if result in ["Решение предоставлено", "Уточнение не предоставлено"]:
            return "Решен"
        if result == "Требуется доработка JIRA":
            return "Возвращен на доработку"
        return "Отклонен"
        
        
    def save_files(self, dataframe, path: str, is_multiindex: bool):
        """Сохранение файлов

        Args:
            dataframe (DataFrame): данные.
            path (str): путь для сохранения данных.
            is_multiindex (bool): есть ли мультииндексы в данных.
        """
    
        import pandas as pd
        
        
        if is_multiindex:
            dataframe[("Год", '')] = self.year
            dataframe[("Месяц", '')] = self.month
        else:
            dataframe["Год"] = self.year
            dataframe["Месяц"] = self.month
            
        dataframe = dataframe.reindex(columns=list(dataframe)[-2:] + list(dataframe)[:-2])
        
        if path.exists():
            try:
                if is_multiindex:
                    report = pd.read_csv(path, header=[0, 1])
                    report = report.rename(columns={
                        "Unnamed: 0_level_1": '',
                        "Unnamed: 1_level_1": '',
                        "Unnamed: 2_level_1": ''
                    })
                else:
                    report = pd.read_csv(path, header=0)
                col_year, col_month = list(report)[:2]
                if (report[col_year].iat[-1] == self.year) and (report[col_month].iat[-1] == self.month):
                    report = report[(report[col_year] != self.year) | (report[col_month] != self.month)]
                report = pd.concat([report, dataframe], axis=0)
                report.to_csv(path, index=False)
            except:
                dataframe.to_csv(path, index=False)
        else:
            dataframe.to_csv(path, index=False)
    
    
    def lifetime(self, dataframe, groups: list[str], path: str):
        """Вспомогательная функция для рассчета времени жизни обращений

        Args:
            dataframe (DataFrame): данные.
            groups (list[str]): необходимые группы.
            path: str: путь для сохранения файла.
        """
        
        temp_data = dataframe[dataframe["Кем решен (группа)"].isin(groups)]
        temp_data = temp_data.drop(columns="Кем решен (группа)")
        temp_data = temp_data.groupby(by="Группа времени решения").agg({"Группа времени решения": "count"}).rename(columns={"Группа времени решения": "Количество"})\
            .reset_index()
        self.save_files(dataframe=temp_data, path=path, is_multiindex=False)
        

    def incidents_and_service_requests(self, filename: str="incidents_and_service_requests"):
        """Рассчитывает количество инцидентов и ЗНО

        Args:
            filename (str): имя файла. По стандарту: "incidents_and_service_requests".
        """
        
        dataframe = self.data[["Тип запроса"]]
        dataframe = dataframe[dataframe["Тип запроса"].isin(["Запрос на обслуживание", "Инцидент"])]
        
        dataframe = dataframe.groupby(by="Тип запроса").agg({"Тип запроса": "count"})\
            .rename(columns={"Тип запроса": "Количество"}).reset_index()
        
        path = self.output_path.joinpath(filename + ".csv")
        self.save_files(dataframe=dataframe, path=path, is_multiindex=False)
        

    def services(self, filenames: list[str]=["service_incidents", "service_requests"]):
        """Рассчитывает количество инцидентов и ЗНО по ТОП-5 услугам

        Args:
            filenames (list[str]): имена файлов. По стандарту: ["service_incidents", "service_requests"].

        """
        
        temp_path = self.output_path.joinpath("services")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        
        dataframe = self.data[["Услуга", "Тип запроса"]]
        dataframe = dataframe.dropna()
        services = ["КИАС", "В2В", "Массовый инцидент", "Рабочее место", "1С"]
        temp_data = dataframe[dataframe["Тип запроса"] == "Инцидент"]
        temp_data = temp_data.drop(columns="Тип запроса")
        temp_data["Услуга"] = temp_data["Услуга"].apply(lambda x: x if x in services else "Прочее")
        temp_data = temp_data.groupby(by="Услуга").agg({"Услуга": "count"}).rename(columns={"Услуга": "Количество"})\
            .reset_index()
            
        path = temp_path.joinpath(filenames[0] + ".csv")
        self.save_files(dataframe=temp_data, path=path, is_multiindex=False)
        
        services = ["В2В", "Рабочее место", "КИАС", "Ошибка выгрузки чека и/или полиса", "Файловые ресурсы"]
        temp_data = dataframe[dataframe["Тип запроса"] == "Запрос на обслуживание"]
        temp_data = temp_data.drop(columns="Тип запроса")
        temp_data["Услуга"] = temp_data["Услуга"].apply(lambda x: x if x in services else "Прочее")
        temp_data = temp_data.groupby(by="Услуга").agg({"Услуга": "count"}).rename(columns={"Услуга": "Количество"})\
            .reset_index()
            
        path = temp_path.joinpath(filenames[1] + ".csv")
        self.save_files(dataframe=temp_data, path=path, is_multiindex=False)
        

    def lifetimes(self, filenames: list[str]=["firstLine", "secondLine", "thirdLine", "ORM_UK", "ORM_FAC", "ORM_Regions"]):
        """Рассчитывает время жизни обращений по линиям и ОРМ

        Args:
            filenames (list[str]): имена файлов. По стандарту: ["firstLine", "secondLine", "thirdLine", "ORM_UK", "ORM_FAC", "ORM_Regions"].
            
        """
        
        dataframe = self.data[["Системный статус", "Кем решен (группа)", "Фактическая длительность выполнения запроса (SLA)"]]
        dataframe = dataframe.dropna()
        dataframe = dataframe[dataframe["Системный статус"] == "Закрыт"]
        dataframe = dataframe.drop(columns="Системный статус")
        dataframe["Группа времени решения"] = dataframe["Фактическая длительность выполнения запроса (SLA)"].apply(self.get_type_of_duration)
        dataframe = dataframe.drop(columns="Фактическая длительность выполнения запроса (SLA)")
        
        temp_path = self.output_path.joinpath("lifetime_of_line_requests")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        groups = ["IT__1-СД-ФАЦ", "IT__1-B2B-ФАЦ"]
        path = temp_path.joinpath(filenames[0] + ".csv")
        self.lifetime(dataframe=dataframe, groups=groups, path=path)
        
        groups = ["IT__2-БП-ФАЦ", "IT__2-ИБ-Информационная безопасность", "IT__2-СА-Системное администрирование"]
        path = temp_path.joinpath(filenames[1] + ".csv")
        self.lifetime(dataframe=dataframe, groups=groups, path=path)
        
        groups = ["IT__3_1С", "IT__3-В2В", "IT__3-В2В-Интеграция", "IT__3-СА-Системное администрирование", "IT__3-Портал/Сайт", "IT__3_КИАС"]
        path = temp_path.joinpath(filenames[2] + ".csv")
        self.lifetime(dataframe=dataframe, groups=groups, path=path)
            
        
        temp_path = self.output_path.joinpath("lifetime_of_ORM_requests")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        groups = ["IT__2-ОРМ-Москва"]
        path = temp_path.joinpath(filenames[3] + ".csv")
        self.lifetime(dataframe=dataframe, groups=groups, path=path)
        
        groups = ["IT__2-ОРМ-Иваново"]
        path = temp_path.joinpath(filenames[4] + ".csv")
        self.lifetime(dataframe=dataframe, groups=groups, path=path)
        
        groups = ["IT__Датафорт", "IT__Доктор байт", "IT__L4_Доктор Байт(Allianz)"]
        path = temp_path.joinpath(filenames[5] + ".csv")
        self.lifetime(dataframe=dataframe, groups=groups, path=path)
    
    
    def metrics(self, filenames: list[str]=["SLA", "SLA_General", "CSI", "CSI_General"]):
        """Рассчитывает статистические показатели SLA и CSI

        Args:
            filenames (list[str]): имена файлов. По стандарту: ["SLA", "SLA_General", "CSI", "CSI_General"].
        """
        
        from re import search
        
        
        temp_path = self.output_path.joinpath("metrics")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        dataframe = self.data[["Кем решен (группа)", "Процент использования SLA"]]
        dataframe = dataframe.dropna()
        dataframe["SLA"] = dataframe["Процент использования SLA"].apply(lambda x: 100 if x != "Просрочен" else 0)
        dataframe = dataframe.drop(columns="Процент использования SLA")
        dataframe = dataframe.groupby(by="Кем решен (группа)").agg({"SLA": ["mean", lambda x: (x == 100).sum(), lambda x: (x == 0).sum()]})\
            .reset_index().rename(columns={"mean": "Процент", "<lambda_0>": "Соблюден", "<lambda_1>": "Нарушен"})
        dataframe[("SLA", "Процент")] = dataframe[("SLA", "Процент")].round(2).apply(str) + '%'
        
        path = temp_path.joinpath(filenames[0] + ".csv")
        self.save_files(dataframe=dataframe, path=path, is_multiindex=True)
        
        
        path = temp_path.joinpath(filenames[1] + ".csv")
        dataframe[("Показатель", '')] = dataframe[("Кем решен (группа)", '')].apply(self.type_service)
        dataframe = dataframe.drop(columns=("Кем решен (группа)", ''))
        dataframe = dataframe[dataframe[('Показатель', '')] != "NA"]
        dataframe[("SLA", "Процент")] = dataframe[("SLA", "Процент")].apply(lambda x: search(r"\d+.\d+", x).group()).astype(float)
        dataframe = dataframe.groupby(by="Показатель").agg({("SLA", "Процент"): "mean"}).reset_index()
        dataframe[("SLA", "Процент")] = dataframe[("SLA", "Процент")].round(2).astype(str) + '%'
        self.save_files(dataframe=dataframe, path=path, is_multiindex=True)
        
        
        dataframe = self.data[["Кем решен (группа)", "Качество проведения работ по Запросу (оценка пользователя)"]]
        dataframe = dataframe.dropna()
        dataframe = dataframe.groupby(by="Кем решен (группа)").agg({"Качество проведения работ по Запросу (оценка пользователя)": 
            ["sum", "count", lambda x: (x > 0).sum()]}).reset_index()\
                .rename(columns={"Качество проведения работ по Запросу (оценка пользователя)": "CSI", "sum": "Средняя", "count": "Всего", "<lambda_0>": "Оценки (шт.)"})
        dataframe[("CSI", "Средняя")] = (dataframe[("CSI", "Средняя")] / dataframe[("CSI", "Оценки (шт.)")]).round(2)
        dataframe[("CSI", "Процент оценок")] = ((100 * dataframe[("CSI", "Оценки (шт.)")] / dataframe[("CSI", "Всего")]).round(2)).astype(str) + '%'
    
        path = temp_path.joinpath(filenames[2] + ".csv")
        self.save_files(dataframe=dataframe, path=path, is_multiindex=True)
        
        
        path = temp_path.joinpath(filenames[3] + ".csv")
        dataframe[("Показатель", '')] = dataframe[("Кем решен (группа)", '')].apply(self.type_service)
        dataframe = dataframe.drop(columns=("Кем решен (группа)", ''))
        dataframe = dataframe[dataframe[('Показатель', '')] != "NA"]
        dataframe = dataframe.groupby(by="Показатель").agg({("CSI", "Средняя"): "mean"}).reset_index()
        dataframe[("CSI", "Средняя")] = dataframe[("CSI", "Средняя")].round(2)
        self.save_files(dataframe=dataframe, path=path, is_multiindex=True)
        
    
    def funnel_targets(self, filename: str="funnel_targets"):
        """Рассчитывает целевые показатели воронки

        Args:
            filename (str): имя файла. По стандарту: "funnel_targets".
        """
        
        dataframe = self.data[["Услуга", "Кем решен (группа)"]]
        dataframe = dataframe.dropna()
        dataframe["Тип группы"] = dataframe["Кем решен (группа)"].apply(self.get_type_of_group)
        dataframe = dataframe.drop(columns="Кем решен (группа)")
        dataframe = dataframe[dataframe["Тип группы"] != -1]
        
        temp_data = dataframe.groupby(by="Услуга").agg({"Тип группы": [lambda x: (x == 1).sum(), lambda x: (x == 2).sum(), 
                                                     lambda x: ((x == 3) | (x == 4)).sum(), "count", 
                                                     lambda x: (x == 4).sum()]}).reset_index()\
                                                         .rename(columns={"<lambda_0>": "Первый (шт.)", "<lambda_1>": "Второй (шт.)",
                                                                          "<lambda_2>": "Третий (шт.)", "count": "Общий итог (шт.)",
                                                                          "<lambda_3>": "Jira (шт.)"})

        temp_data[("Тип группы", "Первый (%)")] = (100 * temp_data[("Тип группы", "Первый (шт.)")] / temp_data[("Тип группы", "Общий итог (шт.)")]).round(2).apply(str) + '%'
        temp_data[("Тип группы", "Второй (%)")] = (100 * temp_data[("Тип группы", "Второй (шт.)")] / temp_data[("Тип группы", "Общий итог (шт.)")]).round(2).apply(str) + '%'
        temp_data[("Тип группы", "Третий (%)")] = (100 * temp_data[("Тип группы", "Третий (шт.)")] / temp_data[("Тип группы", "Общий итог (шт.)")]).round(2).apply(str) + '%'
        temp_data[("Тип группы", "Jira (%)")] = (100 * temp_data[("Тип группы", "Jira (шт.)")] / temp_data[("Тип группы", "Общий итог (шт.)")]).round(2).apply(str) + '%'
        
        temp_data = temp_data.reindex(columns=[("Услуга", ''), ("Тип группы", "Первый (шт.)"), ("Тип группы", "Первый (%)"),("Тип группы", "Второй (шт.)"), 
                                       ("Тип группы", "Второй (%)"), ("Тип группы", "Третий (шт.)"), ("Тип группы", "Третий (%)"),
                                       ("Тип группы", "Общий итог (шт.)"), ("Тип группы", "Jira (шт.)"),
                                       ("Тип группы", "Jira (%)")])
        
        path = self.output_path.joinpath(filename + ".csv")
        temp_data.to_csv(path, index=False)
    
    
    def dynamic_of_KIAS(self, filename: str="dynamic_of_KIAS"):
        """Рассчитывает динамику поступивших обращений по услуге КИАС

        Args:
            filename (str): имя файла. По стандарту: "dynamic_of_KIAS".
        """
        
        from pandas import DataFrame
        
        
        dataframe = self.data[["Услуга", "Кем решен (группа)"]]
        dataframe = dataframe.dropna()
        dataframe = dataframe[dataframe["Услуга"] == "КИАС"]
        dataframe = dataframe.drop(columns="Услуга")
        dataframe["Тип группы"] = dataframe["Кем решен (группа)"].apply(self.get_type_of_group)
        dataframe = dataframe.drop(columns="Кем решен (группа)")
    
        temp_data = DataFrame({
            "Обращения": [dataframe[dataframe["Тип группы"] < 3].count().item()],
            "Наряды": [dataframe[dataframe["Тип группы"] >= 3].count().item()]
        })
        temp_data["Наряды (%)"] = (100 * temp_data["Наряды"] / temp_data["Обращения"]).round(2).apply(str) + '%'
        
        path = self.output_path.joinpath(filename + ".csv")
        self.save_files(dataframe=temp_data, path=path, is_multiindex=False)
    
    
    def funnel_dynamics(self, filename: str="funnel_dynamics"):
        """Рассчитывает динамику воронки

        Args:
            filename (str): имя файла. По стандарту: "funnel_dynamics".
        """

        dataframe = self.data[["Кем решен (группа)", "Системный статус"]]
        dataframe = dataframe.dropna()
        dataframe = dataframe[dataframe["Системный статус"] == "Закрыт"]
        dataframe["Тип группы"] = dataframe["Кем решен (группа)"].apply(self.get_type_of_group)
        dataframe = dataframe.drop(columns=["Системный статус", "Кем решен (группа)"])
        dataframe = dataframe[dataframe["Тип группы"] != -1]
        dataframe["Тип группы"] = dataframe["Тип группы"].apply(lambda x: 3 if x == 4 else x)
        
        dataframe = dataframe.groupby(by=["Тип группы"]).agg({"Тип группы": "count"})\
            .rename(columns={"Тип группы": "Количество"}).reset_index()
        
        path = self.output_path.joinpath(filename + ".csv")
        self.save_files(dataframe=dataframe, path=path, is_multiindex=False)
    
    
    def dynamics_of_closing_orders(self, filename: str="dynamics_of_closing_orders"):
        """Рассчитывает динамику закрытия нарядов

        Args:
            filename (str): имя файла. По стандарту: "dynamics_of_closing_orders".
        """
        
        dataframe = self.data[["Кем решен (группа)", "Результат работ"]]
        dataframe = dataframe.dropna()
        dataframe["Тип группы"] = dataframe["Кем решен (группа)"].apply(self.get_type_of_group)
        dataframe = dataframe.drop(columns="Кем решен (группа)")
        dataframe = dataframe[dataframe["Тип группы"].isin([3, 4])]
        dataframe = dataframe.drop(columns="Тип группы")
        
        dataframe = dataframe.groupby(by=["Результат работ"]).agg({"Результат работ": "count"}).rename(columns={"Результат работ": "Количество"})\
            .reset_index()
        
        path = self.output_path.joinpath(filename + ".csv")
        self.save_files(dataframe=dataframe, path=path, is_multiindex=False)