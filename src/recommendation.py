import joblib
import pandas as pd
from mecab import MeCab
import warnings  # ✅ 추가

warnings.filterwarnings("ignore", category=UserWarning)  # ✅ 경고 무시 설정

mecab = MeCab()

# ✅ 전처리기 및 모델 로드 (애플리케이션 시작 시 1회만 실행)
model_path = 'models/tuned_voting_model.joblib'
preprocessor_path = 'models/preprocessor.joblib'

try:
    loaded_model = joblib.load(model_path)
    loaded_preprocessor = joblib.load(preprocessor_path)
except Exception as e:
    print(f"[초기 로딩 오류] 모델 또는 전처리기 불러오기 실패: {e}")



def stem_processing(text):
    if not isinstance(text, str) or not text.strip(): return ""
    try:
        pos_data = mecab.pos(text)
        result = []
        target_tags = {'NNG', 'NNP'}
        for word, tag in pos_data:
            if tag in target_tags:
                result.append(word)
            elif tag == 'VA':
                processed_word = word + "다"
                result.append(processed_word)
        return " ".join(result)
    except Exception as e:
        return ""
    
def recommend_restaurants(
            time,
            how,
            waiting,
            purpose,
            with_whom,
            tags,
            text=" "
            ):
               
# ============================ == 입력 데이터 인코딩 및 전처리 =================================


    features = pd.DataFrame({

        'TIME_밤에 방문': [1 if time == '밤에 방문' else 0],
        'TIME_아침에 방문': [1 if time == '아침에 방문' else 0],
        'TIME_저녁에 방문': [1 if time == '저녁에 방문' else 0],
        'TIME_점심에 방문': [1 if time == '점심에 방문' else 0],

        'HOW_예약 없이 이용': [1 if how == '예약 없이 이용' else 0],
        'HOW_예약 후 이용': [1 if how == '예약 후 이용' else 0],
        'HOW_포장·배달 이용': [1 if how == '포장·배달 이용' else 0],

    })
    
    # WAIT 인코딩
    wait_mapping = {
        '바로 입장': 0.0,
        '10분 이내': 0.2,
        '30분 이내': 0.5,
        '30분 이상': 0.7,
        '1시간 이상': 1.0,
    }
    features['WAIT_encoded'] = wait_mapping.get(waiting, 0.0)
            

    # PURPOSE 인코딩
    for item in ['데이트', '비즈니스', '가족모임', '여행', '나들이', '기념일', '친목', '회식', '일상']:
        features[f'PURPOSE_{item}'] = 1 if item in purpose else 0
            
    # WITH_WHOM 인코딩
    for item in ['아이', '친구', '친척・형제', '연인・배우자', '혼자', '기타', '부모님', '지인・동료']:
        features[f'WITH_WHOM_{item}'] = 1 if item in with_whom else 0
            
    # TAGS 인코딩
    tag_options = [
        "음식이 맛있어요", "친절해요", "재료가 신선해요", "양이 많아요", 
        "가성비가 좋아요", "매장이 청결해요", "매장이 넓어요", 
        "특별한 메뉴가 있어요", "고기 질이 좋아요", "인테리어가 멋져요"
    ]
    
    for tag in tag_options:
        features[tag] = 1 if tag in tags else 0

    # 텍스트 
    features['PROCESSED_REVIEW'] = stem_processing(text)

    

    print(f"\n예측할 원본 리뷰: {text}")
    print(f"예측용 입력 데이터 (DataFrame):\n{features}") # 필요시 주석 해제


# ======================================= 모델 예측 ===========================================
    # 로드할 파일명

    results = []
    

    try:

    # 1. 로드된 전처리기를 사용하여 데이터 변환
        new_data_processed = loaded_preprocessor.transform(features)
        print(f"\n전처리된 데이터 형태: {new_data_processed.shape}")


        # 전처리된 결과의 컬럼명을 기존 전처기에서 추출 (전처기 안에 컬럼 이름이 있는 경우)
        # processed_df = pd.DataFrame(new_data_processed, columns=loaded_preprocessor.get_feature_names_out())


    # 2. 로드된 모델을 사용하여 예측 수행
        new_prediction = loaded_model.predict(new_data_processed)[0] # 단일 결과 추출
        new_probabilities = loaded_model.predict_proba(new_data_processed)[0] # 단일 결과 확률 추출


        print("\n--- 예측 결과 ---")
        print(f"예측된 카테고리: {new_prediction}")

        print("\n예측 확률 (상위 3개):")
        proba_list = sorted(zip(loaded_model.classes_, new_probabilities), key=lambda item: item[1], reverse=True)
        for i, (category, prob) in enumerate(proba_list[:3]):
            print(f"  {i+1}. {category}: {prob:.4f}")

        print("\n--- 로드 및 단일 예측 예시 완료 ---")

        results = {
            'prediction': new_prediction,
            'top3_probabilities': proba_list[:3]  # [('카테고리', 확률), ...]
        }



    except FileNotFoundError as e:
        print(f"오류: 저장된 파일을 찾을 수 없습니다. '{e.filename}' 경로를 확인하세요.")
    except NameError as e:
        print(f"오류: 필요한 변수(feature_columns, stem_processing 등)가 정의되지 않았습니다. 이전 셀 실행을 확인하세요. 오류: {e}")
    except Exception as e:
        print(f"파일 로드 또는 예측 중 오류 발생: {e}")



    return results
