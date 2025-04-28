import streamlit as st
from datetime import datetime, time
import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import pickle
import base64
from email.mime.text import MIMEText
from notion_client import Client

# .envファイルから環境変数を読み込む
load_dotenv()

# Notionクライアントの初期化
notion = Client(auth=os.getenv("NOTION_TOKEN"))

# ページ設定
st.set_page_config(
    page_title="インターン情報自動作成ツール",
    page_icon="🎓",
    layout="wide"
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

WORK_TYPES = [
    "対面",
    "オンライン",
    "ハイブリッド"
]

# 24時間（30分単位）の時間リストを生成
def generate_time_list():
    times = []
    for hour in range(24):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            times.append(time_str)
    return times

TIMES = generate_time_list()

WORKING_DAYS = [
    "週1日",
    "週2日",
    "週3日",
    "週4日",
    "週5日",
    "週1日〜",
    "週2日〜",
    "週3日〜",
    "週4日〜",
    "週5日〜",
    "その他"
]

TRANSPORTATION_FEES = [
    "支給なし",
    "一部支給",
    "全額支給",
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

# Gmail APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    """Gmail APIサービスを取得する関数"""
    creds = None
    # トークンファイルから認証情報を読み込む
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # 認証情報が無効な場合は更新
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Streamlit Secretsから認証情報を取得
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": st.secrets["GOOGLE_CLIENT_ID"],
                        "client_secret": st.secrets["GOOGLE_CLIENT_SECRET"],
                        "redirect_uris": [st.secrets["GOOGLE_REDIRECT_URI"]],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                scopes=SCOPES
            )
            # 認証URLを生成
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            # 認証が必要な場合は、サイドバーに表示
            with st.sidebar:
                st.warning("⚠️ メール送信機能を使用するには認証が必要です")
                st.markdown(f"[認証リンク]({auth_url})")
                code = st.text_input("認証コードを入力してください：")
            
            if code:
                # 認証コードを使用してトークンを取得
                flow.fetch_token(code=code)
                creds = flow.credentials
                
                # 認証情報を保存
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
                st.sidebar.success("✅ 認証が完了しました！")
            else:
                return None
    
    return build('gmail', 'v1', credentials=creds)

def send_email(to_email, subject, body):
    """メールを送信する関数"""
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return True, "メールが正常に送信されました"
    except Exception as e:
        return False, f"メールの送信に失敗しました: {str(e)}"

def generate_intern_info(company, industry, work_type, location, nearest_station, period, position, grade, salary, 
                        transportation_fee, start_time, end_time, working_days, working_time_per_week, skills, required_skills,
                        selection_process, deadline, start_date, capacity):
    intern_name = f"{company} {position}インターンシップ"
    working_hours = f"{start_time}〜{end_time}" if start_time != "フレックス制" and end_time != "フレックス制" else "フレックス制"
    description = f"""
【募集要項】
### 募集職種
{position}

### 雇用形態
アルバイト

### 給与
{salary}

### 交通費
{transportation_fee}

### 勤務地
{location}

### 最寄り駅
{nearest_station}

### 勤務可能時間
{working_hours}

### 勤務日数
{working_days}

### 勤務時間
{working_time_per_week}

### 勤務期間
{period}

### 業界
{industry}

### 業種
{position}

### 形式
{work_type}

### 勤務時間
・期間：{start_date}〜{period}以上勤務できる方
・稼働時間：{working_time_per_week}以上勤務できる方
・勤務時間：{working_hours}内（土日祝日を除く）

### 応募条件
・{grade}大歓迎！

### 必須スキル
{required_skills}

### 歓迎スキル
{skills}

### 選考フロー
{selection_process}

### 応募締切
{deadline}

### 募集人数
{capacity}名
"""
    return {
        "インターン名": intern_name,
        "説明": description,
        "期間": period,
        "企業名": company,
        "業界": industry,
        "形式": work_type,
        "勤務地": location,
        "最寄り駅": nearest_station,
        "職種": position,
        "募集対象": grade,
        "報酬": salary,
        "交通費": transportation_fee,
        "勤務可能時間": working_hours,
        "勤務日数": working_days,
        "勤務時間": working_time_per_week,
        "選考フロー": selection_process,
        "応募締切": deadline,
        "開始予定日": start_date,
        "募集人数": capacity,
        "必須スキル": required_skills,
        "歓迎スキル": skills
    }

def create_notion_page(info):
    """Notionにページを作成する関数"""
    try:
        # ページのプロパティを設定
        properties = {
            "インターン名": {"title": [{"text": {"content": info["インターン名"]}}]},
            "企業名": {"rich_text": [{"text": {"content": info["企業名"]}}]},
            "業界": {"select": {"name": info["業界"]}},
            "形式": {"select": {"name": info["形式"]}},
            "勤務地": {"rich_text": [{"text": {"content": info["勤務地"]}}]},
            "最寄り駅": {"rich_text": [{"text": {"content": info["最寄り駅"]}}]},
            "期間": {"select": {"name": info["期間"]}},
            "職種": {"select": {"name": info["職種"]}},
            "募集対象": {"rich_text": [{"text": {"content": info["募集対象"]}}]},
            "報酬": {"rich_text": [{"text": {"content": info["報酬"]}}]},
            "交通費": {"rich_text": [{"text": {"content": info["交通費"]}}]},
            "勤務可能時間": {"rich_text": [{"text": {"content": info["勤務可能時間"]}}]},
            "勤務日数": {"rich_text": [{"text": {"content": info["勤務日数"]}}]},
            "勤務時間": {"rich_text": [{"text": {"content": info["勤務時間"]}}]},
            "選考フロー": {"rich_text": [{"text": {"content": info["選考フロー"]}}]},
            "応募締切": {"date": {"start": info["応募締切"]}},
            "開始予定日": {"date": {"start": info["開始予定日"]}},
            "募集人数": {"number": int(info["募集人数"])},
            "必須スキル": {"rich_text": [{"text": {"content": info["必須スキル"]}}]},
            "歓迎スキル": {"rich_text": [{"text": {"content": info["歓迎スキル"]}}]},
        }

        # ページのコンテンツを設定
        children = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": info["説明"]}}]
                }
            }
        ]

        # Notionにページを作成
        new_page = notion.pages.create(
            parent={"database_id": os.getenv("NOTION_DATABASE_ID")},
            properties=properties,
            children=children
        )
        
        return True, new_page["url"]
    except Exception as e:
        return False, str(e)

