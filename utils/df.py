import os
import pandas as pd


def write_to_df(file_path: str, data: dict) -> None:
    if os.path.exists(file_path):
        old_df = pd.read_csv(file_path)
        new_df = pd.DataFrame([data])
        updated_df = pd.concat([old_df, new_df], ignore_index=True)
        updated_df.to_csv(file_path, index=False)
    else:
        new_df = pd.DataFrame([data])
        new_df.to_csv(file_path, index=False)
