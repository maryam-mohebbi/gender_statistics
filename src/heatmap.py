import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('../data/cleaned_data.csv', quotechar='"')

df_melt = df.melt(id_vars=['Series Name', 'Series Code', 'Country Name', 'Country Code'],
                  var_name='Year',
                  value_name='Value')

df_melt['Year'] = df_melt['Year'].apply(lambda x: int(x[0:4]))

series_df = df_melt[df_melt['Series Name'] ==
                    "Labor force, female (% of total labor force)"]

pivot_df = series_df.pivot(
    index='Country Name', columns='Year', values='Value')

plt.figure(figsize=(10, 10))
sns.heatmap(pivot_df)

plt.show()
