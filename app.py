import sys
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

def select_from_list(options, prompt):
    while True:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        try:
            choice = int(input("番号を選択してください: "))
            if 1 <= choice <= len(options):
                return options[choice-1]
            print("無効な選択です。もう一度選択してください。")
        except ValueError:
            print("数字を入力してください。")

def input_date(prompt):
    while True:
        try:
            date_str = input(f"{prompt} (YYYY-MM-DD): ")
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("正しい日付形式で入力してください（例: 2024-03-15）")

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
    print("インターン情報自動作成ツール")
    company = input("企業名を入力してください: ")
    industry = select_from_list(INDUSTRIES, "業界を選択してください:")
    location = input("勤務地を入力してください: ")
    period = select_from_list(PERIODS, "インターン期間を選択してください:")
    position = select_from_list(POSITIONS, "インターン職種を選択してください:")
    grade = select_from_list(GRADES, "募集対象を選択してください:")
    salary = select_from_list(SALARIES, "報酬を選択してください:")
    selection_process = select_from_list(SELECTION_PROCESS, "選考フローを選択してください:")
    deadline = input_date("応募締切日を入力してください")
    start_date = input_date("インターン開始予定日を入力してください")
    capacity = input("募集人数を入力してください: ")
    skills = input("必要なスキル・経験を入力してください（複数ある場合はカンマ区切り）: ")

    info = generate_intern_info(company, industry, location, period, position, grade, 
                              salary, selection_process, deadline, start_date, 
                              capacity, skills)
    print("\n--- 自動生成されたインターン情報 ---")
    for k, v in info.items():
        print(f"\n{k}: {v}")

if __name__ == "__main__":
    main() 