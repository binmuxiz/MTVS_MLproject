import streamlit as st
import json
import plotly.express as px
import json
import plotly.graph_objects as go
import plotly.express as px
import recommendation
import pandas as pd


with open("data/restaurants_info_processed.json", "r", encoding="utf-8") as f:
    restaurant_data = json.load(f)


# 페이지 설정
st.set_page_config(
    page_title="야! 이거 먹어",
    page_icon="🍽️",
    layout="wide"
)



# 제목 및 설명
st.title("🍽️ 야! 이거 먹어!")
st.markdown("<h3 style='color: #C75B7A; font-style: bold;'>메타버스 아카데미 주변 맛집 추천 서비스</h3>", unsafe_allow_html=True)

st.markdown("---")
st.write("식당 방문 정보를 입력하면 추천 음식 카테고리를 알려드립니다!")
st.markdown("---")

# 사이드바에 입력 필드 구성
with st.sidebar:
    st.image("./images/mtvs_logo.png", use_container_width=True)

    st.markdown("""
        <style>
        .space-div {
            margin-top: 40px;
        }
        </style>
        <div class="space-div"></div>
    """, unsafe_allow_html=True)

    # 사이드바 타이틀 스타일링 - 더 눈에 띄게 수정
    st.markdown("""
        <style>
        .sidebar-title {
            background-color: #921A40;
            color: white;
            padding: 7px 15px;
            border-radius: 5px;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        </style>
        <div class="sidebar-title">방문 정보 입력</div>
    """, unsafe_allow_html=True)

    # 1. 이용방법
    # st.subheader("이용방법")
    # 색상이 적용된 subheader
    st.subheader("이용 방법")

    how = st.radio(
        "어떻게 이용하실 예정인가요?",
        ["예약 없이 이용", "예약 후 이용", "포장·배달 이용"],
        index=0
    )
    
    # 2. 이용할 시간대
    st.subheader("이용 시간대")

    time = st.radio(
        "언제 방문하실 예정인가요?",
        ["🌅 아침에 방문", "☀️ 점심에 방문", "🌇 저녁에 방문", "🌃 밤에 방문"],
        index=1  # 디폴트: 점심에 방문
    )
    
    # 3. 웨이팅
    st.subheader("웨이팅")
    
    wait = st.radio(
        "얼마나 기다리실 수 있나요?",
        ["바로 입장", "10분 이내", "30분 이내", "30분 이상", "1시간 이상"],
        index=0
    )

    
    # 4. 방문 목적 (다중 선택)
    st.subheader("방문 목적")
    purpose_options = ["🌹 데이트", "💼 비즈니스", "🏠 가족모임", "✈️ 여행", "🧺 나들이", "🎉 기념일", "🎮 친목", "🍺 회식", "☕ 일상"]
    
    purpose = st.multiselect(
        "방문 목적을 선택해주세요 (복수 선택 가능)",
        purpose_options
    )
    
    # 5. 함께 방문할 사람 (다중 선택)
    st.subheader("함께 방문할 사람")
    with_who_options = ["👶 아이", "👯 친구", "👨‍👩‍👧‍👦 친척・형제", "💑 연인・배우자", "🧘 혼자", "👨‍👩‍👧 부모님", "👥 지인・동료", "기타"]
    
    with_who = st.multiselect(
        "함께 방문할 사람을 선택해주세요 (복수 선택 가능)",
        with_who_options
    )


# 6. 태그 (다중 선택) - 체크박스로 표시

st.header("선호하는 특징")
st.write("선호하는 특징을 선택해주세요 (복수 선택 가능)")

tag_cols = st.columns(2)
tag_options = [
    "음식이 맛있어요", "친절해요", "재료가 신선해요", "양이 많아요", 
    "가성비가 좋아요", "매장이 청결해요", "매장이 넓어요", 
    "특별한 메뉴가 있어요", "고기 질이 좋아요", "인테리어가 멋져요"
]

tags = []
for i, tag in enumerate(tag_options):
    with tag_cols[i % 2]:
        if st.checkbox(tag):
            tags.append(tag)


# 7. 선호하는 특징 텍스트 입력
st.markdown("---")
st.header("오늘의 기분/상황은 어떤가요?")
st.write("자유롭게 입력해주세요! 예: 기분, 날씨, 먹고 싶은 느낌 등")

user_text = st.text_area(
    label="예: 비도 오고 우울해서 따뜻한 국물이 먹고 싶어요 ☔🍜",
    placeholder="지금 기분이나 먹고 싶은 느낌을 자유롭게 적어주세요!",
    height=100
)







# =================================================== 데이터 입력 끝 ===================================================



