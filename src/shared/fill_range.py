import pandas as pd
from shared.path_manager import PathManager


def fill_range(
    df: pd.DataFrame, time_col: str = "DATE_H", value_col: str = "CNT"
) -> pd.DataFrame:
    df.rename(columns={time_col: "timestamp", value_col: "value"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")

    # Floor start to 00:00 and ceil end to 23:00
    start = df.index.min().normalize()  # midnight of first day
    end = (df.index.max().normalize() + pd.Timedelta(days=1)) - pd.Timedelta(hours=1)

    # Create full hourly range
    full_range = pd.date_range(start=start, end=end, freq="h")

    # Reindex and fill with 0
    df = df.reindex(full_range, fill_value=0).reset_index()
    df = df.rename(columns={"index": "timestamp"})
    return df


def main():
    data_path = PathManager().data_file("voice_offer.csv")
    data = pd.read_csv(data_path)
    print(fill_range(data).head())


if __name__ == "__main__":
    main()
