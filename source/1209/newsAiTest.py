import torch
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

tokenizer = PreTrainedTokenizerFast.from_pretrained("gogamza/kobart-summarization")
model = BartForConditionalGeneration.from_pretrained("gogamza/kobart-summarization")

# 요약하고자 하는 기사를 입력합니다.
# 기사원문: http://news.heraldcorp.com/view.php?ud=20211127000015
news_text = """
유럽 주요 언론들은 윤석열 대통령이 탄핵 위기를 모면할 경우 한국의 정치적 불확실성이 커질 것으로 전망했다.
프랑스 일간 르몽드는 7일(현지시간) “비상계엄 선포로 한국 사회를 충격에 빠뜨린 윤 대통령 탄핵소추안이 정족수 미달로 폐기됐다”며 “수만명의 시위에도 여당 의원들의 보이콧으로 표결은 진행되지 못했다”고 보도했다.
르몽드는 윤 대통령이 이날 오전 대국민담화에서 ‘임기단축을 포함한 정국 안정 방안을 당에 일임하겠다’고 밝혔으나, 이 짧은 연설은 국민들의 분노를 진정시키지 못했다고 지적했다.
영국 일간 더타임스 역시 여당 의원들이 투표를 보이콧하면서 탄핵안이 불발됐다고 주요 뉴스로 보도했다. 매체는 분노한 야당 의원들이 “반역자들”이라고 외치기도 했다고 현장을 상세히 보도했다.
더타임스는 또 시위대 사이에서 분노가 퍼졌다며, 며칠 밤을 시위에 참여한 한 학생이 “그들이 보이콧으로 새로운 출발을 향한 우리 희망을 막고 있다니 믿기지 않는다”고 말했다고도 전했다.
매체는 또 보수 지지자들이 도심에서 연 집회에서 ‘야당에 반국가 친북 세력이 침투했다’는 윤 대통령의 주장이 되풀이됐다며 이를 “한국 사회의 깊은 균열”을 보여주는 것이라고 지적했다.
유럽 주요 언론들은 윤 대통령이 탄핵 위기에서 살아남았으나, 그의 정치적 장래가 불투명하다는 데 의견을 같이했다.
영국 일간 가디언은 실시간으로 한국의 탄핵정국 관련 뉴스를 전하는 라이브 페이지에서 “탄핵안 불발은 5년 단임 임기 중 3년에 조금 못 미치는 윤 대통령의 장래에 대한 불확실성을 더할 것”이라고 평가했다.
이탈리아 매체 코리에레델라세라는 “추운 날씨 속에서 수많은 시민이 오랜 시간 기다렸지만, 결국 국민들의 기대를 저버렸다”며 “윤석열은 적어도 당분간 대통령직을 유지하겠으나, 야당인 민주당의 지도부는 다음주에 탄핵안을 다시 발의할 것이라고 밝혔다”고 보도했다.
코리에레델라세라는 또 이번 탄핵 무산으로 한국의 정치 시나리오가 복잡해졌지만, 윤 대통령의 운명은 이미 결정된 것이나 다름없다고 짚었다.
"""

# 토크나이저를 사용하여 뉴스기사 원문을 모델이 인식할 수 있는 토큰형태로 바꿔줍니다.
input_ids = tokenizer.encode(news_text)
# print(input_ids)

# 모델에 넣기 전 문장의 시작과 끝을 나타내는 토큰을 추가합니다.
input_ids = [tokenizer.bos_token_id] + input_ids + [tokenizer.eos_token_id]
input_ids = torch.tensor([input_ids])

summary_text_ids = model.generate(
    input_ids=input_ids,
    bos_token_id=model.config.bos_token_id,
    eos_token_id=model.config.eos_token_id,
    length_penalty=1.5, # 길이에 대한 penalty값. 1보다 작은 경우 더 짧은 문장을 생성하도록 유도하며, 1보다 클 경우 길이가 더 긴 문장을 유도
    max_length=128,     # 요약문의 최대 길이 설정
    min_length=32,      # 요약문의 최소 길이 설정
    num_beams=4,        # 문장 생성시 다음 단어를 탐색하는 영역의 개수
)

# 요약 출력
print(tokenizer.decode(summary_text_ids[0], skip_special_tokens=True))
