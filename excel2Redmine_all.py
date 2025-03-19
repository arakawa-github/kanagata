
import requests
import pandas as pd
import io

# Redmineの設定
REDMINE_URL = "http://sys.asahigum.co.jp:81/redmine/"  # RedmineのURL
API_KEY = "e946cdd15454fead657a3ca864206d15a2386c24"  # RedmineのAPIキー

st.title("ファイルアップロードと選択")

# **ファイルアップローダー**
excel_file_1 = st.file_uploader("ファイルを選択してください", type=["xlsx"])

if excel_file_1 is not None:
    excel_file = io.BytesIO(excel_file_1.read())  # Noneチェックを追加
    df = pd.read_excel(excel_file)

    # **リストから選択**
    options = ["本社", "つくば", "三重", "九州", "倉敷", "京都", "千葉", "土浦",
               "堺", "大阪", "宇都宮", "小山", "小松", "岡山", "新潟", "明石", 
               "松山","枚方", "滋賀", "相模原", "船橋", "長野"]
    
    selected_eigyou = st.selectbox("担当プロジェクトを選択してください", options)

    project_mapping = {
        "本社": "kanagata", "つくば": "tsukubax", "三重": "k-mie", "九州": "k-kyusyu",
        "倉敷": "k-kurashiki", "京都": "k-kyouto", "千葉": "k-chiba", "土浦": "k-tsuchiura",
        "堺": "k-sakai", "大阪": "k-oosaka", "宇都宮": "k-utsunomiya", "小山": "k-oyama",
        "小松": "k-komatsu", "岡山": "k-okayama", "新潟": "k-niigata", "明石": "k-akashi",
        "松山": "k-matsuyama", "枚方": "k-hirakata", "滋賀": "k-shiga", "相模原": "k-sagamihara",
        "船橋": "k-funahashi", "長野": "k-nagano"
    }
    
    projectID = project_mapping.get(selected_eigyou, "unknown")

    st.write(f"選択されたプロジェクト: {selected_eigyou} (ID: {projectID})")
else:
    st.warning("ファイルをアップロードしてください。")

# 必須フィールド（管理画面で確認する）
REQUIRED_FIELDS = ["subject", "project_id", "tracker_id","円外貨","その他記載事項1（備考）","status","区分"]

# ヘッダー情報
headers = {
    "X-Redmine-API-Key": API_KEY,
    "Content-Type": "application/json"
}
def safe_value(value, default=""):
    try:
        return float(value) if pd.notna(value) and str(value).replace(".", "").isdigit() else default
    except ValueError:
        return default
    
ii=0
#トラッカーのIDは数値である！！！！
#{'id': 45, 'name': '金型発注-拠点長決裁'
#{'id': 48, 'name': '海外一括検収分'
#'id': 49, 'name': '海外償却金型'
#{'id': 50, 'name': '国内一括検収分
#{'id': 51, 'name': '国内償却金型'
# チケットをRedmineに登録
for index, row in df.iterrows():
    ii = ii+1
    # 必須フィールドのチェック（空ならデフォルト値を入れる）
    subject = row["subject"] if pd.notna(row["subject"]) else "未設定の件名"
    project_id = projectID
    tracker_id = row["tracker_id"] if pd.notna(row["tracker_id"]) else 50  # デフォルトのトラッカーID
    print("tracker_id"+str(tracker_id))
    status_1 = row["status"] if pd.notna(row["status"]) else "申請"  # デフォルトのトラッカーID
    Yengaika = row["円外貨"] if pd.notna(row["円外貨"]) else "円"
    sonota = row["その他記載事項1（備考）"] if pd.notna(row["その他記載事項1（備考）"]) else "一括入力"
    #--------------------------------------------------
    aaa = pd.to_numeric(row["型仕入"], errors="coerce") if pd.notna(row["型仕入"]) else 0.0
    aaa = aaa if pd.notna(aaa) else 0.0
    bbb1 = (str(row["仕入月"])+"月") if pd.notna(row["仕入月"]) else "1月"
    bbb = (str(row["売上月"])+"月") if pd.notna(row["売上月"]) else "1月"
    ccc = int(pd.to_numeric(row["型売り"], errors="coerce")) if pd.notna(row["型売り"]) else 0
    ccc = ccc if pd.notna(ccc) else 0
    ddd = row["品番"] if pd.notna(row["品番"]) else "999999"
    eee = row["品名"] if pd.notna(row["品名"]) else "MMMMMM"
    fff = row["金型仕入先"] if pd.notna(row["金型仕入先"]) else "XXXXXX"
    ggg = row["インボイス番号"] if pd.notna(row["インボイス番号"]) else "未記入"
    hhh = row["送金依頼番号"] if pd.notna(row["送金依頼番号"]) else "未記入"
    data = {
        "issue": {
            "project_id": projectID,  
            "tracker_id": tracker_id,  
            "status_id": status_1,
            "priority_id": 2,
            "subject": subject, 
			"custom_fields": [
                {"id": 339, "value": "---"},  # 区分,
                {"id": 346, "value": bbb},  # 売上月：売上月},
                {"id": 347, "value": bbb1},  # 売上月：売上月},
                {"id": 305, "value": ddd},   #  金型品番:品番
                {"id": 306, "value": eee},   #  金型品名:品名
                {"id": 289, "value": fff},   #  金型仕入先:金型仕入先
                {"id": 294, "value": aaa},   #  仕入金額:型仕入
                {"id": 295, "value": ccc},    #  redmine売上金額:excel型売り
                {"id": 298, "value": float(safe_value(row["製品仕入"],0.0))},   #  製品　仕入額:製品仕入
                {"id": 299, "value": float(safe_value(row["製品売り"],0.0))},   #  製品　売上額:製品売り
                {"id": 309, "value": Yengaika},   #  製品売り:円外貨
                {"id": 338, "value": sonota},   # その他記載事項1（備考)
                {"id": 303, "value": ggg} ,  # インボイス番号
                {"id": 348, "value": hhh}   # 送金依頼番号
            ]
        }
    }

    response = requests.post(f"{REDMINE_URL}/issues.json", json=data, headers=headers)
    print("入力行数:"+str(ii))
    if response.status_code == 201:
        print(f"チケット作成成功: {subject}")
    else:
        print(f"チケット作成失敗: {subject} - {response.text}")
        
#response = requests.get(f"{REDMINE_URL}/trackers.json", headers=headers)
#trackers = response.json()

#print(trackers)  # ここでIDと名前を確認
