# -*- coding: utf-8 -*-
import datetime
import pytz

def boj_rating_to_lv(rating):
    if rating < 30: return 0
    if rating < 150: return rating // 30
    if rating < 200: return 5
    if rating < 500: return (rating-200) // 100 + 6
    if rating < 1400: return (rating-500) // 150 + 9
    if rating < 1600: return 15
    if rating < 1750: return 16
    if rating < 1900: return 17
    if rating < 2800: return (rating-1900) // 100 + 18
    if rating < 3000: return (rating-2800) // 50 + 27
    return 31


def create_solved_dict(json):
    solved_dict = {}
    # 36주 내 가장 많이 문제를 풀은 날의 solved count가 4 미만일 경우 4으로 설정
    solved_dict['solved_max'] = 4
    
    KST_TZ = pytz.timezone('Asia/Seoul')
    today_kst = datetime.datetime.now(KST_TZ)
    
    weekday_idx = today_kst.isoweekday() % 7 

    for problem in json:
        # timestamp 형식: "2024-06-29T17:00:00.000Z" (ISO 8601, Z는 UTC)
        timedata_str = problem['timestamp'].split('.')[0].replace('T', ' ')
        
        # UTC 시간으로 파싱
        trimmed_timedata_utc = datetime.datetime.strptime(timedata_str, '%Y-%m-%d %H:%M:%S')
        
        # UTC 시간을 KST로 변환
        timestamp_kst = pytz.utc.localize(trimmed_timedata_utc).astimezone(KST_TZ)
        
        # solved.ac의 하루 시작이 KST 오전 6시이므로, 해당 기준에 맞게 날짜 조정
        # 만약 문제 해결 시간이 KST 자정(00:00)부터 오전 5시 59분 59초 사이라면, 이전 날짜로 간주
        # 즉, KST 00:00 ~ 05:59 사이의 기록은 하루 전 날짜로 포함
        if timestamp_kst.hour < 6:
            solved_date = (timestamp_kst - datetime.timedelta(days=1)).date()
        else:
            solved_date = timestamp_kst.date()
        
        # 히트맵 기간 (36주)을 벗어나는 오래된 데이터는 무시하고 함수 종료
        # 36주 = 252일
        # today_kst.date()는 로컬 오늘의 날짜 (KST 기준)
        if today_kst.date() - solved_date > datetime.timedelta(weeks=36 + 1): # 36주 + 여유분 1주 (7일)
            break # 오래된 데이터를 만나면 더 이상 처리할 필요 없음

        # solved_dict에 저장할 때 키를 datetime.date 객체로 변경 (main.py의 now_in_loop와 타입 일치)
        if solved_date not in solved_dict:
            solved_dict[solved_date] = 1
        else:
            solved_dict[solved_date] += 1
            solved_dict['solved_max'] = max(solved_dict['solved_max'], solved_dict[solved_date])
            
    solved_dict['solved_max'] = min(solved_dict['solved_max'], 50) # solved_max 최대 50으로 제한

    return solved_dict


def get_starting_day():
    # 이 함수는 main.py에서 직접 사용되지 않지만, 일관성을 위해 36주 기준으로 수정
    # solved.ac는 하루의 시작이 KST 오전 6시 (UTC+9)
    KST_TZ = pytz.timezone('Asia/Seoul')
    today_kst = datetime.datetime.now(KST_TZ)
    
    # Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6
    weekday_idx = today_kst.isoweekday() % 7
    
    # 36주 = 252일
    # 시작 날짜는 오늘로부터 36주 전의 일요일 (히트맵의 첫 번째 열)
    start_date = (today_kst.date() - datetime.timedelta(days=weekday_idx + (36 * 7) - 1)) # -1로 시작점 조정
    
    return today_kst.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d')


def get_tomorrow(current_date: datetime.date) -> datetime.date:
    """
    주어진 날짜(datetime.date 객체)의 다음 날짜를 datetime.date 객체로 반환합니다.
    """
    tomorrow = current_date + datetime.timedelta(days=1)
    return tomorrow


# solved.ac에서 사용하는 티어 id (0:Unrated, 1~5:Bronze, ..., 31:Master)
def get_tier_name(id: int):
    if id == 0: return 'Unrated'
    lut = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Ruby', 'Master']
    tier = lut[(id - 1) // 5]
    lv = ((id - 1) % 5) + 1
    if tier == 'Master': return 'Master'
    return '{tier} {lv}'.format(tier=tier, lv=lv)


# 티어명을 solved.ac에서 사용하는 티어 id로 변환 ('Bronze 4' => 2)
def get_tier_id(name: str):
    name = name.lower()
    arr = name.split(' ') + [None] # padding when level is empty
    tier = arr[0]
    lv = int(arr[1]) if arr[1] else 0
    lut = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'ruby', 'master']
    if tier in lut:
        if tier == 'master': return 31
        return lut.index(tier) * 5 + lv
    return 0 # unrated
