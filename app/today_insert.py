from datetime import datetime

from app.api.insert import Insert

if __name__ == "__main__":
    outputPath = (
        "/Users/user/Vscode/XBRL_Parse_Project/stock-link-parser/output"
    )
    today = datetime.now().strftime("%Y%m%d")  # 出力例: 20210601
    targetDir = ""
    insert = Insert(outputPath)
    insert.insert_xbrl_dir(targetDir)
