from typing import Optional
from fastapi import FastAPI, Response
from httpx import AsyncClient

from utils import create_solved_dict, boj_rating_to_lv, get_starting_day, get_tomorrow, get_tier_name
from randoms import random_user, random_timestamp
import mapping

app = FastAPI()

# SVG 전체 크기
SVG_WIDTH = 350
SVG_HEIGHT = 170
SVG_VIEWBOX = f"0 0 {SVG_WIDTH} {SVG_HEIGHT}"

# 배경 사각형 크기 및 둥근 모서리
BG_RECT_WIDTH = 349
BG_RECT_HEIGHT = 169
BG_RECT_RADIUS = 14
BG_RECT_STROKE_WIDTH = 0.5

# 핸들 텍스트 위치 및 크기, 애니메이션 딜레이
HANDLE_X = 23
HANDLE_Y = 32
HANDLE_FONT_SIZE = 14
HANDLE_ANIM_DELAY = 100

# 티어 텍스트 위치 및 크기, 애니메이션 딜레이
TIER_X = 327
TIER_Y = 32
TIER_FONT_SIZE = 12
TIER_ANIM_DELAY = 300

# 잔디 사각형 (heatmap boxes) 크기 및 둥근 모서리
ZANDI_RECT_SIZE = 15
ZANDI_RECT_RADIUS = 4

# 잔디 사각형 시작 위치 (기준점)
ZANDI_START_X = 23
ZANDI_START_Y = 44

# 잔디 사각형 레이아웃 간격
ZANDI_COLUMNS = 7 # 한 주에 7일 (세로 줄 수)
ZANDI_X_SPACING = 17 # 각 잔디 사각형의 가로 간격 (너비 포함)
ZANDI_Y_SPACING = 16 # 각 잔디 사각형의 세로 간격 (높이 포함)

# 잔디 사각형 애니메이션 딜레이
ZANDI_BASE_ANIM_DELAY = 500
ZANDI_ROW_ANIM_INCREMENT = 50 # 세로줄 (요일)별 딜레이 증가
ZANDI_BOX_ANIM_INCREMENT = 4 # 개별 박스별 추가 딜레이

