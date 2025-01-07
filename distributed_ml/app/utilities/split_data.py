import pandas as pd
from pandas import DataFrame

def extract_filename(filename: str) -> str:
    filename_list: list[str] = filename.split(".")
    return filename_list[0]    

def split_data(filename: str, n: int) -> list[str]:
    "Splits file into n partitions and returns filename in a list"

    try:
        df: DataFrame = pd.read_csv(filename)
        chunk_size: int = len(df) // n

        new_filename_list: list[str] = []
        for i in range(n):
            start: int = i * chunk_size
            end: int = (i + 1) * chunk_size if i < n - 1 else len(df)
            new_filename = f"{extract_filename(filename)}_chunk_{i + 1}.csv"
                        
            # Temporary. Should be removed when pushing to db
            df.iloc[start: end].to_csv(new_filename, index=False)

            new_filename_list.append(new_filename)
        return new_filename_list

    except Exception as e:
        print(e)            