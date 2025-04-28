import streamlit as st
from datetime import datetime, time
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

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

# Google Sheets APIへの接続
@st.cache_resource
def get_google_sheets_service():
    """Google Sheets APIサービスを取得する関数"""
    try:
        # デバッグ情報を追加
        print("利用可能なシークレットキー:", list(st.secrets.keys()))
        
        # サービスアカウント情報の取得方法を修正
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        st.error(f"認証エラー: {str(e)}")
        st.write(f"エラーの詳細: {type(e).__name__}, {str(e)}")
        return None

def save_to_sheets(info):
    """Googleスプレッドシートに情報を保存する関数"""
    try:
        # デバッグ情報
        st.write("デバッグ情報:")
        st.write(f"利用可能なシークレットキー: {list(st.secrets.keys())}")
        
        if "gcp_service_account" in st.secrets:
            st.write("gcp_service_accountの中のキー:")
            for key in st.secrets["gcp_service_account"]:
                # プライベートキーなどの機密情報は表示しない
                if key == "private_key":
                    st.write(f"- private_key: (存在します)")
                else:
                    st.write(f"- {key}")
        
        # TOMLファイルの階層構造の問題を回避する代替コード
        try:
            # 直接スプレッドシートIDを取得してみる
            spreadsheet_id = st.secrets.get("SPREADSHEET_ID", None)
            if spreadsheet_id:
                st.write(f"SPREADSHEET_ID直接アクセス: あり")
            else:
                st.write("SPREADSHEET_ID直接アクセス: なし")
                
                # gcp_service_accountの中から探す
                if "gcp_service_account" in st.secrets and "SPREADSHEET_ID" in st.secrets["gcp_service_account"]:
                    spreadsheet_id = st.secrets["gcp_service_account"]["SPREADSHEET_ID"]
                    st.write("gcp_service_accountの中にSPREADSHEET_IDがあります")
                else:
                    # ハードコードバックアップ (テスト用)
                    spreadsheet_id = "1SsUwD9XsadcfaxsefaMu49lx72iQxaefdaefA7KzvM"
                    st.write("ハードコードされたSPREADSHEET_IDを使用します")
            
            # シート名も同様に
            sheet_name = st.secrets.get("SHEET_NAME", None)
            if not sheet_name:
                if "gcp_service_account" in st.secrets and "SHEET_NAME" in st.secrets["gcp_service_account"]:
                    sheet_name = st.secrets["gcp_service_account"]["SHEET_NAME"]
                else:
                    sheet_name = "info"
                    
            st.write(f"使用するスプレッドシートID: {spreadsheet_id[:5]}...{spreadsheet_id[-5:]}")
            st.write(f"使用するシート名: {sheet_name}")
                    
            # 以下から既存のコードを続ける
            service = get_google_sheets_service()
            if not service:
                return False, "Google認証に失敗しました"
            
            # 以下略...
        
        service = get_google_sheets_service()
        if not service:
            return False, "Google認証に失敗しました"
            
        # スプレッドシートIDを取得
        try:
            spreadsheet_id = st.secrets["SPREADSHEET_ID"]
            st.write(f"SPREADSHEET_ID: {spreadsheet_id[:5]}...{spreadsheet_id[-3:]}")
        except Exception as e:
            st.error(f"SPREADSHEET_IDの取得に失敗: {str(e)}")
            return False, f"SPREADSHEET_IDの取得に失敗: {str(e)}"
        
        # シート名を取得
        try:
            sheet_name = st.secrets.get("SHEET_NAME", "Sheet1")
            st.write(f"SHEET_NAME: {sheet_name}")
        except Exception as e:
            st.error(f"SHEET_NAMEの取得に失敗: {str(e)}")
            return False, f"SHEET_NAMEの取得に失敗: {str(e)}"
        
        # ヘッダー行を準備
        headers = [
            "インターン名", "企業名", "業界", "形式", "勤務地", "最寄り駅",
            "期間", "職種", "募集対象", "報酬", "交通費", "勤務可能時間",
            "勤務日数", "勤務時間", "選考フロー", "応募締切", "開始予定日",
            "募集人数", "必須スキル", "歓迎スキル", "説明"
        ]
        
        # データ行を準備
        values = [
            info["インターン名"], info["企業名"], info["業界"], info["形式"],
            info["勤務地"], info["最寄り駅"], info["期間"], info["職種"],
            info["募集対象"], info["報酬"], info["交通費"], info["勤務可能時間"],
            info["勤務日数"], info["勤務時間"], info["選考フロー"],
            info["応募締切"], info["開始予定日"], info["募集人数"],
            info["必須スキル"], info["歓迎スキル"], info["説明"]
        ]
        
        # シートが存在するか確認
        try:
            # シート情報を取得
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            
            # シート名リストを取得
            sheet_names = [sheet['properties']['title'] for sheet in sheets]
            
            # シートが存在しない場合は作成
            if sheet_name not in sheet_names:
                service.spreadsheets().batchUpdate(
                    spreadsheetId=spreadsheet_id,
                    body={
                        'requests': [{
                            'addSheet': {
                                'properties': {
                                    'title': sheet_name
                                }
                            }
                        }]
                    }
                ).execute()
                
                # ヘッダー行を書き込む
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f"{sheet_name}!A1:U1",
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
        except Exception as e:
            st.error(f"シート確認中にエラーが発生しました: {str(e)}")
            return False, f"シート確認中にエラーが発生しました: {str(e)}"
        
        # 既存のデータを取得
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:U"
        ).execute()
        
        # 行番号を計算（ヘッダー行を除く）
        rows = result.get('values', [])
        next_row = len(rows) + 1
        
        # 新しいデータを追加
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A{next_row}:U{next_row}",
            valueInputOption='RAW',
            body={'values': [values]}
        ).execute()
        
        return True, "スプレッドシートに保存しました"
    except Exception as e:
        st.error(f"エラーの詳細: {str(e)}")
        return False, f"スプレッドシートへの保存に失敗しました: {str(e)}"

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
    times.append("フレックス制")
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

