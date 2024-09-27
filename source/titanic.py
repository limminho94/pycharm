import pandas as pd
import matplotlib.pyplot as plt

# pd.set_option("display.max_rows", None)
# pd.set_option("display.max_columns", None)
# pd.set_option("display.expand_frame_repr", False)

data_path = "../data/iris/Iris.csv"

df:pd.DataFrame = pd.read_csv(data_path, encoding="utf8")
print(df.describe())

print(df["Species"].unique())

setosa_df:pd.DataFrame = df[df["Sepcies"] == "Iris-setosa"]
versicolor_df:pd.DataFrame = df[df["Species"] == "Iris-versicolor"]
virginica_df:pd.DataFrame = df[df["Species"] == "Iris-virginica"]

print(setosa_df.head())
print(setosa_df.tail())

# plt.scatter(setosa_df["SepalLengthCm"], setosa_df["SepalWidthCm"], color="red", label="Setosa")