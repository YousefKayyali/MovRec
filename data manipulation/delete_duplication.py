import pandas as pd

df = pd.read_csv(r"D:\movrec\update_3\rating_3.csv")
print(df)
data= df.drop_duplicates(subset=['userId','movieId'], keep='first')
data.reset_index(drop=True, inplace=True)
data.to_csv(r"D:\movrec\update_3\rating_3.csv", index=False)
df = pd.read_csv(r"D:\movrec\update_4\rating_4.csv")
data= df.drop_duplicates(subset=['userId','movieId'], keep='first')
data.reset_index(drop=True, inplace=True)
data.to_csv(r"D:\movrec\update_4\rating_4.csv", index=False)

