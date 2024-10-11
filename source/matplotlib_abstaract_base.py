import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def load_csv(name:str) -> pd.DataFrame:
    try:
        df = pd.read_csv(name, encoding="cp949")
        print(f"'{os.path.basename(name)}'이 로드되었습니다.")
        return df
    except FileNotFoundError as e:
        print("해당 파일이 존재하지 않습니다.")
        return pd.DataFrame("[[]]")


def seoul_temperature_analysis() -> None:
    df = load_csv("../data/seoul/seoul.csv")
    # 자료의 전체 형태 확인
    # print(df)
    # print(df.shape)

    # 자료의 기초 통계를 확인
    # print(df.describe())

    # 자료의 속성을 확인
    # print(df.columns)

    # 속성별 유일값 확인(Group의 가능성 등을 평가)
    # for col in df.columns:
    #     print(df[col].unique())

    # 속성별 null값의 유무를 확인
    # for col in df.columns:
    #     print(df[col].hasnans)

    # 속성별 존재하는 null의 위치와 개수를 확인
    # for col in df.columns:
    #     if df[col].hasnans:
    #         print(df[df[col].isna()])

    # 값이 없는 데이터를 처리하는 기법
    # null값 제외하기
    # drop_na_df = df.dropna()
    # print("\nNull값 제외")
    # print(drop_na_df.shape)
    # print(drop_na_df.describe())
    # 주의점
    # 시간의 연속성을 담고 있는 데이터를 Null값을 제외하면 시간의 연속성이 해쳐진다.
    # 때문에 이런 연속성을 중요시하는 데이터는 그냥 Null은 Null대로 남기고 표시하기도 한다.

    # 0으로 채우기
    # fill_zero_df = df.fillna(0)
    # print("\n0으로 채우기")
    # print(fill_zero_df.shape)
    # print(fill_zero_df.describe())
    # 주의점
    # 모든 값이 0이 기준이 아닐 수 있다.
    # 0이라는 수가 유의미하게 전체적인 수치에 영향을 줄 수 있기 때문에 신중해야 한다.
    # 일부 데이터의 경우 Null을 0으로 처리하는 것이 옳을 수 있다.(ex) 국민의 수입 정보, 표기하지 않은 답안지에 대한 평가 등)

    # 평균값으로 채우기
    # fill_mean_df = df.copy()
    # for col in fill_mean_df.columns:
    #     try:
    #         mean = fill_mean_df[col].mean()
    #         fill_mean_df[col] = fill_mean_df[col].fillna(mean)
    #     except TypeError as e:
    #         continue
    # print("\n평균값으로 채우기")
    # print(fill_mean_df.shape)
    # print(fill_mean_df.describe())
    # 주의점
    # 광범위하게 0으로 채우는 것보다는 전체적인 수치에 영향을 주지 않아 좋다.
    # 기간마다 특징을 가지는 날씨 데이터에 평균을 채우는 것은 위험하다(평기온 10도이나 겨울에 영하로 떨어지는 국가의 겨울 결측을 채우는 등)

    # 주변 값으로 채우기
    # print("\n주변 값으로 채우기(이전값")
    # fill_front_df = df.ffill()
    # print(fill_front_df.shape)
    # print(fill_front_df.describe())
    #
    # print("\n주변 값으로 채우기(다음값")
    # fill_back_df = df.bfill()
    # print(fill_back_df.shape)
    # print(fill_back_df.describe())
    # 주의점
    # 기간이 짧거나 중간에 한칸씩 비어있을 경우 매우 효율적이나 긴시간이 결측일 경우 전체적인 수치에 영향을 줄 수 있다.
    # 위를 주의한 상태에서는, 주변의 수치가 다음 수치에 영향이 있는 데이터일 경우 매우 효율이 좋다.
    pass
    # 단순 회귀
    # 이전의 값들의 경향을 가장 그럴듯한 예측모델을 만들어 빈 값들을 채움
    # 주의점
    # 모든 경향의 패턴을 예측하기에는 너무 단순한 모델이다.
    pass
    # 딥러닝
    # 컴퓨터가 다회차로 예측모델을 평가하면서 조금씩 내부 값을 바꿔 예측이 가장 정확할 수 있도록 변화함. 이를 마치고 값을 채움.
    # 경우에 따라 단순 회귀에도 못미치며, 데이터의 양과 모델의 성능, 이를 위한 컴퓨터의 성능 등에 크게 의존한다.


def seoul_temperature_visualize():
    df = load_csv("../data/seoul/seoul.csv")
    # 각 column에 대한 데이터를 그래프화
    # 단, 단순 수치 데이터가 아닌 날짜와 지점은 제외
    for col in df.columns[2:]:
        plt.title('col')
        plt.plot(df[col], color='orange')
        plt.show()

    # 특정 날짜의 데이터만 불러와 그래프화
    df["날짜"] = pd.to_datetime(df["날짜"])
    start_date = "2010-10-01"
    end_date = "2010-10-31"

    range_df = df[(df["날짜"] >= start_date) & (df["날짜"] <= end_date)].copy()
    for col in df.columns[2:]:
        plt.plot(range_df[col], color='red')
        plt.show()

    # 특정 날짜의 일교차를 계산하는 법
    columns = df.columns
    range_df["일교차"] = np.abs(range_df[columns[4]] - range_df[columns[3]])
    plt.plot(range_df["일교차"], color="blue")
    plt.show()

    # 동시에 여러개의 그래프를 그리는 법
    plt.plot(range_df[columns[4]], "r")
    plt.plot(range_df[columns[3]], "b")
    plt.show()


