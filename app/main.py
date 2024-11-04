from app.api.insert import Insert

if __name__ == "__main__":
    output_oath = (
        "/Users/user/Vscode/XBRL_Parse_Project/stock-link-parser/output"
    )
    zip_path = "/Users/user/Documents/tdnet/xbrl/20241031"
    insert = Insert(output_oath)
    insert.insert_xbrl_dir(zip_path)
