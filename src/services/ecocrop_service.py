import pandas as pd
from config import ECOCROP_PATH

class EcoCropService:
    def __init__(self):
        self.df = pd.read_csv(ECOCROP_PATH, encoding="Windows-1252")
        self.df = self.df.apply(lambda c: c.fillna("") if c.dtype == "object" else c)

    def get_crop(self, name: str):
        crop = self.df[self.df["ScientificName"].str.contains(name, case=False, na=False)]
        return crop.iloc[0].to_dict() if not crop.empty else None
