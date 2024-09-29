class Week_Report:
    
    from warnings import filterwarnings
    filterwarnings("ignore")
    
    
    def __init__(self, input_path: str, output_path: str):
        """Иницилизатор класса

        Args:
            input_path (str): путь к папке с отчетами по метрикам.
            output_path (str): путь к папке с результатами.
        """
        self.input_path = input_path
        self.output_path = output_path
        self.groups = [
            "IT__1-B2B-ФАЦ",
            "IT__1-СД-ФАЦ",
            "IT__2-БП-ФАЦ",
            "IT__2-ИБ-Информационная безопасность",
            "IT__2-ОРМ-Иваново",
            "IT__2-ОРМ-Москва",
            "IT__2-СА-Системное администрирование",
            "IT__3-СА-Системное администрирование",
            "IT__3-В2В",
            "IT__3-В2В-Интеграция",
            "IT__3_1С",
            "IT__L3_MIS/WSS/FN",
            "IT__3-Портал/Сайт",
            "IT__3_КИАС"
        ]


    def SLA(self, input_file: str="SLA.csv", output_file: str="SLA.csv"):
        """Формирует показатели по SLA

        Args:
            input_file (str): входной файл. По стандарту: "SLA.csv".
            output_file (str): выходной файл. По стандарту: "SLA.csv".
        """
        
        from pandas import read_csv, merge, notna, DataFrame
        
        
        path = self.input_path.joinpath(input_file)
        
        data = read_csv(path, header=[0, 1])
        data = data.rename(columns={
            "Unnamed: 0_level_1": '',
            "Unnamed: 1_level_1": '',
            "Unnamed: 2_level_1": ''
        })
        
        result = DataFrame({("Кем решен (группа)", ''): self.groups})
        data = data[data["Кем решен (группа)"].isin(self.groups)]

        prev_month, current_month = data["Месяц"].unique()[-2:]
        data = data[(data["Месяц"] == prev_month) | (data["Месяц"] == current_month)]
        
        table1 = data[data["Месяц"] == prev_month][["Кем решен (группа)", "SLA"]].drop(columns=[("SLA", "Соблюден"), ("SLA", "Нарушен")])
        table1 = table1.rename(columns={"SLA": prev_month, "Процент": ''})
        result = merge(left=result, right=table1, on="Кем решен (группа)", how="left")

        table2 = data[data["Месяц"] == current_month][["Кем решен (группа)", "SLA"]]
        result = merge(left=result, right=table2, on="Кем решен (группа)", how="left")

        result = result.rename(columns={"Кем решен (группа)": "Группа", "SLA": current_month, "Процент": "SLA"})
        
        result[(prev_month, '')] = result[(prev_month, '')].apply(lambda x: x if notna(x) else '-')
        result[(current_month, "SLA")] = result[(current_month, "SLA")].apply(lambda x: x if notna(x) else '-')
        result[(current_month, "Соблюден")] = result[(current_month, "Соблюден")].apply(lambda x: int(x) if notna(x) else '-')
        result[(current_month, "Нарушен")] = result[(current_month, "Нарушен")].apply(lambda x: int(x) if notna(x) else '-')
        
        result.to_csv(self.output_path.joinpath(output_file), index=False)
    
    
    def CSI(self, input_file: str="CSI.csv", output_file: str="CSI.csv"):
        """Формирует показатели по CSI

        Args:
            input_file (str): входной файл. По стандарту: "CSI.csv".
            output_file (str): выходной файл. По стандарту: "CSI.csv".
        """
        
        from pandas import read_csv, merge, notna, DataFrame
        
        
        path = self.input_path.joinpath(input_file)
        
        data = read_csv(path, header=[0, 1])
        data = data.rename(columns={
            "Unnamed: 0_level_1": '',
            "Unnamed: 1_level_1": '', 
            "Unnamed: 2_level_1": ''
        })

        result = DataFrame({("Кем решен (группа)", ''): self.groups})
        data = data[data["Кем решен (группа)"].isin(self.groups)]
        
        prev_month, current_month = data["Месяц"].unique()[-2:]
        data = data[(data["Месяц"] == prev_month) | (data["Месяц"] == current_month)]
        
        table1 = data[data["Месяц"] == prev_month][["Кем решен (группа)", "CSI"]].drop(columns=[("CSI", "Всего"), ("CSI", "Оценки (шт.)"), ("CSI", "Процент оценок")])
        table1 = table1.rename(columns={"CSI": prev_month, "Средняя": ''})
        result = merge(left=result, right=table1, on="Кем решен (группа)", how="left")
        
        table2 = data[data["Месяц"] == current_month][["Кем решен (группа)", "CSI"]]
        result = merge(left=result, right=table2, on="Кем решен (группа)", how="left")
        
        result = result.rename(columns={"Кем решен (группа)": "Группа", "CSI": current_month})
        
        result[(prev_month, '')] = result[(prev_month, '')].apply(lambda x: x if notna(x) else '-')
        result[(current_month, "Средняя")] = result[(current_month, "Средняя")].apply(lambda x: x if notna(x) else '-')
        result[(current_month, "Всего")] = result[(current_month, "Всего")].apply(lambda x: int(x) if notna(x) else '-')
        result[(current_month, "Оценки (шт.)")] = result[(current_month, "Оценки (шт.)")].apply(lambda x: int(x) if notna(x) else '-')
        result[(current_month, "Процент оценок")] = result[(current_month, "Процент оценок")].apply(lambda x: x if notna(x) else '-')
        
        result.to_csv(self.output_path.joinpath(output_file), index=False)