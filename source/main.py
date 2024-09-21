import random

while True:
    number = random.sample(range(0, 10),3)
    print(number)
    lev = 0
    ch = int(input("1.상(10회) 2.중(15회) 3.하(20회)"))
    if ch == 1:
        lev = 10
    elif ch == 2:
        lev = 15
    elif ch == 3:
        lev = 20
    cnt = 1
    while(cnt <= lev):
        s = 0
        b = 0
        o = 0
        a = []
        a = list(map(int, input("숫자3개를 입력하세요")))
        print("입력 숫자번호:", a)
        for i in range(0,3):
            for j in range(0,3):
                if number[i] == a[j] and i == j:
                    s += 1
                elif number[i] == a[j] and i != j:
                    b += 1
        print(f"스트라이크:{s}",f"볼:{b}")
        if s == 3:
            print("승리")
            break
        if cnt == lev:
            print("남은 기회가 모두 소진되었습니다")
        cnt += 1
    y = int(input("다시 하시겠습니까? 1.한다 2.안한다"))
    if y == 1:
        continue
    else:
        break
