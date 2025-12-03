import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="나의 체력 & BMI 분석기",
    page_icon="💪",
    layout="wide"
)

# 1. 데이터 로드 함수 (캐싱 적용으로 속도 향상)
@st.cache_data
def load_data():
    try:
        # 업로드해주신 파일명과 동일하게 설정 (같은 폴더에 위치해야 함)
        file_path = "fitness data.xlsx - KS_NFA_FTNESS_MESURE_ITEM_MESUR.csv"
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다. 같은 폴더에 CSV 파일을 넣어주세요.")
        return None

# 2. 메인 화면 구성
st.title("💪 국민체력 데이터 기반 BMI 분석기")
st.markdown("단순 BMI 계산을 넘어, **실제 국민체력 측정 데이터**와 내 수치를 비교해보세요.")

# 사이드바: 사용자 입력
with st.sidebar:
    st.header("📝 정보 입력")
    gender = st.radio("성별", ["남성", "여성"], index=0)
    age = st.number_input("나이 (만)", min_value=10, max_value=100, value=30)
    height = st.number_input("신장 (cm)", min_value=100.0, max_value=250.0, value=170.0)
    weight = st.number_input("체중 (kg)", min_value=30.0, max_value=200.0, value=70.0)
    
    if st.button("결과 확인하기"):
        calc_trigger = True
    else:
        calc_trigger = False

# 3. 로직 처리
if calc_trigger or True: # 기본적으로 화면을 보여주기 위해 True 처리 (버튼 없이도 반응형)
    
    # BMI 계산 (체중kg / 키m^2)
    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 2)
    
    # BMI 판정 기준 (대한비만학회 기준)
    if bmi < 18.5:
        status = "저체중"
        color = "blue"
    elif 18.5 <= bmi < 23:
        status = "정상"
        color = "green"
    elif 23 <= bmi < 25:
        status = "과체중"
        color = "orange"
    else:
        status = "비만"
        color = "red"

    # 결과 표시 영역 (컬럼 분할)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("나의 BMI 결과")
        st.metric(label="BMI 지수", value=bmi, delta=status)
        st.info(f"""
        당신의 BMI는 **{bmi}**이며, 
        판정 결과 **[{status}]**입니다.
        """)

    # 4. 데이터 비교 분석 (데이터가 있을 경우에만)
    df = load_data()
    
    with col2:
        if df is not None:
            st.subheader(f"📊 {age}세 {gender} 평균과의 비교")
            
            # 데이터 필터링 (성별, 연령대)
            # 데이터셋의 성별 코드는 M/F, 입력은 남성/여성 이므로 변환
            gender_code = 'M' if gender == "남성" else 'F'
            
            # 연령대는 ±2세 범위로 넓게 잡아 데이터 확보
            filtered_df = df[
                (df['성별구분코드'] == gender_code) & 
                (df['나이'] >= age - 5) & 
                (df['나이'] <= age + 5)
            ]
            
            if not filtered_df.empty:
                # 데이터 정제 (BMI 결측치 제거)
                filtered_df = filtered_df.dropna(subset=['BMI'])
                
                # 히스토그램 그리기
                fig = px.histogram(
                    filtered_df, 
                    x="BMI", 
                    nbins=30, 
                    title=f"동일 연령대({age-5}~{age+5}세) 체력 측정자들의 BMI 분포",
                    labels={'BMI': 'BMI 수치'},
                    color_discrete_sequence=['#A6C9EC']
                )
                
                # 나의 위치 표시 (수직선)
                fig.add_vline(x=bmi, line_width=3, line_dash="dash", line_color="red")
                fig.add_annotation(x=bmi, y=10, text="나의 위치", showarrow=True, arrowhead=1)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 상위 % 계산
                rank = (filtered_df['BMI'] < bmi).mean() * 100
                st.write(f"데이터 상, 당신의 BMI는 같은 성별/연령대에서 하위 **{rank:.1f}%** (높을수록 체중이 많이 나감)에 위치합니다.")
                
            else:
                st.warning("비교할 수 있는 충분한 데이터가 없습니다.")

st.markdown("---")
st.caption("Data Source: 국민체력100 데이터셋")
