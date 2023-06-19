# http://openapi.tour.go.kr/openapi/service/EdrcntTourismStatsService/getEdrcntTourismStatsList

import os
import sys
import urllib.request
import datetime
import time
import json
import pandas as pd

# 국가별 연월별 방한인원 증감폭 그래프 그리기
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

font_path = "C:\\Windows\\Fonts\\H2GTRM.TTF"
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc("font", family=font_name)

# x축과 y축 레이블 설정
plt.xlabel('연월')
plt.ylabel('인원 수')

# Encoding
# ServiceKey = "uX5MtskMMTbnV7wc9YQXynjfvdZL0SNtyZEfwCEqw9Wv0cTdKd4Us%2FCQTUvtmuRT7%2FBJ5JplUbTiBMFKfmEXrw%3D%3D"
# Decoding
ServiceKey = "uX5MtskMMTbnV7wc9YQXynjfvdZL0SNtyZEfwCEqw9Wv0cTdKd4Us/CQTUvtmuRT7/BJ5JplUbTiBMFKfmEXrw=="


# [CODE 1]
def getRequestUrl(url):
	req = urllib.request.Request(url)
	try:
		response = urllib.request.urlopen(req)
		if response.getcode() == 200:
			print("[%s] Url Request Success" % datetime.datetime.now())
			return response.read().decode('utf-8')
	except Exception as e:
		print(e)
		print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
		return None


# [CODE 2]
def getTourismStatsItem(yyyymm, national_code, ed_cd):
	service_url = "http://openapi.tour.go.kr/openapi/service/EdrcntTourismStatsService/getEdrcntTourismStatsList"
	parameters = "?_type=json&serviceKey=" + ServiceKey  # 인증키
	parameters += "&YM=" + yyyymm
	parameters += "&NAT_CD=" + national_code
	parameters += "&ED_CD=" + ed_cd
	
	url = service_url + parameters
	print(url)  # 액세스 거부 여부 확인용 출력
	retData = getRequestUrl(url)  # [CODE 1]
	
	if (retData == None):
		return None
	else:
		return json.loads(retData)


# [CODE 3]
def getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear):
	jsonResult = []
	result = []
	dataEND = None  # 초기값 설정
	
	# 데이터 리스트
	x = []  # x축 데이터 : 연월
	y = []  # y축 데이터 : 인원 수
	
	for year in range(nStartYear, nEndYear + 1):
		for month in range(1, 13):
			yyyymm = "{0}{1:0>2}".format(str(year), str(month))
			jsonData = getTourismStatsItem(yyyymm, nat_cd, ed_cd)  # [CODE 2]
			
			# 데이터가 없는 마지막 항목인 경우 : 올해의 통계 데이터가 있는 마지막 달----------------------------
			if (jsonData['response']['header']['resultMsg'] == 'OK' and jsonData['response']['body']['items'] == ''):
				dataEND = "{0}{1:0>2}".format(str(year), str(month - 1))
				print("데이터 없음.... \n 제공되는 통계 데이터는 %s년 %s월까지 입니다." % (str(year), str(month - 1)))
				break
			
			# jsonData를 출력하여 확인...........................................
			print(json.dumps(jsonData, indent=4, sort_keys=True, ensure_ascii=False))
			natName = jsonData['response']['body']['items']['item']['natKorNm']
			natName = natName.replace(' ', '')
			num = jsonData['response']['body']['items']['item']['num']
			ed = jsonData['response']['body']['items']['item']['ed']
			print('[ %s_%s : %s ]' % (natName, yyyymm, num))
			print('-----------------------------------------------------')
			
			jsonResult.append({'nat_name': natName, 'nat_cd': nat_cd, 'yyyymm': yyyymm, 'visit_cnt': num})
			result.append([natName, nat_cd, yyyymm, num])
			
			# 그래프 값 저장
			temp = "{0:0>2}".format(str(month))
			x.append(temp)
			y.append(num)
			
			# 데이터가 있는 마지막 항목인 경우 : 끝나는 해의 12월까지 검색 완료 ----------------------------
			if (yyyymm == str(nEndYear) + "12"):
				dataEND = yyyymm
		
		plt.figure(figsize=(12, 5))  # 그래프 비율
		plt.grid(True)  # 그리드 표시
		plt.title(natName + " " + str(year) + "년 \n연월별 방한 인원 변동폭")  # 그래프 제목 설정
		plt.plot(x, y)
		plt.savefig('./ ' + str(natName) + '_' + str(year) + '.png')  # 그래프를 이미지 파일로 저장
		plt.show()  # 그래프 보여주기
		
		# 연도 별 인원 수 초기화
		x = []
		y = []
	return (jsonResult, result, natName, ed, dataEND)


