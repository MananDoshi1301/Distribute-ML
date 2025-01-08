import pandas as pd, os
from pandas import DataFrame

def extract_filename(filename: str) -> str:
    strip_slash: list[str] = filename.split("/")
    if not strip_slash[-1]: 
        print("Error on stripping slash")
        return 'data'
    filename: str = strip_slash[-1] 
    strip_extension: list[str] = filename.split(".")
    if not strip_extension[0]: 
        print("Error on stripping extension")
        return 'data'
    return strip_extension[0]    

def save_chunk(new_filename: str, df: DataFrame, start: int, end: int):
    filefolder = "data/"            
    df.iloc[start: end].to_csv(os.path.join(filefolder, new_filename), index=False)

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
            save_chunk(new_filename, df, start, end)            

            new_filename_list.append(new_filename)
        return new_filename_list

    except Exception as e:
        print(e)            