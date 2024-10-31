from app.api.insert import Insert

if __name__ == "__main__":
    outputPath = (
        "/Users/user/Vscode/XBRL_Parse_Project/stock-link-parser/output"
    )
    targetDir = ""
    insert = Insert(outputPath)
    insert.insert_xbrl_dir(targetDir)
