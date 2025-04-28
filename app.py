import streamlit as st
from datetime import datetime
from notion_client import Client
import os
from dotenv import load_dotenv

# デバッグ情報の表示
st.write("デバッグ情報:")
st.write(f"NOTION_TOKEN exists: {'NOTION_TOKEN' in st.secrets}")
st.write(f"NOTION_DATABASE_ID exists: {'NOTION_DATABASE_ID' in st.secrets}")

# ローカル開発環境用の設定
if os.path.exists(".env"):
    load_dotenv()
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
else:
    # Streamlit Cloud用の設定
    NOTION_TOKEN = st.secrets.get("NOTION_TOKEN")
    NOTION_DATABASE_ID = st.secrets.get("NOTION_DATABASE_ID")

# デバッグ情報の表示
st.write(f"NOTION_TOKEN value: {NOTION_TOKEN is not None}")
st.write(f"NOTION_DATABASE_ID value: {NOTION_DATABASE_ID is not None}")

# Notionクライアントの初期化
def get_notion_client():
    if NOTION_TOKEN:
        try:
            client = Client(auth=NOTION_TOKEN)
            st.write("Notionクライアントの初期化に成功しました")
            return client
        except Exception as e:
            st.error(f"Notionクライアントの初期化に失敗しました: {str(e)}")
            return None
    return None

# グローバル変数としてnotionクライアントを初期化
notion = get_notion_client()

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

def create_notion_page(info):
    """Notionに新しいページを作成する"""
    try:
        st.write("デバッグ: create_notion_page関数が呼び出されました")
        
        if not NOTION_TOKEN or not NOTION_DATABASE_ID:
            st.error("⚠️ Notionの設定が完了していません。Streamlit SecretsにNOTION_TOKENとNOTION_DATABASE_IDを設定してください。")
            return None
            
        if not notion:
            st.error("⚠️ Notionクライアントの初期化に失敗しました。")
            return None
            
        st.write("デバッグ: シークレットとクライアントのチェックを通過しました")
        
        # データベースIDをシークレットから取得
        database_id = NOTION_DATABASE_ID
        
        # ページのプロパティを設定
        properties = {
            "インターン名": {"title": [{"text": {"content": info["インターン名"]}}]},
            "企業名": {"rich_text": [{"text": {"content": info["企業名"]}}]},
            "業界": {"select": {"name": info["業界"]}},
            "勤務地": {"rich_text": [{"text": {"content": info["勤務地"]}}]},
            "期間": {"select": {"name": info["期間"]}},
            "職種": {"select": {"name": info["職種"]}},
            "募集対象": {"select": {"name": info["募集対象"]}},
            "報酬": {"select": {"name": info["報酬"]}},
            "応募締切": {"date": {"start": info["応募締切"]}},
            "開始予定日": {"date": {"start": info["開始予定日"]}},
            "募集人数": {"number": int(info["募集人数"])}
        }
        
        st.write("デバッグ: プロパティの設定が完了しました")
        
        # ページのコンテンツを設定
        children = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": info["インターン名"]}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": info["説明"]}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "選考フロー"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": info["選考フロー"]}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "必要なスキル・経験"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": info["必要なスキル・経験"]}}]
                }
            }
        ]
        
        st.write("デバッグ: コンテンツの設定が完了しました")
        
        # ページを作成
        st.write("デバッグ: ページの作成を開始します")
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            children=children
        )
        
        st.write("デバッグ: ページの作成が完了しました")
        return new_page["url"]
    except Exception as e:
        st.error(f"Notionへの投稿に失敗しました: {str(e)}")
        st.write(f"デバッグ: エラーの詳細: {str(e)}")
        return None

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
    if st.button("インターン情報を生成", key="generate_button"):
        if company and location and skills:
            info = generate_intern_info(
                company, industry, location, period, position, grade,
                salary, selection_process, deadline.strftime("%Y-%m-%d"),
                start_date.strftime("%Y-%m-%d"), str(capacity), skills
            )
            
            st.success("🎉 インターン情報が生成されました！")
            
            # Notionに投稿するかどうかを選択
            if st.checkbox("Notionに投稿する"):
                st.write("デバッグ: Notionに投稿するが選択されました")
                if not NOTION_TOKEN or not NOTION_DATABASE_ID:
                    st.error("⚠️ Notionの設定が完了していません。Streamlit SecretsにNOTION_TOKENとNOTION_DATABASE_IDを設定してください。")
                    st.write(f"NOTION_TOKEN: {NOTION_TOKEN is not None}")
                    st.write(f"NOTION_DATABASE_ID: {NOTION_DATABASE_ID is not None}")
                elif not notion:
                    st.error("⚠️ Notionクライアントの初期化に失敗しました。")
                else:
                    st.write("デバッグ: Notionページの作成を開始します")
                    page_url = create_notion_page(info)
                    if page_url:
                        st.success(f"✅ Notionに投稿しました！ [ページを開く]({page_url})")
                    else:
                        st.error("⚠️ Notionページの作成に失敗しました")
            
            # 結果を表示
            st.markdown("### 生成されたインターン情報")
            for k, v in info.items():
                st.markdown(f"""
                <div style='background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                    <strong style='color: #2c3e50;'>{k}:</strong>
                    <p style='color: #34495e; margin-top: 5px;'>{v}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("⚠️ 必須項目（企業名、勤務地、必要なスキル・経験）を入力してください。")

if __name__ == "__main__":
    main() 