from flask import Flask, render_template, request, redirect, url_for, session
import stanza
import random
import time
import csv
import os
import re
import pandas as pd

app = Flask(__name__)
app.secret_key = '12345'

# 스탠자 한국어 모델 다운로드 및 초기화
stanza.download('ko')  # 한국어 모델 다운로드
nlp = stanza.Pipeline('ko')  # 한국어 형태소 분석기 초기화

# 조사 목록
josa_list = [
    # 주격 조사
    '이', '가',

    # 목적격 조사
    '을', '를',

    # 관형격 조사
    '의',

    # 부사격 조사
    '에', '에서', '에게', '한테', '로', '으로', '까지', '부터', '와', '과', '보다',

    # 호격 조사
    '여', '이여',

    # 인용격 조사
    '라고', '고',

    # 접속 조사
    '와', '과', '하고', '이랑',

    # 보조사
    '은', '는', '도', '만', '밖에', '까지', '조차', '마저', '마는', '이나', '나', '든지', '든가', '나마', '마저', '라야', '뿐', '이라도',

    # 비교 조사
    '보다', '처럼', '같이', '만큼',

    # 기타 조사
    '께', '께서', '라도', '야말로', '으로서', '으로써', '이야말로', '이나마', '하고는', '마다'
]




# UPOS 태그를 한국어로 변환하기 위한 매핑 테이블
upos_to_korean = {
    'NOUN': '명사',
    'PROPN': '고유 명사',
    'PRON': '대명사',
    'VERB': '동사',
    'ADJ': '형용사',
    'ADV': '부사',
    'ADP': '전치사',
    'AUX': '조동사',
    'CCONJ': '접속사',
    'DET': '한정사',
    'INTJ': '감탄사',
    'NUM': '수사',
    'PART': '불변화사',
    'SCONJ': '종속 접속사',
    'PUNCT': '구두점',
    'SYM': '기호',
    'X': '기타',
}

# CSV 파일 경로 설정
csv_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sentences.csv')

# Flask 앱이 실행되는 경로를 기준으로 절대 경로 설정
base_dir = os.path.abspath(os.path.dirname(__file__))
log_dir = os.path.join(base_dir, 'logs')
log_file = os.path.join(log_dir, 'quiz_logs.csv')

# CSV 파일에서 문장 불러오기
def load_sentences_from_csv():
    df = pd.read_csv(csv_file)
    return df['sentence'].tolist()

# 조사 분리 함수
def separate_josa(word):
    for josa in josa_list:
        if word.endswith(josa):  # 조사로 끝나는 단어를 찾음
            stem = word[:-len(josa)]
            return stem, josa
    return word, None

# 품사 맞추기 문제 생성 (조사 분리 포함)
def generate_pos_quiz():
    sentences = load_sentences_from_csv()

    # 세션에 출제된 문장 목록이 없으면 빈 리스트로 초기화
    if 'used_sentences' not in session:
        session['used_sentences'] = []

    # 사용된 문장을 제외한 문장 목록 생성
    available_sentences = [sentence for sentence in sentences if sentence not in session['used_sentences']]

    # 모든 문장을 다 출제했으면 초기화
    if not available_sentences:
        session['used_sentences'] = []  # 사용된 문장 초기화
        available_sentences = sentences  # 모든 문장을 다시 사용할 수 있도록 초기화

    # 랜덤으로 문장 선택
    sentence = random.choice(available_sentences)

    # 선택된 문장을 세션에 저장 (출제된 문장으로 기록)
    session['used_sentences'].append(sentence)

    def correct_pos(doc):
        for sent in doc.sentences:
            for word in sent.words:
            # '놀이공원'과 '주말'이 부사(ADV)로 태깅되었을 때 이를 명사(NOUN)로 수정
                if word.text in ['놀이공원', '주말'] and word.upos == 'ADV':
                    word.upos = 'NOUN'  # 명사로 태깅 수정
                if word.text in ['가족'] and word.upos != 'NOUN':
                    word.upos = 'NOUN'

    # Stanza를 사용한 형태소 분석
    doc = nlp(sentence)

    correct_pos(doc)

    morphemes = [] # 단어와 품사를 넣는 리스트

    for sent in doc.sentences:  # sentence는 Stanza의 Sentence 객체이므로, JSON으로 변환 불가
        for word in sent.words:
            word_text = word.text
            pos = upos_to_korean.get(word.upos, word.upos)  # UPOS 태그를 한국어로 변환

            # 구두점은 문제로 출제하지 않도록 필터링
            if pos == '구두점':
                continue
            
            # 조사 분리 후 어간과 조사를 처리
            stem, josa = separate_josa(word_text)
            if josa:
                morphemes.append((stem, pos))  # 어간은 품사를 그대로 사용
                morphemes.append((josa, '조사'))  # 분리된 조사는 '조사'로 처리
            else:
                morphemes.append((word_text, pos))

    quiz_word, quiz_pos = random.choice(morphemes)

    # 오답 선택지로 쓸 랜덤한 태그 4개 생성 (정답을 제외하고)
    all_pos_tags = list(upos_to_korean.values()) + ['조사']  # '조사' 태그도 추가
    all_pos_tags.remove('구두점') # 구두점이 선택지로 나오지 않게 제외
    all_pos_tags.remove(quiz_pos)  # 정답을 제외
    wrong_choices = random.sample(all_pos_tags, 4)

    # 정답 포함한 5지선다 선택지 생성
    choices = wrong_choices + [quiz_pos]
    random.shuffle(choices)  # 선택지 순서를 섞음

    # 세션에 문제와 정답 저장 (JSON 직렬화 가능한 형태로 저장)
    session['current_sentence'] = sentence  # sentence는 문자열이므로 직렬화 가능
    session['quiz_word'] = quiz_word  # quiz_word는 문자열이므로 직렬화 가능
    session['correct_pos'] = quiz_pos  # quiz_pos는 문자열이므로 직렬화 가능
    session['choices'] = choices  # 리스트 형태로 저장 가능

    return sentence, quiz_word, choices

