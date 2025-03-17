import pandas as pd

# Use the Python engine for parsing
df = pd.read_csv('hiking_trails.csv', engine='python')
print(df.head())
