import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import streamlit as st

# .envファイルから環境変数を読み込む
load_dotenv()

def send_email(to_email, subject, body):
    """メールを送信する関数"""
    try:
        # GmailのSMTPサーバー設定
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # 送信元のメールアドレスとパスワード
        from_email = os.getenv("GMAIL_ADDRESS")
        password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not from_email or not password:
            return False, "Gmail認証情報が設定されていません"
        
        # メールの作成
        msg = MIMEText(body)
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # SMTPサーバーへの接続とメール送信
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())
        
        return True, "メールが正常に送信されました"
    except smtplib.SMTPAuthenticationError:
        return False, "認証に失敗しました。Gmail認証情報を確認してください"
    except smtplib.SMTPException as e:
        return False, f"メール送信エラー: {str(e)}"
    except Exception as e:
        return False, f"予期せぬエラーが発生しました: {str(e)}" 