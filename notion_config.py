import os
from dotenv import load_dotenv
from notion_client import Client

# .envファイルから環境変数を読み込む
load_dotenv()

# Notionクライアントの初期化
notion = Client(auth=os.getenv("NOTION_TOKEN"))

def get_notion_client():
    """Notionクライアントを取得する関数"""
    return notion

def get_database_id():
    """データベースIDを取得する関数"""
    return os.getenv("NOTION_DATABASE_ID")

def is_notion_configured():
    """Notionが正しく設定されているか確認する関数"""
    return bool(os.getenv("NOTION_TOKEN") and os.getenv("NOTION_DATABASE_ID"))

def create_notion_page(info):
    """Notionにページを作成する関数"""
    try:
        # ページのプロパティを設定
        properties = {
            "Name": {"title": [{"text": {"content": info["インターン名"]}}]},
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
            parent={"database_id": get_database_id()},
            properties=properties,
            children=children
        )
        
        return True, new_page["url"]
    except Exception as e:
        return False, str(e) 