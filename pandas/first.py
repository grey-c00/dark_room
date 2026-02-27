import pandas as pd

data = {
    'Country': ['India', 'India', 'USA', 'USA'],
    'City': ['Delhi', 'Mumbai', 'New York', 'Chicago'],
    'Population': [30, 20, 8, 3]
}

df = pd.DataFrame(data)
df = df.set_index(['Country', 'City'])
print(df)


print(df.columns)