def prepare_input_data():
    # 이모지 제거 함수
    def remove_emoji(text):
        if text and isinstance(text, str):
            # 이모지와 그 뒤의 공백을 제거 (정규식으로 개선 가능)
            parts = text.split(' ', 1)
            if len(parts) > 1:
                return parts[1]
        return text
    
    # PURPOSE와 WITH_WHO에서 이모지 제거
    clean_purpose = [remove_emoji(item) for item in purpose] if purpose else []
    clean_with_who = [remove_emoji(item) for item in with_who] if with_who else []

    # TIME에서 이모지 제거
    clean_time = remove_emoji(time) if time else None


    data = {
        'how': how if how != "선택 없음" else None,
        'time': clean_time,
        'waiting': wait if wait != "선택 없음" else None,
        'purpose': clean_purpose,
        'with_whom': clean_with_who,
        'tags': tags,
        'text': user_text.strip() if user_text.strip() else "특별히 생각나는 건 없어요"
    }

    return data


# ======================================================= 추천받기 버튼 ================================================================
# 버튼을 감싸는 div에 스타일 지정
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #C75B7A;
        color: white;
        height: 3em;
        width: 100%;
        font-size: 18px;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #7b1736;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)
if st.button("카테고리 추천받기", type="primary"):

    input_data = prepare_input_data()

    with st.spinner('맛집 카테고리를 분석 중입니다... 잠시만 기다려주세요!'):
        import time
        time.sleep(2)
    


    
        # 모델 및 관련 데이터 로드
            
        result = recommendation.recommend_restaurants(
                    time=input_data['time'],
                    how=input_data['how'],
                    waiting=input_data['waiting'],
                    purpose=input_data['purpose'],
                    with_whom=input_data['with_whom'],
                    tags=input_data['tags'],
                    text=input_data['text']
        )



        # 1. 예측된 카테고리 가져오기
        predicted_category = result['prediction']


        # 3. 예측된 카테고리에 해당하는 식당 목록 가져오기
        recommended_restaurants = restaurant_data['restaurants'].get(predicted_category, [])

# ================= 추천 카테고리 =============================
        st.markdown("---")
        st.subheader(f"🍽️ 추천 카테고리: {predicted_category}")

        top3_probs = result['top3_probabilities']

        top_categories = []
        top_probs = []
        colors = ['#921A40', '#D9ABAB', '#F4D9D0']  # 1~3위 색상

        
        for category, prob in top3_probs:
            top_categories.append(category)
            top_probs.append(prob)


        fig = go.Figure()

        # 각 막대를 개별적으로 추가하고 색상 지정
        for i, (category, prob, color) in enumerate(zip(top_categories, top_probs, colors)):
            fig.add_trace(
                go.Bar(
                    x=[category],
                    y=[prob],
                    marker_color=color,
                    text=f"{prob*100:.1f}%",
                    textposition='outside',
                    name=category
                )
            )

        fig.update_layout(
            title='🔍 예측된 카테고리 확률',
            yaxis=dict(range=[0, 1]),
            height=400,
            showlegend=False
        )

        # Streamlit에 출력
        st.plotly_chart(fig, use_container_width=True)




