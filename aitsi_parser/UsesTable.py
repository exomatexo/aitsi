from typing import List

import pandas as pd


class UsesTable:

    def __init__(self, table: pd.DataFrame = None) -> None:
        if table is None:
            table = pd.DataFrame()
        self.table: pd.DataFrame = table

    def set_uses(self, var_name: str, stmt: int) -> None:
        if var_name not in self.table.index[:]:
            indexes: List[str] = list(self.table.index[:])
            indexes.append(var_name)
            self.table = self.table.reindex(indexes)
            self.table = self.table.sort_index(axis=0)
        if stmt not in self.table.columns.values:
            self.table[stmt] = pd.Series(1, index=[var_name])
            self.table = self.table.sort_index(axis=1)
            self.table = self.table.fillna(value=0)
        else:
            self.table[stmt][var_name] = 1

    def get_used(self, stmt: int) -> List[str]:
        results: List[str] = []
        if stmt not in self.table.columns.values:
            return results
        for i in range(len(self.table[stmt])):
            if self.table[stmt][i] == 1:
                results.append(self.table[stmt].index[i])
        return results

    def get_uses(self, var_name: str) -> List[int]:
        results: List[int] = []
        if var_name not in self.table.index[:]:
            return results
        for col in self.table.loc[var_name].index[:]:
            if self.table.loc[var_name][col] == 1:
                results.append(col)
        return results

    def is_used(self, var_name: str, stmt: int) -> bool:
        if stmt not in self.table.columns.values or var_name not in self.table.index[:]:
            return False
        return self.table.at[var_name, stmt] == 1

    def to_string(self) -> None:
        print("UsesTable:")
        print(self.table.to_string())
