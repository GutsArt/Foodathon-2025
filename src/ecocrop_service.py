import pandas as pd

class EcoCropService:
    def __init__(self, path: str):
        # Загружаем CSV в DataFrame
        self.df = pd.read_csv(path, encoding='windows-1252')
        self.df.columns = self.df.columns.str.strip()  # очищаем названия столбцов
        self.df.fillna("", inplace=True)

    def find_crop(self, name: str):
        """Найти культуру по научному или общему названию"""
        crop = self.df[
            (self.df["ScientificName"].str.lower() == name.lower()) |
            (self.df["COMNAME"].str.lower().str.contains(name.lower(), na=False))
        ]
        return crop if not crop.empty else None

    def get_growth_params(self, name: str):
        """Получить диапазоны температуры и осадков"""
        crop = self.find_crop(name)
        if crop is None:
            return None

        record = crop.iloc[0]
        return {
            "TMIN": record.get("TMIN", None),
            "TMAX": record.get("TMAX", None),
            "ROPMN": record.get("ROPMN", None),
            "ROPMX": record.get("ROPMX", None),
        }