def hist_dice() -> None:
    np.random.seed(0)
    # 랜덤하게 주사위를 굴려서 나온 값을 가지는 특정 길이의 array 만들기(100, 10000)
    arr_100 = np.random.randint(1,7,size=(100, ))
    arr_10000 = np.random.randint(1, 7, size=(10000, ))

    # 이를 그래프로 출력, x의 값이 다르므로 두 표를 따로 출력하도록 함.
    # 출력시 길이가 부족하니 이를 늘려줌
    plt.figure(figsize=(16, 4))
    plt.subplot(2,1,1)
    plt.plot(arr_100)
    plt.subplot(2,1,2)
    plt.plot(arr_10000)
    plt.show()
    # 잘못된 표현 방식.
    # 완전한 랜덤(모든 확률변수가 동일한 확률을 가지는 것)을 선형 그래프로 표현하는 것은 내용면으로 의미가 없다.
    # 이럴 경우 '빈도'에 대해서 작동하도록 하는 것이 옳다.
    # 이럴때 사용하는 것이 histogram이다.
    plt.subplot(1,2,1)
    plt.hist(arr_100, bins=6, rwidth=0.8)
    plt.subplot(1,2,2)
    plt.hist(arr_10000, bins=6, rwidth=0.8)
    plt.show()
    # 빈도수가 많아질수록 모든 경우의 수에 대해서 동일한 횟수에 가까워진다.
    # 이는 곧, 동일한 확률로 수행했다는 의미
    # 주사위는 완전 랜덤이다.


def hist_seoul_temperature_visualize() -> None:
    df = load_csv("../data/seoul/seoul.csv")
    df = df.dropna()
    # 기온이 어느정도 빈도를 가지는지를 만들 것이다.
    # 다만, 기온은 주사위의 정수처럼 나눠지는 수가 아니다.
    # 실질적으로, 연속적인 데이터이므로 이를 나누기 위해서 먼저 bins를 몇개를 대상으로 할지 정해야 한다.
    print(df[df.columns[4]].max(), df[df.columns[4]].min())

    # 이를 토대로 38 - (-16)을 기준으로 54개의 bin(1도 단위로 bin을 계산)을 가지도록 histogram구성
    plt.hist(df[df.columns[4]], bins=54, rwidth=0.8)
    plt.show()

    # 4계절 중 여름과 겨울이 도드라지는 계절성을 가진 우리나라의 기온의 분포는 '이중봉형 분포'를 가진다.
    # 이를 통해 우리나라가 여름과 겨울이 훨씬 도드라진 계절을 가진 나라임을 알 수 있다.
    pass

    # 그렇다면 추가적으로 이 빈도수를 통해서 비교해보면 온난화의 영향도 얼추 볼 수 있다.
    plt.subplot(2,1,1)
    plt.hist(df[df.columns[4]][:15000], bins=54, rwidth=0.8)
    plt.subplot(2,1,2)
    plt.hist(df[df.columns[4]][-15000:], bins=54, rwidth=0.8)
    plt.show()

    # 비교가 어려우니 이경우에는 오히려 표를 합쳐주겠다.
    plt.hist(df[df.columns[4]][:15000], bins=54, color='r')
    plt.hist(df[df.columns[4]][-15000:], bins=54, color='b')
    plt.show()

def boxplot_seoul_temperature_visualize() -> None:
    # 물론 이 모든 값을 연속적으로 보아도 되지만 월별 데이터를 보고 싶을 경우가 있다.
    # 일전 우리는 데이터의 기본적인 통계 수치를 보는 방법을 배웠었다.
    df = load_csv("../data/seoul/seoul.csv")
    print(df.describe())

    # 이 수치를 그림으로 표현한 것이 바로 boxplot이다.
    # 87page에 내용이 있으며, 어떤 연속적인 변화를 가지는 그래프(기온이나 주식)에서 단위범위별로 데이터를 볼때 사용된다.
    # 년도별 데이터를 보겠다고 하면 다음과 같이 할 수 있다.
    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year

    df.boxplot(column=df.columns[4], by="연도")
    years = df["연도"].unique()
    plt.xticks(ticks=np.arange(0, len(years), 10), labels=years[::10], rotation=45)
    plt.show()

    # 한글이 깨지는 이유는 단순 폰트 문제입니다. 다음을 추가하여 영문으로 바꿔주어도 되고 한글이 가능한 폰트를 설치를 하셔도 됩니다.
    df.boxplot(column=df.columns[4], by="연도")
    years = df["연도"].unique()
    plt.xticks(ticks=np.arange(0, len(years), 10), labels=years[::10], rotation=45)
    plt.suptitle("")
    plt.title("Seoul Temperature Boxplot")
    plt.xlabel("years")
    plt.ylabel("temperature")
    plt.show()

    # 달별 온도를 원한다면 다음과 같이 될 것입니다.
    df["달"] = df["날짜"].dt.month

    df.boxplot(column=df.columns[4], by="달")
    plt.suptitle("")
    plt.title("Seoul Temperature Boxplot")
    plt.xlabel("month")
    plt.ylabel("temperature")
    plt.show()


def main() -> None:
    # seoul_temperature_analysis()
    seoul_temperature_visualize()
    # hist_dice()
    # hist_seoul_temperature_visualize()
    # boxplot_seoul_temperature_visualize()


if __name__ == "__main__":
    main()