# [CODE 0]
if __name__ == '__main__':
	# 홈페이지 예시 코드
	# url = 'http://openapi.tour.go.kr/openapi/service/EdrcntTourismStatsService/getEdrcntTourismStatsList'
	# params = {'serviceKey': ServiceKey_decode, 'YM': '201201', 'NAT_CD': '112', 'ED_CD': 'E'}
	# 
	# response = requests.get(url, params=params)
	# print(response.content)
	
	# ppt 코드 main()
	jsonResult = []
	result = []
	
	print("<< 국내 입국한 외국인의 통계 데이터를 수집합니다. >>")
	nat_cd = input('국가 코드를 입력하세요(중국: 112 / 일본: 130 / 미국: 275) : ')
	nStartYear = int(input('데이터를 몇 년부터 수집할까요? : '))
	nEndYear = int(input('데이터를 몇 년까지 수집할까요? : '))
	ed_cd = "E"  # E : 방한외래관광객, D : 해외 출국
	jsonResult, result, natName, ed, dataEND = getTourismStatsService(nat_cd, ed_cd, nStartYear, nEndYear)  # [CODE 3]
	
	# 파일저장 1 : json 파일
	with open('./%s_%s_%d_%s.json' % (natName, ed, nStartYear, dataEND), 'w', encoding='utf8') as outfile:
		jsonFile = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
		outfile.write(jsonFile)
	# 파일저장 2 : csv 파일
	columns = ["입국자국가", "국가코드", "입국연월", "입국자 수"]
	result_df = pd.DataFrame(result, columns=columns)
	result_df.to_csv('./%s_%s_%d_%s.csv' % (natName, ed, nStartYear, dataEND), index=False, encoding='cp949')

