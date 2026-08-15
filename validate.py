import os
import json
import pandas as pd
import utils

class Validator:
    def __init__(self):
        self.script_path = os.path.dirname(os.path.realpath(__file__))
        self.log = utils.get_logger("validador_xml")

    def validate_dict_xml(self, data: dict):
        path_setting = os.path.join(
            self.script_path,
            "config",
            "settings_xml.json"
        )

        with open(path_setting, "r", encoding="utf-8") as f:
            config = json.load(f)

        result = self._validate_recursive(data=data, schema=config, path="" )
        return result


    def _validate_recursive(self, data, schema, path):
        """
        Percorre recursivamente o dicionário comparando com o schema.
        """
        try:
            for key, expected in schema.items():
                current_path = f"{path}.{key}" if path else key

                # Campo obrigatório
                if key not in data:
                    raise ValueError(
                        f"Campo obrigatório ausente: {current_path}"
)

                value = data[key]

                # -------------------------
                # DICIONÁRIO
                # -------------------------

                if isinstance(expected, dict):

                    if not isinstance(value, dict):
                        raise ValueError(
                            f"{current_path} deveria ser um dicionário."
                        )

                    self._validate_recursive(
                        value,
                        expected,
                        current_path
                    )

                # -------------------------
                # LISTA
                # -------------------------

                elif isinstance(expected, list):

                    if not isinstance(value, list):
                        raise ValueError(
                            f"{current_path} deveria ser uma lista."
                        )

                    item_schema = expected[0]

                    for index, item in enumerate(value):

                        self._validate_recursive(
                            item,
                            item_schema,
                            f"{current_path}[{index}]"
                        )

                # -------------------------
                # TIPO
                # -------------------------

                else:

                    validator = getattr(
                        self,
                        f"_validate_{expected}",
                        None
                    )

                    if validator is None:
                        raise ValueError(
                            f"Validador '{expected}' não encontrado."
                        )

                    validator(value, current_path)
        except ValueError as e:
            self.log.error(e)
            return False

        return True


    def _validate_str(self, value, path):
        if not isinstance(value, str):
            raise ValueError(
                f"{path} deveria ser string."
            )


    def _validate_int(self, value, path):
        try:
            int(value)
        except Exception:
            raise ValueError(
                f"{path} deveria ser inteiro."
            )


    def _validate_float(self, value, path):
        try:
            float(value)
        except Exception:
            raise ValueError(
                f"{path} deveria ser float."
            )


    def _validate_cnpj(self, value, path):
        # futuramente valida CNPJ
        self._validate_str(value, path)


    def _validate_date(self, value, path):
        # futuramente datetime.strptime(...)
        self._validate_str(value, path)

    def data_frame_validator(self, data_frame):
        """ Transforma os dados Dataframe para se adequar as regras de negocio"""
        path_setting = os.path.join(self.script_path, "config/schema_pandas.json")

        with open(path_setting, "r", encoding="utf-8") as f:
            schema: dict = json.load(f)

        valid_mask = pd.Series(True, index=data_frame.index)

        for column, column_rules in schema.items():
            if column not in data_frame.columns:
                raise ValueError(f"Column '{column}' not found in Dataframe")

            if column_rules["type"] == "str":
                data_frame[column] = data_frame[column].astype("string")

            elif column_rules["type"] in ("int", "float"):
                data_frame[column] = pd.to_numeric(data_frame[column], errors="coerce")


            elif column_rules["type"] == "datetime":
                data_frame[column] = pd.to_datetime(data_frame[column], errors="coerce", dayfirst=True)

            if not column_rules["nullable"]:
                valid_mask &= ~data_frame[column].isnull()

        return data_frame[valid_mask], data_frame[~valid_mask]