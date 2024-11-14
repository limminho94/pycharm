from tensorflow.keras.preprocessing.text import text_to_word_sequence
from tensorflow.keras.preprocessing.text import Tokenizer

docs = ['먼저 텍스트의 각 단어를 나누어 토큰화합니다.', '텍스트의 단어로 토큰화해야 딥러닝에서 인식됩나다.', '토큰화한 결과는 딥러닝에서 사용할 수 있습니다.',]

token = Tokenizer()
token.fit_on_texts(docs)

print("\n단어 카운트:\n", token.word_counts)
print("\n문장 카운트:\n", token.document_count)

# # 전처리할 텍스트
# text = '아기 다리고기 다리던 여름 방학'
#
# # 텍스트를 토큰화한다
# result = text_to_word_sequence(text)
# print("\n원문:\n", text)
# print("\n토큰화:\n", result)

