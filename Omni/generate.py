class Report_generator:
    
    def __init__(self, data, output_path: str, year: int, month: str):
        """Инициализатор класса

        Args:
            data (DataFrame): исходный набор данных.
            output_path (str): путь к папке с отчетами.
            year (int):  год.
            month (str): месяц.
        """
        
        self.data = data
        self.output_path = output_path
        self.year = year
        self.month = month


    def save_files(self, dataframe, path: str):
        """Сохранение файлов

        Args:
            dataframe (DataFrame): данные.
            path (str): путь для сохранения данных.
        """
        
        import pandas as pd
        
        
        dataframe["Год"] = self.year
        dataframe["Месяц"] = self.month
        dataframe = dataframe.reindex(columns=list(dataframe)[-2:] + list(dataframe)[:-2])
        
        if path.exists():
            try:
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
    

    def helper_function(self, dataframe, types_of_groups: list[int], path: str):
        """Вспомогательная функция для генерации данных

        Args:
            dataframe (DataFrame): данные.
            types_of_groups (list[int]): учитываемые типы групп.
            path: str: путь для сохранения файла.
        """
        
        from pandas import merge
        
        
        dataframe = dataframe[dataframe["Тип группы"].isin(types_of_groups)]
        
        dataframe1 = dataframe.groupby(by="Тип группы").agg({"Тип группы": "count"}).rename(columns={"Тип группы": "Общее количество"}).reset_index()
        dataframe2 = dataframe[dataframe["Статус"] == "Закрыто"].groupby(by="Тип группы").agg({"Тип группы": "count"}).rename(columns={"Тип группы": "Кол-во закрытых заявок"}).reset_index()
        result = merge(left=dataframe1, right=dataframe2, on="Тип группы", how="left").fillna(value=0)
        result["% закрытых заявок"] = (100 * result["Кол-во закрытых заявок"] / result["Общее количество"]).round(2).apply(str) + '%'
        result["Кол-во закрытых заявок"] = result["Кол-во закрытых заявок"].astype(int)
        self.save_files(dataframe=result, path=path)
    

    def first_list(self, filenames: str=["table_1", "table_2"]):
        """Генериует данные для 1-го листа

        Args:
            filename (list[str]): имена файлов. По стандарту: ["table_1", "table_2"].
        """
        
        from pandas import merge
        
        
        temp_path = self.output_path.joinpath("list_1")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        path = temp_path.joinpath(filenames[0] + ".csv")
        
        dataframe = self.data[["Тип группы", "Статус"]]
        dataframe = dataframe.dropna()
        dataframe = dataframe.groupby(by=["Тип группы", "Статус"]).agg({"Статус": "count"}).rename(columns={"Статус": "Общее Количество"}).reset_index()
        dataframe.to_csv(path, index=False)
        
        path = temp_path.joinpath(filenames[1] + ".csv")
        
        dataframe1 = dataframe.groupby(by="Тип группы").agg({"Общее Количество": "sum"}).reset_index()
        dataframe2 = dataframe[dataframe["Статус"] == "Закрыто"][["Тип группы", "Общее Количество"]].rename(columns={"Общее Количество": "Кол-во закрытых заявок"})
        result = merge(left=dataframe1, right=dataframe2, on="Тип группы", how="left").fillna(value=0)
        result["% закрытых заявок"] = (100 * result["Кол-во закрытых заявок"] / result["Общее Количество"]).round(2).apply(str) + '%'
        result.to_csv(path, index=False)


    def second_list(self, filename: str="list_2"):
        """Генерирует данные для 2-го листа

        Args:
            filename (str): имя файла. По стандарту: "list_2".
        """
        
        path = self.output_path.joinpath(filename + ".csv")
        
        dataframe = self.data[["Тип группы", "Тип_запроса"]]
        dataframe = dataframe[dataframe["Тип группы"] == 1]
        dataframe = dataframe.drop(columns=["Тип группы"])
        dataframe = dataframe.dropna()
        dataframe = dataframe.groupby(by="Тип_запроса").agg({"Тип_запроса": "count"}).rename(columns={"Тип_запроса": "Количество"}).reset_index()
        self.save_files(dataframe=dataframe, path=path)


    def third_list(self, filenames: list[str]=["list_3", "list_4"]):
        """Генерирует данные для 3-го и 4-го листа

        Args:
            filenames (list[str]): имена файлов. По стандарту: "["list_3", "list_4"]".
        """
        
        dataframe = self.data[["Тип группы", "Статус"]]
        
        path = self.output_path.joinpath(filenames[0] + ".csv")
        self.helper_function(dataframe=dataframe, types_of_groups=[1, 2], path=path)
    
        path = self.output_path.joinpath(filenames[1] + ".csv")
        self.helper_function(dataframe=dataframe, types_of_groups=[1, 2, 3], path=path)