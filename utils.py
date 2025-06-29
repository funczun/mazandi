# -*- coding: utf-8 -*-
import datetime
import pytz

from mapping import TIER_RATES

# solved.ac 기준 하루의 시작은 KST(UTC+9) 오전 6시
KST = pytz.timezone('Asia/Seoul')

def get_solved_ac_effective_day(dt_object: datetime.datetime = None) -> datetime.datetime:
    if dt_object is None:
        dt_object = datetime.datetime.now(KST)

    effective_day_kst = dt_object.replace(hour=6, minute=0, second=0, microsecond=0)
    # 현재 시간이 오전 6시 이전이면 어제 날짜로 간주
    if dt_object.time() < datetime.time(6, 0, 0):
        effective_day_kst -= datetime.timedelta(days=1)
        
    return effective_day_kst.date()


def boj_rating_to_lv(rating):
    if rating >= TIER_RATES[31]:
        return 31

    if rating < TIER_RATES[0]:
        return 0

    for i in range(1, len(TIER_RATES)):
        if rating < TIER_RATES[i]:
            return i - 1

    return 0


def create_solved_dict(json_data):
    solved_dict = {'solved_max': 4}
    
    effective_today_kst_date = get_solved_ac_effective_day()
    
    # 18주 시작점 계산 (18주 = 126일)
    cutoff_date = effective_today_kst_date - datetime.timedelta(days=126)

    for problem in json_data:
        timedata_str = problem['timestamp'].split('.')[0].replace('T', ' ')
        utc_dt = datetime.datetime.strptime(timedata_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
        
        problem_kst_time = utc_dt.astimezone(KST) 
        problem_effective_day_kst_date = get_solved_ac_effective_day(problem_kst_time)
        
        # 18주 내에 해결한 문제까지만 solved_dict에 저장
        if problem_effective_day_kst_date < cutoff_date:
            return solved_dict
        
        timestamp_key = problem_effective_day_kst_date.strftime('%Y-%m-%d')

        if solved_dict.get(timestamp_key) is None:
            solved_dict[timestamp_key] = 1
        else:
            solved_dict[timestamp_key] += 1
            solved_dict['solved_max'] = max(solved_dict['solved_max'], solved_dict[timestamp_key])
            
    solved_dict['solved_max'] = min(solved_dict['solved_max'], 50)

    return solved_dict


def get_starting_day():
    effective_today_kst_date = get_solved_ac_effective_day()

    days_since_effective_sunday = effective_today_kst_date.isoweekday() % 7 
    last_effective_sunday = effective_today_kst_date - datetime.timedelta(days=days_since_effective_sunday)
    seventeen_weeks_ago_sunday = last_effective_sunday - datetime.timedelta(weeks=17)
    
    return effective_today_kst_date.strftime('%Y-%m-%d'), seventeen_weeks_ago_sunday.strftime('%Y-%m-%d')


def get_tomorrow(timestamp):
    # timestamp로부터 하루 뒤의 날짜를 반환
    timedata = datetime.datetime.strptime(timestamp, '%Y-%m-%d')
    tomorrow = timedata + datetime.timedelta(days=1)

    return tomorrow.strftime('%Y-%m-%d')


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
