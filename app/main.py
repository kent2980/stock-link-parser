from app.api.insert import Insert

if __name__ == "__main__":
    output_oath = (
        "/home/kent2980/docker_cont/stock-link-parser/output"
    )
    zip_path = "/home/kent2980/doc/tdnet/20241031"
    insert = Insert(output_oath)
    insert.insert_xbrl_dir(zip_path)
