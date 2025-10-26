import pandas as pd
from config import ECOCROP_PATH

class EcoCropService:
    """Сервис для работы с базой FAO EcoCrop."""
    
    DELETE_COLUMNS = {"AUTH", "FAMNAME"}

    def __init__(self):
        # Читаем CSV
        try:
            self.df = pd.read_csv(ECOCROP_PATH, encoding="Windows-1252")
        except FileNotFoundError:
            raise RuntimeError(f"EcoCrop CSV not found at {ECOCROP_PATH}")        # Приводим все названия к нижнему регистру для ускоренного поиска
        self.df["ScientificName"] = self.df["ScientificName"].astype(str).str.lower()
        self.df["COMNAME"] = self.df["COMNAME"].astype(str).str.lower()
        
        # Заменяем NaN на None, чтобы JSON мог сериализовать
        self.df = self.df.where(pd.notnull(self.df), None)


    def get_crop(self, name: str) -> dict | None:
        """Ищет культуру по научному названию (ScientificName)."""
        if not name:
            return None
        name = name.lower().strip()
        
        crop = self.df[self.df["ScientificName"].str.contains(name, na=False)]
        if crop.empty:
            crop = self.df[self.df["COMNAME"].str.contains(name, na=False)]
            if crop.empty:
                return None
        # Преобразуем строку в словарь без NaN
        data = crop.iloc[0].to_dict()
        import pprint
        pprint.pprint(data)

        # Убираем NaN вручную на случай, если где-то остались
        clean_data = {
            k: (None if pd.isna(v) else v)
            for k, v in data.items()
            if k not in self.DELETE_COLUMNS
        }

        return clean_data
        
        """ # No need
        EcoPortCode - номмер записи в базе EcoCrop
        AUTH - Автор

        FAMNAME - таксономическое семейство
          
        # Морфология и жизненный цикл
        LIFO - Форма роста (дерево, куст, трава и т.д.)
        HABI - Характер роста (прямостоячий, вьющийся и т.п.)
        LISPA - Жизненный цикл (однолетник, многолетник и т.д.)
        PHYS - Физические характеристики (вечнозелёный, одиночный стебель)


        """

        """ # Need
        ScientificName - Научное название
        SYNO - Synonyms, синонимы научного названия
        COMNAME - Common Name, народное название
        
        # Использование и выращивание
        CAT - Категория культуры
        PLAT - Маштаб выращивания
        PROSY - Сферы применения
        GMIN / GMAX - Продолжительность вегетационного периода

        
        # экологические требования
        🌡️ Температура
        - TOPMN / TOPMX — Оптимальная температура роста (минимум / максимум)
        - TMIN / TMAX — Абсолютный температурный диапазон, при котором культура может выживать
        - KTMPR / KTMP — Критическая минимальная температура, ниже которой растение погибает (репродуктивная / вегетативная)

        🌧️ Осадки
        - ROPMN / ROPMX — Оптимальное количество осадков в год (мм)
        - RMIN / RMAX — Допустимый диапазон осадков (мм)

        🧪 pH почвы
        - PHOPMN / PHOPMX — Оптимальный диапазон pH почвы
        - PHMIN / PHMAX — Допустимый диапазон pH почвы

        🌍 География
        - LATOPMN / LATOPMX — Оптимальная широта (минимум / максимум)
        - LATMN / LATMX — Абсолютный диапазон широты
        - ALTMX — Максимальная высота над уровнем моря (м)

        ☀️ Свет
        - LIOPMN / LIOPMX — Оптимальный уровень освещённости
        - LIMN / LIMX — Допустимый диапазон освещённости

        🧱 Почва
        - DEP / DEPR — Оптимальная / допустимая глубина почвы
        - TEXT / TEXTR — Оптимальная / допустимая текстура почвы (например, лёгкая, средняя, тяжёлая)
        - FER / FERR — Требования к плодородию почвы (высокие / умеренные)
        - SAL / SALR — Устойчивость к солёности почвы (например, низкая <4 dS/m)
        - DRA / DRAR — Требования к дренажу и переносимость засухи

        ☠️ Токсичность
        - TOX / TOXR — Устойчивость к токсичным условиям (если указано)

        📸 Фотопериод
        - PHOTO — Требуемая длина дня: короткий (<12 ч), нейтральный (12–14 ч), длинный (>14 ч)

        🌦️ Климат
        - CLIZ — Климатические зоны по классификации Кёппена (например, Aw — тропический влажный и сухой)

        🧬 Адаптация
        - ABITOL — Толерантность к абиотическим стрессам (если указано)
        - ABISUS — Основной абиотический фактор, влияющий на культуру (например, влажность)
        - INTRI — История интродукции (если указано)

        🧑‍🌾 Использование
        - PROSY — Сферы применения: домашние сады, коммерческое выращивание и т.д.
        - GMIN / GMAX — Продолжительность вегетационного периода (в днях)
        """



# Создаём один экземпляр, чтобы не читать CSV каждый раз
ecocrop_service = EcoCropService()


def get_crop(name: str):
    """Фасад для вызова из FastAPI."""
    return ecocrop_service.get_crop(name)


