import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from joblib import dump
import os

def preprocess_data(data, target_column, save_path, file_path, output_dir):
    """
    Preprocess data: numeric preprocessing + label encoding on target.

    Parameters:
    - data: DataFrame, input data
    - target_column: str, name of the target column
    - save_path: str, path to save the pipeline
    - file_path: str, path to save the column headers

    Returns:
    - X_train, X_test, y_train, y_test, label_encoder (for decoding)
    """

    # Pisahkan fitur numerik
    numeric_features = data.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # Hilangkan kolom target dari daftar fitur numerik (jika termasuk)
    if target_column in numeric_features:
        numeric_features.remove(target_column)

    # Simpan nama kolom fitur ke file CSV (tanpa target)
    column_names = data.columns.drop(target_column)
    df_header = pd.DataFrame(columns=column_names)
    df_header.to_csv(file_path, index=False)
    print(f"[INFO] Nama kolom fitur disimpan di: {file_path}")

    # Pipeline untuk fitur numerik
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', StandardScaler())
    ])

    # Column transformer (hanya fitur numerik)
    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features)
    ])

    # Pisahkan fitur dan target
    X = data.drop(columns=[target_column])
    y = data[target_column]

    # Encode target kategorikal
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.3, random_state=42
    )

    # Fit + transform fitur numerik
    X_train = preprocessor.fit_transform(X_train)
    X_test = preprocessor.transform(X_test)

    # Simpan pipeline numerik
    dump(preprocessor, save_path)
    print(f"[INFO] Pipeline preprocessing disimpan di: {save_path}")

    # Buat direktori output
    os.makedirs(output_dir, exist_ok=True)

    # Simpan ke CSV (konversi dari array ke DataFrame)
    pd.DataFrame(X_train).to_csv(f"{output_dir}/X_train.csv", index=False)
    pd.DataFrame(X_test).to_csv(f"{output_dir}/X_test.csv", index=False)
    pd.DataFrame(y_train).to_csv(f"{output_dir}/y_train.csv", index=False)
    pd.DataFrame(y_test).to_csv(f"{output_dir}/y_test.csv", index=False)

    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    # Baca data mentah
    raw_data = pd.read_csv("data_raw.csv")

    # Jalankan preprocessing
    preprocess_data(
        data=raw_data,
        target_column="encoded_label", 
        save_path="preprocessing/pipeline.joblib",
        file_path="preprocessing/column_headers.csv",
        output_dir="preprocessing/data_preprocessing"
    )