@app.route('/')
def index():
    session['score'] = 0
    session['total_questions'] = 0
    session['start_time'] = time.time()
    return render_template('index.html')

# 문장에서 문제로 나온 단어 밑줄 혹은 볼드 처리
def highlight_word_in_sentence(sentence, quiz_word, highlight_type="underline"):
    if highlight_type == "underline":
        highlighted_word = f"<u>{quiz_word}</u>"  # 밑줄 처리
    elif highlight_type == "bold":
        highlighted_word = f"<b>{quiz_word}</b>"  # 볼드 처리
    else:
        highlighted_word = quiz_word  # 기본 처리
    
    # 주어진 문장에서 단어를 강조 처리된 단어로 대체
    return sentence.replace(quiz_word, highlighted_word)


@app.route('/question')
def question():
    if session['total_questions'] >= 10:
        return redirect(url_for('result'))

    # 문제 생성
    sentence, quiz_word, choices = generate_pos_quiz()
    total_questions = session['total_questions'] + 1

    # 품사를 맞출 단어에 밑줄 처리
    sentence_with_highlight = highlight_word_in_sentence(sentence, quiz_word, highlight_type="underline")

    return render_template('question.html', sentence=sentence_with_highlight, quiz_word=quiz_word, choices=choices, total_questions=total_questions)


@app.route('/check_answer', methods=['POST'])
def check_answer():
    user_answer = request.form['answer']  # 사용자가 선택한 답변
    correct_answer = session['correct_pos']
    sentence = session['current_sentence']
    quiz_word = session['quiz_word']
    is_correct = user_answer == correct_answer

    # 결과 메시지 설정
    if is_correct:
        session['score'] += 1
        result_message = "정답입니다!"
    else:
        result_message = f"틀렸습니다. 정답은 '{correct_answer}'입니다."

    session['total_questions'] += 1

    # 로그 기록
    with open(log_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([user_answer, correct_answer, sentence, quiz_word, "정답" if is_correct else "오답", time.strftime('%Y-%m-%d %H:%M:%S')])

    return render_template('answer.html', result=result_message)

@app.route('/result')
def result():
    end_time = time.time()
    total_time = round(end_time - session['start_time'], 2)
    score = session['score']
    
    return render_template('result.html', score=score, total_time=total_time)

# 관리자 페이지 - 텍스트 추가
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_text = request.form['new_text']
        
        # 정규식으로 문장 단위로 텍스트 분리
        new_sentences = re.split(r'\“?\‘?(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\’?\”?\s', new_text)

        # CSV 파일 불러오기 (Unnamed: 0 제거)
        df = pd.read_csv(csv_file)
        df = df.drop(columns=['Unnamed: 0'], errors='ignore')  # Unnamed 열 제거
        
        # 새로운 문장을 DataFrame으로 변환
        new_sentences_df = pd.DataFrame({'sentence': [sentence.strip() for sentence in new_sentences if sentence.strip()]})
        
        # 기존 DataFrame과 새로운 문장 DataFrame을 concat으로 병합
        df = pd.concat([df, new_sentences_df], ignore_index=True)

        # 줄바꿈 문자 제거 후 CSV 파일에 저장
        df['sentence'] = df['sentence'].str.replace(r'\\r\\n|\r|\n', ' ', regex=True)
        df.to_csv(csv_file, index=False, encoding='utf-8')

        return render_template('admin.html', sentences=load_sentences_from_csv(), message="새 문장이 추가되었습니다.")
    
    # 문장 목록 불러오기 (GET 요청 시)
    return render_template('admin.html', sentences=load_sentences_from_csv())


@app.route('/logs')
def logs():
    # 로그 파일을 읽어옴
    with open(log_file, 'r', encoding='utf-8') as file:
        log_data = csv.reader(file)
        logs = list(log_data)
    
    # 로그를 시간 기준으로 내림차순 정렬 (시간이 마지막 컬럼에 있다고 가정)
    logs = sorted(logs[1:], key=lambda x: x[-1], reverse=True)  # 첫 번째 row(헤더)를 제외하고 정렬

    return render_template('log.html', logs=logs)

if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.makedirs('logs')
    app.run(debug=True, host='0.0.0.0')