def make_heatmap_svg(handle: str, tier: str, solved_dict: dict, color_theme: dict):
    tier_name = tier.split(' ')[0]
    solved_max = solved_dict['solved_max'] if 'solved_max' in solved_dict else 0

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="{SVG_VIEWBOX}">
        <style type="text/css">
            <![CDATA[
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=block');
                @keyframes fadeIn {{
                    0% {{ opacity: 0; }}
                    40% {{ opacity: 0; }}
                    100% {{ opacity: 1; }}
                }}
                .zandi {{
                    opacity: 0;
                    animation: fadeIn 0.5s ease-in-out forwards;
                }}
                #handle {{
                    opacity: 0;
                    animation: fadeIn 0.5s ease-in-out forwards;
                }}
                #tier {{
                    opacity: 0;
                    animation: fadeIn 0.5s ease-in-out forwards;
                }}
            ]]>
        </style>
        <defs>
            <clipPath id="clip-Gold_-_1">
            <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}"/>
            </clipPath>
        </defs>
        <g id="zandies">
            <rect id="background" width="{BG_RECT_WIDTH}" height="{BG_RECT_HEIGHT}" rx="{BG_RECT_RADIUS}" fill="{color_theme['background']}" style="stroke-width:{BG_RECT_STROKE_WIDTH}; stroke:{color_theme['border']};"/>
            <text id="handle" transform="translate({HANDLE_X} {HANDLE_Y})" fill="{color_theme[tier_name][5]}" font-size="{HANDLE_FONT_SIZE}" font-family="NotoSansKR-Black, Noto Sans KR" font-weight="800" style="animation-delay:{HANDLE_ANIM_DELAY}ms">{handle}</text>
            <text id="tier" transform="translate({TIER_X} {TIER_Y})" fill="{color_theme[tier_name][5]}" font-size="{TIER_FONT_SIZE}" font-family="NotoSansKR-Black, Noto Sans KR" font-weight="800" text-anchor="end" style="animation-delay:{TIER_ANIM_DELAY}ms">{tier}</text>
    """

    idx = 0
    today, now_in_loop = get_starting_day()

    while True:
        # solved.ac streak specs:
        # n := clamp (solved_max) to [4, 50]
        # [0, 0], [1, 0.1n), [0.1n, 0.3n), [0.3n, 0.6n), [0.6n, 1.0n] -- all values are rounded up
        solved_count = solved_dict.get(now_in_loop, 0)

        # 색상 임계값들을 미리 계산하여 조건문에서 재사용
        # solved.ac의 소수점 올림 방식 ((값 * 비율 + 9) // 10)을 유지
        threshold_10_percent = (solved_max * 1 + 9) // 10
        threshold_30_percent = (solved_max * 3 + 9) // 10
        threshold_60_percent = (solved_max * 6 + 9) // 10

        if solved_count == 0:
            color = color_theme[tier_name][0] # 해결 문제 0개 (가장 밝은 색상)
        elif solved_count >= threshold_60_percent:
            color = color_theme[tier_name][4] # 상위 40% 이상 (가장 진한 색상)
        elif solved_count >= threshold_30_percent:
            color = color_theme[tier_name][3] # 상위 70% 이상 (중간보다 진한 색상)
        elif solved_count >= threshold_10_percent and solved_count > 1:
            color = color_theme[tier_name][2] # 상위 90% 이상 (단, 1문제 초과)
        else:
            color = color_theme[tier_name][1] # 그 외 (1문제 이하 또는 1문제이지만 10% 미만)
        
        nemo = f"""
        <rect class="zandi"
                width="{ZANDI_RECT_SIZE}" height="{ZANDI_RECT_SIZE}" rx="{ZANDI_RECT_RADIUS}"
                transform="translate({ZANDI_START_X + (idx // ZANDI_COLUMNS) * ZANDI_X_SPACING} {ZANDI_START_Y + (idx % ZANDI_COLUMNS) * ZANDI_Y_SPACING})" 
                fill="{color}"
                style="animation-delay:{ZANDI_BASE_ANIM_DELAY + (idx % ZANDI_COLUMNS) * ZANDI_ROW_ANIM_INCREMENT + idx * ZANDI_BOX_ANIM_INCREMENT}ms"/>
        """
        svg += nemo
        idx += 1

        if now_in_loop == today:
            break
        now_in_loop = get_tomorrow(now_in_loop)
    
    svg += """
        </g>
    </svg>
    """
    return svg


@app.get("/api")
async def generate_badge(handle: str, theme: Optional[str] = "warm"):
    api = 'https://solved.ac/api/v3/user'
    user_info_url = api + '/show?handle=' + handle
    timestamp_url = api + '/history?handle=' + handle + '&topic=solvedCount'
    solved_dict = {}
    # 테마 색상표 (기본값: WARM)
    theme = theme if theme.upper() in mapping.THEMES else 'warm'
    color_theme = mapping.THEMES[theme.upper()]
    
    async with AsyncClient() as client:
        user_info = await client.get(user_info_url)
        timestamp = await client.get(timestamp_url)
        
    if user_info.status_code == 200 and timestamp.status_code == 200:
        user_info = user_info.json()
        timestamp = timestamp.json()
        
        print(timestamp)
        solved_dict = create_solved_dict(timestamp)
        
        rating = user_info['rating']
        tier = mapping.TIERS[boj_rating_to_lv(rating)]
    else:
        user_info = {'handle': handle, 'rating': 0, 'solved': 0}
        tier = 'Unknown'
    
    svg = make_heatmap_svg(handle, tier, solved_dict, color_theme)
    
    response = Response(content=svg, media_type='image/svg+xml')
    response.headers['Cache-Control'] = 'no-cache'
    
    return response


@app.get("/api/random")
async def generate_random_badge(
    tier: Optional[str] = None,
    theme: Optional[str] = "warm"):
    user = random_user(tier)
    handle = user['handle']
    solved_dict = create_solved_dict(random_timestamp())
    theme = theme if theme.upper() in mapping.THEMES else 'warm'
    color_theme = mapping.THEMES[theme.upper()]

    svg = make_heatmap_svg(handle, get_tier_name(user['tier']), solved_dict, color_theme)

    response = Response(content=svg, media_type='image/svg+xml')
    response.headers['Cache-Control'] = 'no-cache'

    return response
