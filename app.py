import streamlit as st
from datetime import datetime
import pyperclip

# ページ設定
st.set_page_config(
    page_title="インターン情報生成ツール",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSSの追加
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .stSelectbox>div>div>select {
        border-radius: 10px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 10px;
    }
    .stDateInput>div>div>input {
        border-radius: 10px;
    }
    .stNumberInput>div>div>input {
        border-radius: 10px;
    }
    .css-1d391kg {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .css-1v0mbdj {
        margin-bottom: 20px;
    }
    .stAlert {
        border-radius: 10px;
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-radius: 10px;
        padding: 10px;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 選択肢の定義
INDUSTRIES = [
    "IT・テクノロジー",
    "金融・保険",
    "製造・メーカー",
    "商社・流通",
    "サービス",
    "広告・マーケティング",
    "コンサルティング",
    "メディア・エンターテインメント",
    "小売・流通",
    "不動産・建設",
    "医療・ヘルスケア",
    "教育",
    "エネルギー・資源",
    "運輸・物流",
    "その他"
]

PERIODS = [
    "1日",
    "2日",
    "3日",
    "1週間",
    "2週間",
    "3週間",
    "1ヶ月",
    "2ヶ月",
    "3ヶ月",
    "夏季（7-8月）",
    "冬季（12-1月）",
    "春季（3-4月）",
    "通年",
    "その他"
]

POSITIONS = [
    "エンジニア",
    "デザイナー",
    "マーケティング",
    "営業",
    "企画",
    "人事",
    "経理・財務",
    "法務",
    "その他"
]

GRADES = [
    "大学1年生",
    "大学2年生",
    "大学3年生",
    "大学4年生",
    "大学院1年生",
    "大学院2年生",
    "その他"
]

SALARIES = [
    "無給",
    "時給1,000円",
    "時給1,500円",
    "時給2,000円",
    "日給10,000円",
    "日給15,000円",
    "その他"
]

SELECTION_PROCESS = [
    "書類選考 → 面接",
    "書類選考 → グループディスカッション → 面接",
    "書類選考 → 筆記試験 → 面接",
    "書類選考 → グループワーク → 面接",
    "その他"
]

def generate_intern_info(company, industry, location, period, position, grade, salary, 
                        selection_process, deadline, start_date, capacity, skills):
    intern_name = f"{company} {position}インターンシップ ({period})"
    description = f"""
{company}（業界: {industry}）が{location}で開催する{period}の{position}インターンシップです。
募集対象: {grade}
報酬: {salary}
募集人数: {capacity}名
応募締切: {deadline}
開始予定日: {start_date}

【選考フロー】
{selection_process}

【必要なスキル・経験】
{skills}

実務体験や社員交流を通じて、{industry}業界の理解を深めることができます。
"""
    return {
        "インターン名": intern_name,
        "説明": description,
        "期間": period,
        "企業名": company,
        "業界": industry,
        "勤務地": location,
        "職種": position,
        "募集対象": grade,
        "報酬": salary,
        "選考フロー": selection_process,
        "応募締切": deadline,
        "開始予定日": start_date,
        "募集人数": capacity,
        "必要なスキル・経験": skills
    }

def main():
    # ヘッダー
    st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1 style='color: #2c3e50;'>インターン情報自動作成ツール</h1>
        <p style='color: #7f8c8d;'>必要な情報を入力して、インターン情報を作成しましょう</p>
    </div>
    """, unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center;'>
            <h2 style='color: #2c3e50;'>About</h2>
            <p style='color: #7f8c8d;'>このアプリはインターン情報を自動生成するツールです。</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("""
        💡 **使い方**
        1. 各項目を入力・選択
        2. 「インターン情報を生成」ボタンをクリック
        3. 生成された情報を確認
        4. 「全てをコピー」ボタンで情報をコピー
        """)
    
    # メインコンテンツ
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 基本情報")
        company = st.text_input("企業名", placeholder="例: 株式会社〇〇")
        industry = st.selectbox("業界", INDUSTRIES)
        location = st.text_input("勤務地", placeholder="例: 東京都渋谷区")
        period = st.selectbox("インターン期間", PERIODS)
        position = st.selectbox("インターン職種", POSITIONS)
        grade = st.selectbox("募集対象", GRADES)
    
    with col2:
        st.markdown("### 詳細情報")
        salary = st.selectbox("報酬", SALARIES)
        selection_process = st.selectbox("選考フロー", SELECTION_PROCESS)
        deadline = st.date_input("応募締切日")
        start_date = st.date_input("インターン開始予定日")
        capacity = st.number_input("募集人数", min_value=1, step=1)
        skills = st.text_area("必要なスキル・経験", placeholder="例:\n- Python\n- コミュニケーション能力\n- チームワーク", height=100)
    
    # 生成ボタン
    if st.button("インターン情報を生成"):
        if company and location and skills:
            info = generate_intern_info(
                company, industry, location, period, position, grade,
                salary, selection_process, deadline.strftime("%Y-%m-%d"),
                start_date.strftime("%Y-%m-%d"), str(capacity), skills
            )
            
            st.success("🎉 インターン情報が生成されました！")
            
            # 結果を表示
            st.markdown("### 生成されたインターン情報")
            for k, v in info.items():
                st.markdown(f"""
                <div style='background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <strong style='color: #2c3e50;'>{k}:</strong>
                    <p style='color: #34495e; margin-top: 5px;'>{v}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # コピーボタン
            if st.button("全てをコピー"):
                # 情報を整形してコピー
                copy_text = f"""【{info['インターン名']}】

{info['説明']}

【詳細情報】
・企業名: {info['企業名']}
・業界: {info['業界']}
・勤務地: {info['勤務地']}
・期間: {info['期間']}
・職種: {info['職種']}
・募集対象: {info['募集対象']}
・報酬: {info['報酬']}
・選考フロー: {info['選考フロー']}
・応募締切: {info['応募締切']}
・開始予定日: {info['開始予定日']}
・募集人数: {info['募集人数']}名
・必要なスキル・経験:
{info['必要なスキル・経験']}"""
                
                pyperclip.copy(copy_text)
                st.success("✅ クリップボードにコピーしました！")
        else:
            st.error("⚠️ 必須項目（企業名、勤務地、必要なスキル・経験）を入力してください。")

if __name__ == "__main__":
    main() 