import streamlit as st
from datetime import datetime

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
    st.title("インターン情報自動作成ツール")
    
    # サイドバーにロゴや説明を追加
    st.sidebar.title("About")
    st.sidebar.info(
        "このアプリはインターン情報を自動生成するツールです。\n"
        "必要な情報を入力して、インターン情報を作成しましょう。"
    )
    
    # メインコンテンツ
    col1, col2 = st.columns(2)
    
    with col1:
        company = st.text_input("企業名")
        industry = st.selectbox("業界", INDUSTRIES)
        location = st.text_input("勤務地")
        period = st.selectbox("インターン期間", PERIODS)
        position = st.selectbox("インターン職種", POSITIONS)
        grade = st.selectbox("募集対象", GRADES)
    
    with col2:
        salary = st.selectbox("報酬", SALARIES)
        selection_process = st.selectbox("選考フロー", SELECTION_PROCESS)
        deadline = st.date_input("応募締切日")
        start_date = st.date_input("インターン開始予定日")
        capacity = st.number_input("募集人数", min_value=1, step=1)
        skills = st.text_area("必要なスキル・経験（複数ある場合は改行区切り）")
    
    if st.button("インターン情報を生成"):
        if company and location and skills:
            info = generate_intern_info(
                company, industry, location, period, position, grade,
                salary, selection_process, deadline.strftime("%Y-%m-%d"),
                start_date.strftime("%Y-%m-%d"), str(capacity), skills
            )
            
            st.success("インターン情報が生成されました！")
            
            # 結果を表示
            st.subheader("生成されたインターン情報")
            for k, v in info.items():
                st.write(f"**{k}**: {v}")
        else:
            st.error("必須項目（企業名、勤務地、必要なスキル・経験）を入力してください。")

if __name__ == "__main__":
    main() 