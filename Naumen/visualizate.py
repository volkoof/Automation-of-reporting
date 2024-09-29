class Visualizator:
    
    from warnings import filterwarnings
    filterwarnings("ignore")
    
    
    def __init__(self, input_path: str, output_path: str):
        """Иницилизатор класса

        Args:
            input_path (str): путь к папке с отчетами.
            output_path (str): путь к папке с графиками.
        """
        self.input_path = input_path
        self.output_path = output_path
        self.scale = 1.2
        self.text_offset = 1.02
        
        
    def get_number_of_month(self, month_name: str) -> int:
        """Возвращает номер месяца, начиная с нуля

        Args:
            month_name (str): название месяца.

        Returns:
            int: номер месяца.
        """
        
        months_to_numbers = {
            "Январь": 0,
            "Февраль": 1,
            "Март": 2,
            "Апрель": 3,
            "Май": 4,
            "Июнь": 5,
            "Июль": 6,
            "Август": 7,
            "Сентябрь": 8,
            "Октябрь": 9,
            "Ноябрь": 10,
            "Декабрь": 11
        }
        
        return months_to_numbers[month_name]
    
    
    def service(self, dataframe, output_path: str, **kwargs):
        """Вспомогательная функция для визуализации динамики по услугам

        Args:
            dataframe (DataFrame): данные.
            output_path: str: выходной путь.
        """
        
        from matplotlib.pyplot import subplots, ioff, close
        ioff()
        
        
        dataframe = dataframe[dataframe["Год"] > (dataframe["Год"].iat[-1] - 1)]
    
        fig, ax = subplots(figsize=kwargs["figsize"])
        legends = (dataframe["Услуга"]).unique()
        n = len(legends)
        x = range(len(dataframe["Месяц"].unique()))

        for service, color in zip(legends, kwargs["colors"]):
            count = dataframe[dataframe["Услуга"] == service]["Количество"]
            ax.plot(x, count, label=service, color=color)
        
        ax.set_ylim(0, dataframe["Количество"].max() * self.scale)
        ax.set_title(kwargs["title"])
        ax.set_xticks(x, dataframe["Месяц"].unique())
        ax.legend(loc=kwargs["loc"], ncols=n//2)
        fig.savefig(output_path.joinpath(kwargs["name"] + '.' + kwargs["ext"]), format=kwargs["ext"])
        close(fig)
        
        
    def lifetime(self, dataframe, output_path: str, **kwargs):
        """Вспомогательная функция для визуализации времени обращений

        Args:
            dataframe (DataFrame): данные.
            output_path (str): выходной путь.
        """
        
        from matplotlib.pyplot import subplots, ioff, close
        from numpy import zeros
        ioff()
        
        
        last_six_months = dataframe["Месяц"].unique()[-6:]
        dataframe = dataframe[dataframe["Месяц"].isin(last_six_months)]
        dataframe["Месяц"] = dataframe["Месяц"].apply(self.get_number_of_month)
        dataframe["Месяц"] -= dataframe["Месяц"].min()
        
        fig, ax = subplots(figsize=kwargs["figsize"])
        legends = dataframe["Группа времени решения"].unique()
        n = len(legends)
        x = dataframe["Месяц"].unique()
        bottom = zeros(len(x))

        for group, color in zip(legends, kwargs["colors"]):
            temp_data = dataframe[dataframe["Группа времени решения"] == group]
            indexes = temp_data["Месяц"].to_numpy()
            rects = ax.bar(x=temp_data["Месяц"], height=temp_data["Количество"], width=kwargs["width"], label=group, bottom=bottom[indexes], color=color)
            bottom[indexes] += temp_data["Количество"]

        rects = ax.bar(x=x, height=zeros(len(x)), width=kwargs["width"], bottom=bottom)
        ax.bar_label(rects, padding=kwargs["padding"])

        ax.set_ylim(0, max(bottom) * self.scale)
        ax.set_xticks(range(len(x)), last_six_months)
        ax.set_title(kwargs["title"])
        ax.legend(loc=kwargs["loc"], ncols=n)
        fig.savefig(output_path.joinpath(kwargs["name"] + '.' + kwargs["ext"]), format=kwargs["ext"])
        close(fig)
        
        
    def incidents_and_service_requests(
        self,
        file: str = "incidents_and_service_requests.csv",
        figsize: tuple[int]=(12, 6),
        colors: list[str] = ["tab:cyan", "tab:orange", "tab:blue", "tab:red"],
        point: int=0,
        offset: float=0.3,
        width: float=0.25,
        padding: int=3,
        loc: str="upper left",
        name: str="incidents_and_service_requests",
        ext: str="svg"
    ):
        """Визуализирует динамику инцидентов и ЗНО

        Args:
            file (str): входной файл. По стандарту: "incidents_and_service_requests.csv".
            figsize (tuple[int]): Общий размер фигуры. По стандарту: (12, 6).
            colors (list[str]): Цвета столбцов. По стандарту: ["tab:cyan", "tab:orange", "tab:blue", "tab:red"].
            point (int): Начальное положение по оси x. По стандарту: 0.
            offset (float): Смещение по оси x. По стандарту: 0.3.
            width (float): Ширина столбцов. По стандарту: 0.25.
            padding (int): Смещение надписей над столбцами. По стандарту: 3.
            loc (str): Расположение легенды. По стандарту: "upper left".
            name (str): Имя выходного файла. По стандарту: "incidents_and_service_requests".
            ext (str): Расширение выходного файла. По стандарту: "svg".
        """
        
        import pandas as pd
        from matplotlib.pyplot import subplots, ioff, close
        from numpy import arange
        ioff()
        
        
        path = self.input_path.joinpath(file)
        
        try:
            dataframe = pd.read_csv(path, header=0)
            dataframe = dataframe[dataframe["Год"] > (dataframe["Год"].iat[-1] - 2)]
            
            fig, ax = subplots(figsize=figsize)
            legends = (dataframe["Год"].astype(str) + '|' + dataframe["Тип запроса"]).unique()
            n = len(legends)
            x = arange(len(dataframe["Месяц"].unique()))
            
            for request, color in zip(legends, colors[:n]):
                year, type_request = request.split(sep='|')
                count = dataframe[(dataframe["Год"] == int(year)) & (dataframe["Тип запроса"] == type_request)]["Количество"]
                rects = ax.bar(x=x+point, height=count, width=width, label=year+' '+type_request, color=color)
                ax.bar_label(rects, padding=padding)
                point += offset 
                
            ax.set_ylim(0, dataframe["Количество"].max() * self.scale)
            ax.set_title("Динамика инцидентов и ЗНО")
            ax.set_xticks(x, dataframe["Месяц"].unique())
            ax.legend(loc=loc, ncols=n)
            fig.savefig(self.output_path.joinpath(name + '.' + ext), format=ext)
            close(fig)
        except pd.errors.EmptyDataError:
            print(f"Файл '{file}' пустой или не существует")
    
    
    def services(
        self,
        folder: str = "services",
        figsize: tuple[int]=(14, 8),
        colors: list[str] = ["tab:olive", "tab:blue", "tab:green", "tab:red", "tab:gray", "tab:purple"],
        loc: str="upper left",
        names: list[str]=["service_incidents", "service_requests"],
        ext: str="svg"
    ):
        """Визуализирует динамику инцидентов по ТОП-5 услугам

        Args:
            folder (str): Папка с файлами. По стандарту: "services".
            figsize (tuple[int]): Общий размер фигуры. По стандарту: (14, 8).
            colors (list[str]): Цвета столбцов. По стандарту: ["tab:olive", "tab:blue", "tab:green", "tab:red", "tab:gray", "tab:purple"].
            loc (str): Расположение легенды. По стандарту: "upper left".
            names (list[str]): Имена выходных файлов. По стандарту: ["service_incidents", "service_requests"].
            ext (str): Расширение выходного файла. По стандарту: "svg".
        """
        
        import pandas as pd
        
        
        general_path = self.input_path.joinpath(folder)
        
        temp_path = self.output_path.joinpath("services")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        path = general_path.joinpath("service_incidents.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.service(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, loc=loc, name=names[0], ext=ext, title="Динамика инцидентов по ТОП-5 услугам")
        except pd.errors.EmptyDataError:
            print(f"Файл {path.name} пустой или не существует")
        
        path = general_path.joinpath("service_requests.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.service(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, loc=loc, name=names[1], ext=ext, title="Динамика ЗНО по ТОП-5 услугам")
        except pd.errors.EmptyDataError:
            print(f"Файл {path.name} пустой или не существует")
    
    
    def lifetimes(
        self,
        folders: list[str] = ["lifetime_of_line_requests", "lifetime_of_ORM_requests"],
        figsize: tuple[int]=(12, 6),
        colors = ["tab:green", "tab:blue", "tab:orange", "tab:red"],
        width: float=0.25,
        padding: int=3,
        loc: str="upper left",
        names_images: list[str]=["firstLine", "secondLine", "thirdLine", "ORM_UK", "ORM_FAC", "ORM_Regions"],
        ext: str="svg"
    ):
        """Визуализирует динамику времени жизни обращений по линиям

        Args:
            folders (list[str]): Папки с файлами. По стандарту: ["lifetime_of_line_requests", "lifetime_of_ORM_requests"]".
            figsize (tuple[int]): Общий размер фигуры. По стандарту: (12, 6).
            colors (list[str]): Цвета столбцов. По стандарту: ["tab:green", "tab:blue", "tab:orange", "tab:red"].
            width (float): Ширина столбцов. По стандарту: 0.25.
            padding (int): Смещение надписей над столбцами. По стандарту: 3.
            loc (str): Расположение легенды. По стандарту: "upper left".
            names_images (list[str]): Имена выходных изображений. По стандарту: ["firstLine", "secondLine", "thirdLine", "ORM_UK", "ORM_FAC", "ORM_Regions"].
            ext (str): Расширение выходного изображения. По стандарту: "svg".
        """
        
        import pandas as pd
        
        
        general_path = self.input_path.joinpath(folders[0])
        
        temp_path = self.output_path.joinpath("lifetime_of_line_requests")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        path = general_path.joinpath("firstLine.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.lifetime(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, width=width, 
                          padding=padding, loc=loc, name=names_images[0], ext=ext, title="Время жизни на 1 линии")
        except pd.errors.EmptyDataError: 
            print(f"Файл {path.name} пустой или не существует")
        
        path = general_path.joinpath("secondLine.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.lifetime(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, width=width, 
                          padding=padding, loc=loc, name=names_images[1], ext=ext, title="Время жизни на 2 линии")
        except pd.errors.EmptyDataError:
            print(f"Файл {path.name} пустой или не существует")
        
        path = general_path.joinpath("thirdLine.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.lifetime(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, width=width, 
                          padding=padding, loc=loc, name=names_images[2], ext=ext, title="Время жизни на 3 линии")
        except pd.errors.EmptyDataError:
            print(f"Файл {path.name} пустой или не существует")
        
        
        general_path = self.input_path.joinpath(folders[1])
        
        temp_path = self.output_path.joinpath("lifetime_of_ORM_requests")
        if not temp_path.exists():
            temp_path.mkdir(parents=True, exist_ok=True)
        
        path = general_path.joinpath("ORM_UK.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.lifetime(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, width=width, 
                          padding=padding, loc=loc, name=names_images[3], ext=ext, title="Время жизни на 2 ОРМ УК")
        except pd.errors.EmptyDataError:
            print(f"Файл {path.name} пустой или не существует")
        
        path = general_path.joinpath("ORM_FAC.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.lifetime(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, width=width, 
                          padding=padding, loc=loc, name=names_images[4], ext=ext, title="Время жизни на 2 ОРМ ФАЦ")
        except pd.errors.EmptyDataError:
            print(f"Файл {path.name} пустой или не существует")
        
        path = general_path.joinpath("ORM_Regions.csv")
        try:
            dataframe = pd.read_csv(path, header=0)
            self.lifetime(dataframe=dataframe, output_path=temp_path, figsize=figsize, colors=colors, width=width, 
                          padding=padding, loc=loc, name=names_images[5], ext=ext, title="Время жизни на 2 ОРМ Регионы")
        except pd.errors.EmptyDataError:
            print(f"Файл {path.name} пустой или не существует")


    def dynamic_of_KIAS(
        self,
        file: str = "dynamic_of_KIAS.csv",
        figsize: tuple[int]=(14, 8),
        colors: list[str] = ["tab:blue", "tab:orange"],
        point: int=0,
        offset: float=0.3,
        width: float=0.25,
        padding: int=3,
        loc: str="upper left",
        name: str="dynamic_of_KIAS",
        ext: str="svg"
    ):
        """Визуализирует динамику обращений по услуге КИАС

        Args:
            file (str): входной файл. По стандарту: "dynamic_of_KIAS.csv".
            figsize (tuple[int]): Общий размер фигуры. По стандарту: (14, 8).
            colors (list[str]): Цвета столбцов. По стандарту: ["tab:blue", "tab:orange"].
            point (int): Начальное положение по оси x. По стандарту: 0.
            offset (float): Смещение по оси x. По стандарту: 0.3.
            width (float): Ширина столбцов. По стандарту: 0.25.
            padding (int): Смещение надписей над столбцами. По стандарту: 3.
            loc (str): Расположение легенды. По стандарту: "upper left".
            name (str): Имя выходного файла. По стандарту: "dynamic_of_KIAS".
            ext (str): Расширение выходного файла. По стандарту: "svg".
        """
        
        import pandas as pd
        from matplotlib.pyplot import subplots, ioff, close
        from numpy import arange
        from re import search
        ioff()
    

        path = self.input_path.joinpath(file)
        
        try:
            dataframe = pd.read_csv(path, header=0)
        
            dataframe = dataframe[dataframe["Год"] > (dataframe["Год"].iat[-1] - 1)]
        
            fig, ax = subplots(figsize=figsize)
            legends = ["Обращения", "Наряды"]
            n = len(legends)
            x = arange(len(dataframe["Месяц"].unique()))

            for type_request, color in zip(legends, colors):
                count = dataframe[type_request]
                rects = ax.bar(x=x+point, height=count, width=width, label=type_request, color=color)
                ax.bar_label(rects, padding=padding)
                point += offset
            
            y_plot = dataframe["Наряды (%)"].apply(lambda x: search(r"\d+.\d+", x).group()).astype(float) + self.scale * max(dataframe["Обращения"])
            ax.plot(x, y_plot, marker='.')
            
            for x_temp, y_temp, text_temp in zip(x, y_plot, dataframe["Наряды (%)"]):
                ax.text(x=x_temp, y=y_temp*self.text_offset, s=text_temp)
            
            ax.set_ylim(0, max(y_plot) * self.scale)
            ax.set_title("Динамика поступивших обращений и созданных нарядов по услуге КИАС")
            ax.set_xticks(x, dataframe["Месяц"].unique())
            ax.legend(loc=loc, ncols=n)
            fig.savefig(self.output_path.joinpath(name + '.' + ext), format=ext)
            close(fig)
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            print(f"Файл '{file}' пустой или не существует")
    
    
    def funnel_dynamics(
        self,
        file: str = "funnel_dynamics.csv",
        figsize: tuple[int]=(12, 6),
        colors: list[str] = ["tab:blue", "tab:orange", "tab:red"],
        point: int=0,
        offset: float=0.3,
        width: float=0.25,
        padding: int=3,
        loc: str="upper left",
        name: str="funnel_dynamics",
        ext: str="svg"
    ):
        """Визуализирует динамику целевых показателей

        Args:
            file (str): входной файл. По стандарту: "funnel_dynamics.csv".
            figsize (tuple[int]): Общий размер фигуры. По стандарту: (12, 6).
            colors (list[str]): Цвета столбцов. По стандарту: ["tab:blue", "tab:orange", "tab:red"].
            point (int): Начальное положение по оси x. По стандарту: 0.
            offset (float): Смещение по оси x. По стандарту: 0.3.
            width (float): Ширина столбцов. По стандарту: 0.25.
            padding (int): Смещение надписей над столбцами. По стандарту: 3.
            loc (str): Расположение легенды. По стандарту: "upper left".
            name (str): Имя выходного файла. По стандарту: "funnel_dynamics".
            ext (str): Расширение выходного файла. По стандарту: "svg".
        """
        
        import pandas as pd
        from matplotlib.pyplot import subplots, ioff, close
        from numpy import arange
        ioff()
        
        
        path = self.input_path.joinpath(file)
        
        try:
            dataframe = pd.read_csv(path, header=0)
            dataframe = dataframe[dataframe["Год"] > (dataframe["Год"].iat[-1] - 1)]

            fig, ax = subplots(figsize=figsize)
            legends = dataframe["Тип группы"].unique()
            n = len(legends)
            x = arange(len(dataframe["Месяц"].unique()))

            for type_line, color in zip(legends, colors):
                count = dataframe[dataframe["Тип группы"] == type_line]["Количество"]
                rects = ax.bar(x=x+point, height=count, width=width, label=str(type_line)+" линия", color=color)
                ax.bar_label(rects, padding=padding)
                point += offset 
            
            ax.set_ylim(0, dataframe["Количество"].max() * self.scale)
            ax.set_title("Динамика воронки")
            ax.set_xticks(x, dataframe["Месяц"].unique())
            ax.legend(loc=loc, ncols=n)
            fig.savefig(self.output_path.joinpath(name + '.' + ext), format=ext)
            close(fig)
        except pd.errors.EmptyDataError:
            print(f"Файл '{file}' пустой или не существует")
    
    
    def dynamics_of_closing_orders(
        self,
        file: str = "dynamics_of_closing_orders.csv",
        figsize: tuple[int]=(14, 6),
        colors: list[str] = ["tab:orange", "tab:red", "tab:gray", "tab:green", "tab:cyan", "tab:blue", "tab:purple"],
        width: float=0.25,
        padding: int=3,
        loc: str="upper left",
        name: str="dynamics_of_closing_orders",
        ext: str="svg"
    ):
        """Визуализирует динамику закрытия нарядов

        Args:
            file (str): входной файл. По стандарту: "dynamics_of_closing_orders.csv".
            figsize (tuple[int]): Общий размер фигуры. По стандарту: (14, 6).
            colors (list[str]): Цвета столбцов. По стандарту: ["tab:orange", "tab:red", "tab:gray", "tab:green", "tab:cyan", "tab:blue", "tab:purple"].
            width (float): Ширина столбцов. По стандарту: 0.25.
            padding (int): Смещение надписей над столбцами. По стандарту: 3.
            loc (str): Расположение легенды. По стандарту: "upper left".
            name (str): Имя выходного файла. По стандарту: "dynamics_of_closing_orders".
            ext (str): Расширение выходного файла. По стандарту: "svg".
        """
        
        import pandas as pd
        from matplotlib.pyplot import subplots, ioff, close
        from numpy import zeros
        ioff()
        
        
        path = self.input_path.joinpath(file)
        
        try:
            dataframe = pd.read_csv(path, header=0)
            dataframe = dataframe[dataframe["Год"] > (dataframe["Год"].iat[-1] - 1)]

            names = dataframe["Месяц"].unique()
            dataframe["Месяц"] = dataframe["Месяц"].apply(self.get_number_of_month)
            dataframe["Месяц"] -= dataframe["Месяц"].min()

            fig, ax = subplots(figsize=figsize)
            legends = dataframe["Результат работ"].unique()
            n = len(legends)
            x = dataframe["Месяц"].unique()
            bottom = zeros(len(x))

            for result, color in zip(legends, colors):
                temp_data = dataframe[dataframe["Результат работ"] == result]
                indexes = temp_data["Месяц"].to_numpy()
                rects = ax.bar(x=temp_data["Месяц"], height=temp_data["Количество"], width=width, label=result, bottom=bottom[indexes], color=color)
                bottom[indexes] += temp_data["Количество"]

            rects = ax.bar(x=x, height=zeros(len(x)), width=width, bottom=bottom)
            ax.bar_label(rects, padding=padding)

            ax.set_ylim(0, max(bottom) * self.scale)
            ax.set_xticks(range(len(x)), names)
            ax.set_title("Динамика закрытия нарядов (3 линия)")
            ax.legend(loc=loc, ncols=n//3)
            fig.savefig(self.output_path.joinpath(name + '.' + ext), format=ext)
            close(fig)
        except pd.errors.EmptyDataError:
            print(f"Файл '{file}' пустой или не существует")