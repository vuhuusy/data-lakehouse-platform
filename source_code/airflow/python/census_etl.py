import numpy as np
import requests
import pandas as pd
import io
import boto3

def check_api_availability(api_key: str) -> bool:
    """
    Check if the Census API is available by making a simple request.
    """
    BASE_URL = 'https://api.census.gov/data/2023/acs/acs5'
    params = {
        'get': 'B01003_001E',  # Total population
        'for': 'state:*',
        'key': api_key
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return True
    except requests.RequestException:
        return False

def extract(api_key: str) -> pd.DataFrame:
    VARS = [
        "B01003_001E",  # Total population
        "B01002_001E",  # Median age
        "B19013_001E",  # Median household income
        "B17001_002E",  # Poverty count
        "B23025_005E"   # Unemployment count
    ]

    BASE_URL = 'https://api.census.gov/data/2023/acs/acs5'

    params = {
        'get': ','.join(VARS),
        'for': 'state:*',
        'key': api_key
    }

    # Send request
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    # Convert to DataFrame
    columns = data[0]
    df = pd.DataFrame(data[1:], columns=columns)

    # Rename columns
    df = df.rename(columns={
        "B01003_001E": "total_population",
        "B01002_001E": "median_age",
        "B19013_001E": "median_household_income",
        "B17001_002E": "poverty_count",
        "B23025_005E": "unemployment_count",
        "state": "code"
    })

    # Map state codes to abbreviations
    state_abbreviation = {
        "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT", "10": "DE",
        "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL", "18": "IN", "19": "IA",
        "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
        "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
        "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI",
        "45": "SC", "46": "SD", "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
        "54": "WV", "55": "WI", "56": "WY", "60": "AS", "66": "GU", "69": "MP", "72": "PR", "74": "UM", "78": "VI"
    }
    df['state_abbreviation'] = df['code'].map(state_abbreviation)

    # Convert numeric columns to appropriate types
    numeric_cols = ["total_population", "median_age", "median_household_income", "poverty_count", "unemployment_count"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    print(df.head())

    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["poverty_rate"] = df["poverty_count"] / df["total_population"].replace(0, np.nan)
    df["unemployment_rate"] = df["unemployment_count"] / df["total_population"].replace(0, np.nan)
    df["poverty_per_unemployed"] = df["poverty_count"] / df["unemployment_count"].replace(0, np.nan)

    df["population_level"] = pd.cut(
        df["total_population"],
        bins=[-1, 5_000_000, 15_000_000, np.inf],
        labels=["Low", "Medium", "High"]
    )

    df["income_level"] = pd.cut(
        df["median_household_income"],
        bins=[-1, 50_000, 90_000, np.inf],
        labels=["Low", "Medium", "High"]
    )

    df["is_young_state"] = (df["median_age"] < 38).astype(int)

    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())

    df["norm_poverty_rate"] = normalize(df["poverty_rate"])
    df["norm_unemployment_rate"] = normalize(df["unemployment_rate"])
    df["norm_poverty_per_unemployed"] = normalize(df["poverty_per_unemployed"])

    return df[[
        "code", "state_abbreviation",
        "population_level", "income_level", "is_young_state",
        "norm_poverty_rate", "norm_unemployment_rate", "norm_poverty_per_unemployed"
    ]]

def write_parquet_to_minio(
    df: pd.DataFrame,
    bucket_name: str,
    object_name: str,
    minio_endpoint: str,
    access_key: str,
    secret_key: str,
    region: str = "us-east-1",
    use_ssl: bool = False
):

    # Serialize dataframe to parquet in memory
    buffer = io.BytesIO()
    df.to_parquet(buffer, engine="pyarrow", index=False)
    buffer.seek(0)

    # Connect to MinIO S3-compatible storage
    s3 = boto3.client(
        's3',
        endpoint_url = minio_endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        verify=use_ssl  # disable SSL cert validation if use_ssl=False
    )

    # Create bucket if it doesn't exist
    try:
        s3.head_bucket(Bucket=bucket_name)
    except s3.exceptions.ClientError:
        s3.create_bucket(Bucket=bucket_name)

    # Upload
    s3.upload_fileobj(buffer, bucket_name, object_name)
    print(f"Uploaded to s3://{bucket_name}/{object_name}")