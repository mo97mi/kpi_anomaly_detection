import pandas as pd
from shared.to_date import to_date, to_char
from datetime import datetime


def split_data(
    df: pd.DataFrame, split_date: datetime, split_col: str = "timestamp"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    # print(df[split_col].head())
    df_mask = df[split_col] < split_date
    # print(f"mask is: {df_mask.head()}", f"mask not is: {~df_mask.head()}", sep="\n")
    train_data = df[df_mask]
    test_data = df[~df_mask]
    return train_data.copy(deep=True), test_data.copy(deep=True)