# ================= 추천 식당 =============================


        # if recommended_restaurants:
        #     st.write(f"총 {len(recommended_restaurants)}개의 추천 식당이 있어요!")

        #     # 카드 스타일 CSS 정의
        #     st.markdown("""
        #         <style>
        #             .card-container {
        #                 display: flex;
        #                 flex-wrap: wrap;
        #                 justify-content: flex-start;
        #                 gap: 20px;
        #                 margin-bottom: 30px;
        #             }
        #             .card {
        #                 background-color: #ffffff;
        #                 border-radius: 15px;
        #                 padding: 20px;
        #                 width: 300px;
        #                 box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        #                 transition: transform 0.2s;
        #             }
        #             .card:hover {
        #                 transform: scale(1.02);
        #             }
        #             .card h4 {
        #                 color: #921A40;
        #                 margin-bottom: 10px;
        #                 font-size: 18px;
        #             }
        #             .card p {
        #                 margin: 5px 0;
        #                 color: #444;
        #                 font-size: 15px;
        #             }
        #             .category-tag {
        #                 background-color: #F4D9D0;
        #                 color: #921A40;
        #                 padding: 3px 8px;
        #                 border-radius: 10px;
        #                 font-size: 14px;
        #                 display: inline-block;
        #                 margin-bottom: 8px;
        #             }
        #             .price-tag {
        #                 background-color: #F4D9D0;
        #                 color: #921A40;
        #                 padding: 3px 8px;
        #                 border-radius: 10px;
        #                 font-size: 14px;
        #                 display: inline-block;
        #                 margin-bottom: 8px;
        #                 margin-left: 5px;
        #             }
        #             .menu-section {
        #                 margin-top: 10px;
        #             }
        #             .menu-list {
        #                 list-style-type: disc;
        #                 padding-left: 20px;
        #                 margin-top: 5px;
        #                 margin-bottom: 0;
        #             }
        #             .menu-list li {
        #                 font-size: 14px;
        #                 color: #555;
        #                 margin-bottom: 2px;
        #             }
        #             .category-header {
        #                 background-color: #921A40;
        #                 color: white;
        #                 padding: 10px 15px;
        #                 border-radius: 10px;
        #                 margin-top: 30px;
        #                 margin-bottom: 20px;
        #                 font-size: 18px;
        #                 font-weight: bold;
        #             }
        #         </style>
        #     """, unsafe_allow_html=True)

        #     # 추천 식당 결과 시작 전 안내 메시지
        #     st.markdown("### 🍽️ 추천 식당 리스트")
        #     st.markdown("""
        #     <div style="background-color:#f0f0f5; padding:10px 15px; border-radius:10px; border-left: 6px solid #921A40; margin-bottom: 15px;">
        #         <strong>ℹ️ 식당 이름을 클릭하면 네이버 지도로 이동합니다!</strong>
        #     </div>
        #     """, unsafe_allow_html=True)

        #     # 세부 카테고리별로 식당 그룹화
        #     category_groups = {}
        #     for restaurant in recommended_restaurants:
        #         category = restaurant.get('category', '기타')
        #         if category not in category_groups:
        #             category_groups[category] = []
        #         category_groups[category].append(restaurant)
            
        #     # 카테고리별로 식당 표시
        #     for category, restaurants in category_groups.items():
        #         # 카테고리 제목 표시
        #         st.markdown(f'<div class="category-header">🍲 {category} ({len(restaurants)})</div>', unsafe_allow_html=True)
                
        #         # 이 카테고리에 속한 식당들을 위한 카드 컨테이너 시작
        #         st.markdown('<div class="card-container">', unsafe_allow_html=True)
                
        #         for restaurant in restaurants:
        #             # 주소 표시를 위한 처리 (길이가 너무 길면 줄임)
        #             address = restaurant.get('address', '')
        #             if len(address) > 30:
        #                 address = address[:30] + "..."
                        
        #             # 메뉴 가져오기 및 처리
        #             menu_text = restaurant.get('menu', '')
        #             menu_items = []
                    
        #             if menu_text:
        #                 # 메뉴 항목 분리 (슬래시로 구분된 경우)
        #                 menu_items = [item.strip() for item in menu_text.split('/') if item.strip()]
        #                 # 최대 5개만 표시
        #                 menu_items = menu_items[:5]
                    
        #             # 가격대 가져오기 (없으면 "가격 정보 없음")
        #             price_range = restaurant.get('price_range', '')
        #             price_display = price_range if price_range else "가격 정보 없음"
                    
        #             # 메뉴 항목 HTML 생성
        #             menu_html = ""
        #             if menu_items:
        #                 menu_html = "<div class='menu-section'><strong>🍴 대표 메뉴:</strong><ul class='menu-list'>"
        #                 for item in menu_items:
        #                     menu_html += f"<li>{item}</li>"
        #                 menu_html += "</ul></div>"
                    
        #             st.markdown(f"""
        #                 <div class="card" style="margin-bottom: 20px;">
        #                     <h4 style="margin-bottom: 5px;">
        #                         <a href="{restaurant['link']}" target="_blank" style="text-decoration: none; color: #921A40;">
        #                             {restaurant['name']}
        #                         </a>
        #                     </h4>
        #                     <div>
        #                         <span class="price-tag">{price_display}</span>
        #                     </div>
        #                     <p style="font-size: 14px; color: #666; margin-top: 8px;">
        #                         📍 {address}
        #                     </p>
        #                     {menu_html}
        #                 </div>
        #             """, unsafe_allow_html=True)
                
        #         # 카드 컨테이너 종료
        #         st.markdown('</div>', unsafe_allow_html=True)

        # else:
        #     st.warning("추천된 카테고리에 해당하는 식당 정보를 찾을 수 없습니다.")


        if recommended_restaurants:
            st.write(f"총 {len(recommended_restaurants)}개의 추천 식당이 있어요!")

            # 카드 스타일 CSS 정의
            st.markdown("""
                <style>
                    .card-container {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: flex-start;
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    .card {
                        background-color: #ffffff;
                        border-radius: 15px;
                        padding: 20px;
                        width: 100%;
                        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                        transition: transform 0.2s;
                        display: flex;
                        flex-direction: row;
                    }
                    .card:hover {
                        transform: scale(1.01);
                    }
                    .card-left {
                        width: 40%;
                        padding-right: 20px;
                        border-right: 1px dashed #e0e0e0;
                    }
                    .card-right {
                        width: 60%;
                        padding-left: 20px;
                    }
                    .card h4 {
                        color: #921A40;
                        margin-bottom: 10px;
                        font-size: 18px;
                    }
                    .card p {
                        margin: 5px 0;
                        color: #444;
                        font-size: 15px;
                    }
                    .price-tag {
                        background-color: #F4D9D0;
                        color: #921A40;
                        padding: 3px 8px;
                        border-radius: 10px;
                        font-size: 14px;
                        display: inline-block;
                        margin-bottom: 15px;
                        margin-top: 5px;
                    }
                    .address {
                        margin-top: 10px;
                        font-size: 14px;
                        color: #666;
                    }
                    .menu-title {
                        font-weight: bold;
                        margin-bottom: 10px;
                        color: #333;
                    }
                    .menu-list {
                        list-style-type: disc;
                        padding-left: 20px;
                        margin-top: 5px;
                        margin-bottom: 0;
                    }
                    .menu-list li {
                        font-size: 14px;
                        color: #555;
                        margin-bottom: 2px;
                    }
                    .category-header {
                        background-color: #921A40;
                        color: white;
                        padding: 10px 15px;
                        border-radius: 10px;
                        margin-top: 30px;
                        margin-bottom: 20px;
                        font-size: 18px;
                        font-weight: bold;
                    }
                    
                    @media (max-width: 768px) {
                        .card {
                            flex-direction: column;
                        }
                        .card-left, .card-right {
                            width: 100%;
                            padding: 0;
                            border-right: none;
                        }
                        .card-left {
                            margin-bottom: 15px;
                            border-bottom: 1px dashed #e0e0e0;
                            padding-bottom: 15px;
                        }
                    }
                </style>
            """, unsafe_allow_html=True)

            # 추천 식당 결과 시작 전 안내 메시지
            st.markdown("### 🍽️ 추천 식당 리스트")
            st.markdown("""
            <div style="background-color:#f0f0f5; padding:10px 15px; border-radius:10px; border-left: 6px solid #921A40; margin-bottom: 15px;">
                <strong>ℹ️ 식당 이름을 클릭하면 네이버 지도로 이동합니다!</strong>
            </div>
            """, unsafe_allow_html=True)

            # 세부 카테고리별로 식당 그룹화
            category_groups = {}
            for restaurant in recommended_restaurants:
                category = restaurant.get('category', '기타')
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(restaurant)
            
            # 카테고리별로 식당 표시
            for category, restaurants in category_groups.items():
                # 카테고리 제목 표시
                st.markdown(f'<div class="category-header">🍲 {category} ({len(restaurants)})</div>', unsafe_allow_html=True)
                
                # 이 카테고리에 속한 식당들을 위한 카드 컨테이너 시작
                st.markdown('<div class="card-container">', unsafe_allow_html=True)
                
                for restaurant in restaurants:
                    # 주소 정보
                    address = restaurant.get('address', '')
                    
                    # 메뉴 가져오기 및 처리
                    menu_text = restaurant.get('menu', '')
                    menu_items = []
                    
                    if menu_text:
                        # 메뉴 항목 분리 (슬래시로 구분된 경우)
                        menu_items = [item.strip() for item in menu_text.split('/') if item.strip()]
                        # 최대 5개만 표시
                        menu_items = menu_items[:5]
                    
                    # 가격대 가져오기 (없으면 "가격 정보 없음")
                    price_range = restaurant.get('price_range', '')
                    price_display = price_range if price_range else "가격 정보 없음"
                    
                    # 메뉴 항목 HTML 생성
                    menu_html = ""
                    if menu_items:
                        menu_html = "<div class='menu-title'>🍴 대표 메뉴:</div><ul class='menu-list'>"
                        for item in menu_items:
                            menu_html += f"<li>{item}</li>"
                        menu_html += "</ul>"
                    else:
                        menu_html = "<div class='menu-title'>🍴 메뉴 정보가 없습니다</div>"
                    
                    st.markdown(f"""
                        <div class="card" style="margin-bottom: 20px;">
                            <div class="card-left">
                                <h4>
                                    <a href="{restaurant['link']}" target="_blank" style="text-decoration: none; color: #921A40;">
                                        {restaurant['name']}
                                    </a>
                                </h4>
                                <div>
                                    <span class="price-tag">{price_display}</span>
                                </div>
                                <p class="address">
                                    📍 {address}
                                </p>
                            </div>
                            <div class="card-right">
                                {menu_html}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # 카드 컨테이너 종료
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.warning("추천된 카테고리에 해당하는 식당 정보를 찾을 수 없습니다.")
# 푸터
st.markdown("---")
st.caption("© 2025 메타버스 아카데미 AI 맛집 추천 시스템")