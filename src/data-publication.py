import pandas as pd
import numpy as np

data = pd.read_csv('../data/data.csv')
data = data.replace('..', np.nan)
year_columns = [col for col in data.columns if 'YR' in col]

# First step: Removing missing countries:
data['all_missing'] = data[year_columns].isnull().all(axis=1)
missing_counts = data.groupby('Country Name').apply(
    lambda group: group['all_missing'].sum())
missing_counts_sorted = missing_counts.sort_values(ascending=False)

for country, count in missing_counts_sorted.items():
    print(f"{country}: {count}")

countries_to_remove = missing_counts_sorted[missing_counts_sorted > 6].index.tolist(
)
data_cleaned = data[~data['Country Name'].isin(countries_to_remove)]


# Second step: Removing missing years:
missing_values_per_year = data_cleaned[year_columns].isnull().sum(axis=0)
percentage_missing_per_year = (
    missing_values_per_year / len(data_cleaned)) * 100

for year, count in missing_values_per_year.items():
    print(
        f"{year}: {count} missing values ({percentage_missing_per_year[year]:.2f}% of total)")

years_to_drop = percentage_missing_per_year[percentage_missing_per_year > 40].index
data_cleaned = data_cleaned.drop(years_to_drop, axis=1)

year_columns = [col for col in data_cleaned.columns if 'YR' in col]


# Third step: Removing missing series
missing_values_per_series = data_cleaned.groupby('Series Name').apply(
    lambda group: group[year_columns].isnull().sum().sum())
percentage_missing_per_series = (
    missing_values_per_series / (len(year_columns) * len(data_cleaned)) * 100)

for series, count in missing_values_per_series.items():
    print(
        f"{series}: {count} missing values ({percentage_missing_per_series[series]:.2f}% of total)")

series_to_drop = percentage_missing_per_series[percentage_missing_per_series > 0.5].index
data_cleaned = data_cleaned[~data_cleaned['Series Name'].isin(series_to_drop)]

data_cleaned = data_cleaned.drop(columns=['all_missing'])
# Export cleaned data
data_cleaned.to_csv('../data/cleaned_data.csv', index=False)
