import torch
from transformers import PreTrainedTokenizerFast, BartForConditionalGeneration

tokenizer = PreTrainedTokenizerFast.from_pretrained("gogamza/kobart-summarization")
model = BartForConditionalGeneration.from_pretrained("gogamza/kobart-summarization")

# 요약하고자 하는 기사를 입력합니다.
# 기사원문: http://news.heraldcorp.com/view.php?ud=20211127000015
news_text = """
개그맨 박명수가 소설가 한강의 노벨문학상 수상을 축하하며 현 시국을 언급했다.
10일 방송된 KBS 쿨FM '박명수의 라디오쇼'(이하 '라디오쇼')에는 김태진이 게스트로 출연해 DJ 박명수와 퀴즈를 진행했다.
이날 퀴즈로 한강 작가 관련 내용이 출제됐다. 이후 박명수는 "한강 작가님 축하드린다. 고생하신 만큼 큰 보람이 있으시다. 우리나라의 대경사"라고 말했다.
이어 "요 근래 여러 가지로 뒤숭숭한데 한강 작가님이 딱 정리 한번 해주신다"며 비상계엄 사태 이후 시국을 언급했다. 그는 "국민들에게 큰 힘을 주신 것 같다. 감사하다"고 한강에게 감사 인사를 전했다.
박명수는 지난 9일에도 비상계엄 사태와 관련해 소신 발언을 했다. 박명수는 "주말 내내 뉴스만 보느라 힘드셨죠"라며 입을 뗐다. 이어 "나중에는 우울해지더라. 이제 그만 보시고 원래대로 자기 일 열심히 하면서 살아야 할 것 같다"고 말했다. 그는 "국민의 한 사람으로서, 이 상황이 빨리 좀 수습돼서 많은 국민이 우울해하지 않았으면 하는 바람"이라고 밝혔다.
그는 비상계엄 사태 직후인 지난 4일에도 이와 관련해 목소리를 냈다. 그는 "밤새 깜짝 놀라셨을 거다. 저도 마찬가지"라며 "안 그래도 살기 팍팍한데 이게 무슨 일인지. 고생들 많으시다"고 말했다. 이어 "어제 거의 밤을 새웠다. 너무 어이없는 일이 생겼다. 누가 장난으로 생각하고 잠을 잘 수 있었겠냐. 하고 싶은 얘기는 많이 있지만 잘 정리가 되고 있고, 다들 발 빠르게 제자리로 돌려놓기 위해 노력하고 계시니 믿고 기다려보자"고 덧붙였다.
한편 한강은 이날 스웨덴에서 열리는 노벨문학상 시상식에 참석한다. 한화로 환산했을 때 약 14억 3천만 원의 상금을 받는다.
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