def main():
    # セッション状態の初期化
    if 'info' not in st.session_state:
        st.session_state.info = None
    if 'info_generated' not in st.session_state:
        st.session_state.info_generated = False
    if 'save_option' not in st.session_state:
        st.session_state.save_option = "保存しない"
    
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
        4. Googleスプレッドシートに保存（オプション）
        """)

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
        with col_end:
            end_time = st.selectbox("終了時間", TIMES)
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
            st.session_state.info_generated = True
            
            st.success("🎉 インターン情報が生成されました！")
        else:
            st.error("⚠️ 必須項目（企業名、勤務地、必須スキル）を入力してください。")
    
    # 生成された情報がある場合に表示
    if st.session_state.info_generated and st.session_state.info:
        # 結果を表示
        st.markdown("### 生成されたインターン情報")
        st.code(st.session_state.info['説明'], language="text")
        
        # Googleスプレッドシートへの保存オプション
        st.markdown("### Googleスプレッドシートへの保存")
        
        # ラジオボタンの選択状態をセッションに保存
        st.session_state.save_option = st.radio(
            "保存オプション",
            ["保存しない", "Googleスプレッドシートに保存する"],
            key="save_option_radio"
        )
        
        # 保存オプションが選択された場合、保存ボタンを表示
        if st.session_state.save_option == "Googleスプレッドシートに保存する":
            save_button = st.button("保存を実行する", key="save_button")
            if save_button:
                with st.spinner("スプレッドシートに保存中..."):
                    try:
                        success, result = save_to_sheets(st.session_state.info)
                        if success:
                            st.success(f"✅ {result}")
                        else:
                            st.error(f"⚠️ {result}")
                    except Exception as e:
                        st.error(f"⚠️ エラーが発生しました: {str(e)}")
                        st.write(f"エラー詳細: {str(e)}")

if __name__ == "__main__":
    main()
