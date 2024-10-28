import os

import pandas as pd
import matplotlib.pyplot as plt


def extract_data(df: pd.DataFrame, index) -> pd.Series:
    """"""
    return df.loc[index]


def separate_to_gender(series: pd.Series, drops: list = None) -> tuple[pd.Series, pd.Series]:
    """"""
    indexes = series.index
    if drops is not None:
        indexes = indexes.drop(drops)
    series = series[indexes]
    total_len = len(indexes)
    half = round(total_len / 2)
    return series[:half], series[half:]


def show_graph(data_1: pd.Series, data_2: pd.Series) -> None:
    """"""
    size = (data_1.sum(), data_2.sum())
    plt.figure(figsize=(10, 5))
    plt.title("Male and female population")
    plt.pie(size, labels=("Male", "Female"), autopct="%.1f%%", colors=("blue", "crimson"), startangle=90)
    plt.legend()
    plt.show()


def main():
    path = "../data/gender/gender.csv"
    df = pd.read_csv(path, index_col=0, encoding="cp949")
    # print(df)
    # print(df.columns)
    # print(df.index)
    print(pd.Series)

    while True:
        inputs = input("원하는 동네를 말해주세요. : ")
        value = df.index[df.index.str.contains(inputs)]

        if len(value) == 0:
            input("존재하지 않는 지역입니다. 다시 검색해 주세요!(Enter)")
        else:
            """"""
            drop = ["2019년01월_남_총인구수", "2019년01월_남_연령구간인구수", "2019년01월_여_총인구수", "2019년01월_여_연령구간인구수"]
            for idx in value:
                series = extract_data(df, idx)
                m, f = separate_to_gender(series, drop)
                print(f"현재 지역: {idx}")
                show_graph(m, f)


if __name__ == "__main__":
    main()