# 000=미상
# 100=한  국
# 101=아프가니스탄
# 104=바레인
# 105=방글라데시
# 106=부  탄
# 107=브루나이
# 108=미얀마
# 109=영령 인도양섬
# 110=캄보디아
# 111=스리랑카
# 112=중  국
# 113=대  만
# 114=키프로스
# 118=북  한
# 120=홍  콩
# 121=홍콩난민
# 124=인  도
# 125=인도네시아
# 126=이  란
# 127=이라크
# 128=이스라엘
# 130=일  본
# 131=요르단
# 133=카자흐스탄
# 134=키르기스스탄
# 135=쿠웨이트
# 138=라오스
# 139=레바논
# 142=마카오
# 143=말레이시아
# 144=몰디브
# 145=몽  골
# 146=마요트
# 148=네  팔
# 150=오  만
# 153=파키스탄
# 154=팔레스타인
# 155=필리핀
# 156=티모르
# 159=카타르
# 162=사우디아라비아
# 163=시킴왕국
# 164=싱가포르
# 165=시리아
# 169=타지키스탄
# 170=태  국
# 171=터  키
# 172=투르크메니스탄
# 180=아랍에미리트연합
# 181=우즈베키스탄
# 185=베트남
# 191=예멘공화국
# 192=예멘인민민주공화국
# 200=앵귈라
# 201=앤티가 바부다
# 202=아르헨티나
# 203=아루바
# 205=바하마
# 206=바베이도스
# 207=벨리즈
# 208=볼리비아
# 209=브라질
# 210=버뮤다
# 211=부베트
# 212=케이맨 제도
# 213=캐나다
# 214=칠  레
# 215=콜롬비아
# 216=코스타리카
# 217=쿠  바
# 220=도미니카연방
# 221=도미니카공화국
# 223=이스터 제도
# 224=에콰도르
# 225=엘살바도르
# 226=포클랜드
# 227=불령 가이아나
# 229=그레나다
# 230=과들루프
# 231=과테말라
# 232=가이아나
# 235=아이티
# 236=온두라스
# 240=자메이카
# 247=마르티니크
# 248=멕시코
# 249=몬서래트
# 251=네덜란드령 앤틸리스
# 252=니카라과
# 255=파나마
# 256=파라과이
# 257=페  루
# 258=푸에르토리코
# 260=남조지아 남샌드위치 군도
# 261=상피에르 미클롱
# 262=세인트크리스토퍼 네비스
# 263=세인트루시아
# 264=세인트빈센트 그레나딘
# 265=수리남
# 268=트리니다드토바고
# 269=터크스케이커스
# 274=우루과이
# 275=미  국
# 276=미국인근섬
# 280=베네수엘라
# 281=미령 버진아일랜드
# 282=영령 버진아일랜드
# 301=알바니아
# 302=안도라
# 303=오스트리아
# 304=아르메니아
# 305=아제르바이잔
# 306=벨기에
# 307=불가리아
# 308=벨로루시
# 309=보스니아-헤르체고비나
# 310=체  코
# 311=페로 섬
# 312=에스토니아
# 313=덴마크
# 314=영국 보호민
# 315=영국 속국민
# 316=영  국
# 317=영국 속령지 시민
# 318=영국 외지민
# 319=영국 외지시민
# 320=핀란드
# 321=프랑스
# 323=그루지야
# 324=독  일
# 325=동  독
# 326=그리스
# 327=지브롤터
# 328=그린란드
# 329=헝가리
# 333=아이슬란드
# 334=아일랜드
# 335=이탈리아
# 337=코소보
# 339=라트비아
# 340=리히텐슈타인
# 341=룩셈부르크
# 342=리투아니아
# 343=마케도니아
# 344=몰  타
# 345=모나코
# 346=몰도바
# 347=몬테네그로
# 350=네덜란드
# 352=노르웨이
# 360=폴란드
# 361=포르투갈
# 365=루마니아
# 366=러시아(연방)
# 367=세르비아
# 368=슬로바크
# 370=슬로베니아
# 371=산마리노
# 372=스페인
# 373=스웨덴
# 374=스위스
# 375=스발바르
# 378=우크라이나
# 380=독립국가연합
# 390=바티칸
# 391=크로아티아
# 395=유고슬라비아
# 396=세르비아 앤 몬테네그로
# 404=오스트레일리아
# 411=캐롤라인 군도
# 412=쿡아일랜드
# 413=크리스마스
# 414=코코스
# 418=피  지
# 419=불령 폴리네시아
# 420=불령 남태평양섬
# 423=괌
# 425=허드 맥도날드
# 429=키리바시
# 434=북마리아나 군도
# 435=미크로네시아
# 436=마라아나 군도
# 437=마샬군도
# 438=미드웨이
# 441=나우루
# 443=뉴칼레도니아
# 446=뉴질랜드
# 447=니우에
# 448=노폴크
# 451=팔라우
# 452=파푸아뉴기니
# 454=핏캐른
# 461=사모아
# 462=미령 사모아
# 463=솔로몬군도
# 464=호주령 솔로몬군도
# 473=통  가
# 474=토켈라우
# 475=투발루
# 485=비누아투
# 490=웨이크아일랜드
# 491=월리스푸투나
# 502=알제리
# 503=앙골라
# 506=보츠와나
# 507=부룬디
# 510=카메룬
# 511=카나리아군도
# 512=카보베르데
# 513=중앙 아프리카 공화국
# 514=차  드
# 515=코모로
# 516=콩  고
# 517=콩고 민주공화국
# 520=베  냉
# 521=지부티
# 525=이집트
# 526=적도기니
# 527=에티오피아
# 528=에리트레아
# 530=가  봉
# 531=감비아
# 532=가  나
# 533=기  니
# 534=기니비사우
# 537=코트디부아르
# 540=케  냐
# 542=레소토
# 543=라이베리아
# 544=리비아
# 550=마다가스카르
# 551=말라위
# 552=말  리
# 553=모리타니
# 554=모리셔스
# 555=모로코
# 556=모잠비크
# 560=나미비아
# 561=니제르
# 562=나이지리아
# 564=레위니옹
# 565=짐바브웨
# 566=르완다
# 571=상투메 프린시페
# 572=세네갈
# 573=세이셸
# 574=시에라리온
# 575=소말리아
# 576=남아프리카 공화국
# 577=세인트헬레나
# 578=수  단
# 579=스와질란드
# 580=남수단공화국
# 583=탄자니아
# 584=토  고
# 585=튀니지
# 588=우간다
# 589=부르키나파소
# 591=서사하라
# 594=자이르
# 595=잠비아
# 620=남극대륙
# 666=공해
# 900=국제연합
# 998=승무원
# 999=교포