from api.insert import Insert

if __name__ == "__main__":
    output_oath = (
        "/Users/user/Vscode/XBRL_Parse_Project/stock-link-parser/output"
    )
    zip_path = (
        "/Users/user/Documents/tdnet/xbrl/20240808/081220240801560862.zip"
    )
    insert = Insert(output_oath)
    insert.insert_xbrl_zip(zip_path)
