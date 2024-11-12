# kor_grammar_test_flask

한국어 품사 퀴즈

stanza 1.9.2 버전을 이용한 플라스크 기반 웹 페이지입니다.

최상위 폴더 아래에는 메인 파일인 app.py가 있고, 문제로 나올 문제가 기록되는 sentence.csv가 있습니다.

template 폴더 안에는 html 파일들이 있습니다.

static\css 폴더 안에는 웹페이지 스타일이 정의된 css 파일이 있습니다.

logs 폴더 안에는 퀴즈를 푼 로그가 기록된 quiz_logs.csv 파일이 있습니다.

먼저 터미널에서 flask, stanza를 다운받으시고,

app.py 파이썬 파일을 실행시키면 먼저 stanza 한국어 모델이 다운로드되고, 서버가 열립니다.

터미널에 뜨는 두 주소 중 아무거나 접속하시면 됩니다. (두 번째 주소는 url 공유를 위해 host가 0.0.0.0으로 된 주소입니다.)


웹 페이지 설명 : 
폴더에 포함된 바로가기를 실행하면 메인 페이지로 접속됩니다.

총 10문제가 5지선다 객관식으로 출제됩니다.

정답을 체크하지 않고 정답 확인을 하려고 하면, 선택지를 선택하라는 알림이 뜹니다.

정답이면 '정답입니다!' 를 출력하고, 오답이면 '틀렸습니다. 정답은 '부사'입니다.' 와 같이 원래 정답을 같이 출력합니다.

10문제를 다 풀면 총점과 푸는 데 걸린 전체 시간이 출력됩니다.

메인 페이지 오른쪽 아래에 관리자 페이지가 있습니다.

관리자 페이지에서는 텍스트 박스에 새로운 문장을 입력하고, 문장 추가 버튼을 누르면 목록에 새로운 문장을 추가할 수 있고, 추가되면 바로 목록에서 확인 가능합니다.

관리자 페이지에서 로그 확인 버튼을 누르면, 타임라인 기준으로 내림차순으로 정리된 로그를 확인할 수 있습니다.

로그는 문제로 나온 문장, 출제 단어, 사용자 답변, 정답, 정답 여부, 시간 정보가 기록됩니다.

문장들과 로그들은 각각 csv에 저장되어 관리합니다.

MIT License

Copyright (c) 2023 Stanford NLP Group

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