def main():
    # セッション状態の初期化
    if 'info' not in st.session_state:
        st.session_state.info = None
    
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
        4. Notionに保存（オプション）
        """)
        
        # Notion設定
        st.markdown("### Notion設定")
        notion_token = st.text_input("Notion Token", type="password", value=os.getenv("NOTION_TOKEN", ""))
        notion_database_id = st.text_input("Notion Database ID", value=os.getenv("NOTION_DATABASE_ID", ""))
        
        if notion_token and notion_database_id:
            os.environ["NOTION_TOKEN"] = notion_token
            os.environ["NOTION_DATABASE_ID"] = notion_database_id
    
    # メインコンテンツ
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 基本情報")
        company = st.text_input("企業名", placeholder="例: 株式会社〇〇")
        industry = st.selectbox("業界", INDUSTRIES)
        work_type = st.selectbox("形式", WORK_TYPES)
        location = st.text_input("勤務地", placeholder="例: 東京都渋谷区道玄坂1-2-3 渋谷フクラス")
        nearest_station = st.text_input("最寄り駅", placeholder="例: JR山手線・埼京線、東急東横線・田園都市線、京王井の頭線、地下鉄銀座線・半蔵門線の渋谷駅より徒歩1分")
        period = st.selectbox("インターン期間", PERIODS)
        position = st.selectbox("インターン職種", POSITIONS)
        grade = st.multiselect("募集対象", GRADES)
        if "その他" in grade:
            other_grade = st.text_input("募集対象（その他）", placeholder="例: 社会人")
            grade = [g for g in grade if g != "その他"] + [other_grade]
        salary = st.number_input("報酬（時給）", min_value=0, step=100, value=1000)
        transportation_fee = st.selectbox("交通費", TRANSPORTATION_FEES)
        if transportation_fee == "その他":
            transportation_fee = st.text_input("交通費（その他）", placeholder="例: 上限5,000円まで支給")
    
    with col2:
        st.markdown("### 詳細情報")
        col_start, col_end = st.columns(2)
        with col_start:
            start_time = st.selectbox("開始時間", TIMES)
            if start_time == "その他":
                start_time = st.text_input("開始時間（その他）", placeholder="例: フレックス制")
        with col_end:
            end_time = st.selectbox("終了時間", TIMES)
            if end_time == "その他":
                end_time = st.text_input("終了時間（その他）", placeholder="例: フレックス制")
        working_days = st.selectbox("勤務日数", WORKING_DAYS)
        if working_days == "その他":
            working_days = st.text_input("勤務日数（その他）", placeholder="例: 月2回〜")
        working_time_per_week = st.number_input("勤務時間（週）", min_value=0, step=1, value=15)
        selection_process = st.selectbox("選考フロー", SELECTION_PROCESS)
        deadline = st.date_input("応募締切日")
        start_date = st.date_input("インターン開始予定日")
        capacity = st.number_input("募集人数", min_value=1, step=1)
        required_skills = st.text_area("必須スキル", placeholder="例:\n・Webアプリケーションの開発経験\n・コミュニケーション能力", height=100)
        skills = st.text_area("歓迎スキル", placeholder="例:\n・Ruby on Railsを用いたWebアプリケーションの開発経験\n・WordPressのカスタマイズ経験\n・MySQLなどのRDBMSを用いたWebアプリケーション開発\n・GitHubを用いたチーム開発の経験", height=100)
    
    # 生成ボタン
    if st.button("インターン情報を生成", type="primary"):
        if company and location and required_skills:
            # 募集対象を文字列に変換
            grade_text = "、".join(grade)
            
            info = generate_intern_info(
                company, industry, work_type, location, nearest_station, period, position, grade_text,
                f"時給{salary}円", transportation_fee, start_time, end_time, working_days, f"週{working_time_per_week}時間",
                skills, required_skills, selection_process, deadline.strftime("%Y-%m-%d"),
                start_date.strftime("%Y-%m-%d"), str(capacity)
            )
            
            # セッション状態に情報を保存
            st.session_state.info = info
            
            st.success("🎉 インターン情報が生成されました！")
            
            # 結果を表示
            st.markdown("### 生成されたインターン情報")
            st.code(info['説明'], language="text")
            
            # Notionに送信するかどうかのチェックボックス
            if os.getenv("NOTION_TOKEN") and os.getenv("NOTION_DATABASE_ID"):
                if st.checkbox("Notionに保存する"):
                    with st.spinner("Notionに保存中..."):
                        success, result = create_notion_page(info)
                        if success:
                            st.success(f"✅ Notionに保存しました！\n[ページを開く]({result})")
                        else:
                            st.error(f"⚠️ Notionへの保存に失敗しました: {result}")
            else:
                st.warning("⚠️ Notionに保存するには、サイドバーでNotion TokenとDatabase IDを設定してください。")
        else:
            st.error("⚠️ 必須項目（企業名、勤務地、必須スキル）を入力してください。")

if __name__ == "__main__":
    main() 