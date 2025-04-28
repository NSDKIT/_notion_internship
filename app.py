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

# ページ設定
st.set_page_config(
    page_title="インターン情報自動作成ツール",
    page_icon="🎓",
    layout="wide"
)

# スタイルのカスタマイズ
st.markdown(""" 
<style>
    .css-18e3th9 {
        padding-top: 0rem;
        padding-bottom: 10rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .stSidebar > div:first-child {
        background-color: #f0f2f6;
    }
    .css-1d391kg {
        padding-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# フォームの各セクション定義
sections = [
    {"title": "基本情報", "fields": [
        {"label": "企業名*", "key": "company_name", "type": "text"},
        {"label": "業界", "key": "industry", "type": "select", "options": INDUSTRIES},
        {"label": "形式", "key": "format_type", "type": "select", "options": WORK_TYPES},
        {"label": "勤務地*", "key": "location", "type": "text"},
        {"label": "最寄り駅", "key": "nearest_station", "type": "text"},
        {"label": "インターン期間", "key": "period", "type": "text"},
        {"label": "インターン職種", "key": "position", "type": "text"},
        {"label": "募集対象", "key": "grade", "type": "multiselect", "options": GRADES},
        {"label": "報酬（時給）", "key": "salary", "type": "number", "min": 0, "step": 100, "value": 1000},
        {"label": "交通費", "key": "transportation_fee", "type": "select", "options": TRANSPORTATION_FEES}
    ]},
    {"title": "勤務時間", "fields": [
        {"label": "開始時間", "key": "start_time", "type": "select", "options": TIMES},
        {"label": "終了時間", "key": "end_time", "type": "select", "options": TIMES},
        {"label": "勤務日数", "key": "working_days", "type": "select", "options": WORKING_DAYS},
        {"label": "勤務時間（週）", "key": "working_hours", "type": "number", "min": 0, "step": 1, "value": 0}
    ]},
    {"title": "選考情報", "fields": [
        {"label": "選考フロー", "key": "selection_process", "type": "select", "options": SELECTION_PROCESS},
        {"label": "応募締切日", "key": "deadline", "type": "date"},
        {"label": "インターン開始予定日", "key": "start_date", "type": "date"},
        {"label": "募集人数", "key": "number_of_recruits", "type": "number", "min": 0, "step": 1, "value": 0}
    ]},
    {"title": "スキル要件", "fields": [
        {"label": "必須スキル*", "key": "required_skills", "type": "textarea"},
        {"label": "歓迎スキル", "key": "preferred_skills", "type": "textarea"}
    ]}
]

# フォームデータと現在のステップの初期化
if "form_data" not in st.session_state:
    st.session_state.form_data = {}
if "current_step" not in st.session_state:
    st.session_state.current_step = 0

def initialize_session_state():
    for section in sections:
        for field in section["fields"]:
            if field["key"] not in st.session_state:
                st.session_state[field["key"]] = ""
    if "current_step" not in st.session_state:
        st.session_state["current_step"] = 0

initialize_session_state()

# セクション名のリストを作成
section_names = [section["title"] for section in sections]

# サイドバーにセクションのナビゲーションを表示
st.sidebar.markdown("## セクション")
for i, section_name in enumerate(section_names):
    if i == st.session_state.current_step:
        if st.sidebar.button(f"→ {i+1}. {section_name} (現在)", key=f"btn_current_{i}"):
            st.session_state.current_step = i
            st.rerun()
    else:
        if st.sidebar.button(f"{i+1}. {section_name}", key=f"btn_{i}"):
            st.session_state.current_step = i
            st.rerun()

# プログレスバーの初期化と更新
progress_bar = st.progress(0)
current_section_index = st.session_state.current_step
progress_percentage = (current_section_index + 1) / len(sections)
progress_bar.progress(progress_percentage)

def display_section(section):
    st.header(section["title"])
    for field in section["fields"]:
        if field["type"] == "text":
            st.text_input(label=field["label"], key=field["key"])
        elif field["type"] == "select":
            st.selectbox(label=field["label"], key=field["key"], options=field["options"])
        elif field["type"] == "multiselect":
            selected = st.multiselect(label=field["label"], key=field["key"], options=field["options"])
            if "その他" in selected:
                other_value = st.text_input(f"{field['label']}（その他）", key=f"{field['key']}_other")
                if other_value:
                    selected = [x for x in selected if x != "その他"] + [other_value]
                st.session_state[field["key"]] = selected
        elif field["type"] == "number":
            st.number_input(
                label=field["label"],
                key=field["key"],
                min_value=field.get("min", 0),
                step=field.get("step", 1),
                value=field.get("value", 0)
            )
        elif field["type"] == "date":
            st.date_input(label=field["label"], key=field["key"])
        elif field["type"] == "textarea":
            st.text_area(label=field["label"], key=field["key"])

def save_form_data():
    current_section = sections[st.session_state.current_step]
    for field in current_section["fields"]:
        field_key = field["key"]
        st.session_state.form_data[field_key] = st.session_state.get(field_key, "")

def navigate_sections():
    current_section = sections[st.session_state.current_step]
    display_section(current_section)

    col1, col2, col3 = st.columns([1,5,1])
    with col1:
        if st.button("戻る") and st.session_state.current_step > 0:
            st.session_state.current_step -= 1
            st.rerun()

    with col3:
        if st.session_state.current_step < len(sections) - 1:
            if st.button("次へ"):
                save_form_data()
                st.session_state.current_step += 1
                st.rerun()
        else:
            if st.button("生成"):
                save_form_data()
                if not st.session_state.form_data.get("company_name") or not st.session_state.form_data.get("location") or not st.session_state.form_data.get("required_skills"):
                    st.error("⚠️ 必須項目（企業名、勤務地、必須スキル）を入力してください。")
                else:
                    info = generate_intern_info(
                        company_name=st.session_state.form_data["company_name"],
                        industry=st.session_state.form_data["industry"],
                        format_type=st.session_state.form_data["format_type"],
                        location=st.session_state.form_data["location"],
                        nearest_station=st.session_state.form_data["nearest_station"],
                        period=st.session_state.form_data["period"],
                        position=st.session_state.form_data["position"],
                        grade="、".join(st.session_state.form_data["grade"]),
                        salary=st.session_state.form_data["salary"],
                        transportation_fee=st.session_state.form_data["transportation_fee"],
                        start_time=st.session_state.form_data["start_time"],
                        end_time=st.session_state.form_data["end_time"],
                        working_days=st.session_state.form_data["working_days"],
                        working_hours=st.session_state.form_data["working_hours"],
                        selection_process=st.session_state.form_data["selection_process"],
                        deadline=st.session_state.form_data["deadline"],
                        start_date=st.session_state.form_data["start_date"],
                        number_of_recruits=st.session_state.form_data["number_of_recruits"],
                        required_skills=st.session_state.form_data["required_skills"],
                        preferred_skills=st.session_state.form_data["preferred_skills"]
                    )
                    
                    st.success("🎉 インターン情報が生成されました！")
                    st.code(info['説明'], language="text")
                    
                    # Notionに保存
                    if save_to_notion(info):
                        st.success("📝 Notionデータベースに保存されました！")
                    
                    # メール送信
                    try:
                        service = get_gmail_service()
                        if service:
                            message = MIMEText(info['説明'])
                            message['to'] = os.getenv('GMAIL_ADDRESS')
                            message['subject'] = f"【インターン情報】{st.session_state.form_data['company_name']}"
                            
                            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                            service.users().messages().send(
                                userId='me',
                                body={'raw': raw_message}
                            ).execute()
                            st.success("📧 メールが送信されました！")
                        else:
                            st.warning("⚠️ メール送信には認証が必要です。サイドバーから認証を行ってください。")
                    except Exception as e:
                        st.error(f"メールの送信に失敗しました: {str(e)}")

navigate_sections()

# サイドバーに使い方の説明を表示
with st.sidebar:
    st.markdown("""
    ### 使い方
    1. 各セクションの情報を入力
    2. 「次へ」ボタンで次のセクションに進む
    3. 最後のセクションで「生成」ボタンをクリック
    4. 情報が自動的にNotionデータベースに保存されます
    5. メールが自動的に送信されます

    ### 注意事項
    - * が付いている項目は必須です
    - 「その他」を選択した場合は、詳細を入力できます
    - メール送信にはGoogle認証が必要です
    - Notionデータベースへの保存にはNotionトークンが必要です
    """)

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

def get_notion_client():
    """Notionクライアントを取得する関数"""
    try:
        return Client(auth=os.getenv("NOTION_TOKEN"))
    except Exception as e:
        st.error(f"Notionクライアントの初期化に失敗しました: {str(e)}")
        return None

def save_to_notion(info):
    """Notionデータベースに情報を保存する関数"""
    try:
        notion = get_notion_client()
        if not notion:
            return False

        database_id = os.getenv("NOTION_DATABASE_ID")
        
        # 日付をISO形式に変換
        deadline = info['応募締切日'].strftime("%Y-%m-%d") if info['応募締切日'] else None
        start_date = info['インターン開始予定日'].strftime("%Y-%m-%d") if info['インターン開始予定日'] else None
        
        # 勤務時間の表示形式を設定
        working_hours_display = f"{info['開始時間']}〜{info['終了時間']}" if info['開始時間'] != "フレックス制" and info['終了時間'] != "フレックス制" else "フレックス制"
        
        # データベースに新しいページを作成
        notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "企業名": {"title": [{"text": {"content": info['企業名']}}]},
                "業界": {"select": {"name": info['業界']}},
                "形式": {"select": {"name": info['形式']}},
                "勤務地": {"rich_text": [{"text": {"content": info['勤務地']}}]},
                "最寄り駅": {"rich_text": [{"text": {"content": info['最寄り駅']}}]},
                "インターン期間": {"rich_text": [{"text": {"content": info['インターン期間']}}]},
                "インターン職種": {"rich_text": [{"text": {"content": info['インターン職種']}}]},
                "募集対象": {"rich_text": [{"text": {"content": info['募集対象']}}]},
                "報酬": {"number": info['報酬']},
                "交通費": {"rich_text": [{"text": {"content": info['交通費']}}]},
                "勤務時間": {"rich_text": [{"text": {"content": working_hours_display}}]},
                "勤務日数": {"rich_text": [{"text": {"content": info['勤務日数']}}]},
                "週の勤務時間": {"number": info['週の勤務時間']},
                "選考フロー": {"rich_text": [{"text": {"content": info['選考フロー']}}]},
                "応募締切日": {"date": {"start": deadline}} if deadline else None,
                "インターン開始予定日": {"date": {"start": start_date}} if start_date else None,
                "募集人数": {"number": info['募集人数']},
                "必須スキル": {"rich_text": [{"text": {"content": info['必須スキル']}}]},
                "歓迎スキル": {"rich_text": [{"text": {"content": info['歓迎スキル']}}]},
                "ステータス": {"select": {"name": "新規"}},
                "登録日": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            }
        )
        return True
    except Exception as e:
        st.error(f"Notionへの保存に失敗しました: {str(e)}")
        return False

def generate_intern_info(company, industry, work_type, location, nearest_station, period, position, grade, 
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

if __name__ == "__main__":
    main() 