# region IX Table Endpoints
# POST エンドポイント
POST_HEAD_TITLES = "/xbrl/ix/head/list/"
""" IX_HEAD_TITLEテーブルに複数データを追加するエンドポイント """
POST_NON_NUMERICS = "/xbrl/ix/non_numeric/list/"
""" IX_NON_NUMERICテーブルに複数データを追加するエンドポイント """
POST_NON_FRACTIONS = "/xbrl/ix/non_fraction/list/"
""" IX_NON_FRACTIONテーブルに複数データを追加するエンドポイント """
POST_LABEL_LOCS = "/xbrl/link/lab/loc/list/"
""" LINK_LABEL_LOCテーブルに複数データを追加するエンドポイント """
POST_LABEL_ARCS = "/xbrl/link/lab/arc/list/"
""" LINK_LABEL_ARCテーブルに複数データを追加するエンドポイント """
POST_LABEL_VALUES = "/xbrl/link/lab/value/list/"
""" LINK_LABEL_VALUEテーブルに複数データを追加するエンドポイント """
POST_CAL_LOCS = "/xbrl/link/cal/loc/list/"
""" LINK_CAL_LOCテーブルに複数データを追加するエンドポイント """
POST_CAL_ARCS = "/xbrl/link/cal/arc/list/"
""" LINK_CAL_ARCテーブルに複数データを追加するエンドポイント """
POST_PRE_LOCS = "/xbrl/link/pre/loc/list/"
""" LINK_PRE_LOCテーブルに複数データを追加するエンドポイント """
POST_PRE_ARCS = "/xbrl/link/pre/arc/list/"
""" LINK_PRE_ARCテーブルに複数データを追加するエンドポイント """
POST_DEF_LOCS = "/def/link/def/loc/list/"
""" LINK_DEF_LOCテーブルに複数データを追加するエンドポイント """
POST_DEF_ARCS = "/def/link/def/arc/list/"
""" LINK_DEF_ARCテーブルに複数データを追加するエンドポイント """
POST_SOURCES = "/xbrl/source/list/"
""" SOURCEテーブルに複数データを追加するエンドポイント """
POST_SCHEMAS = "/xbrl/schema/linkbase/list/"
""" SCHEMAテーブルに複数データを追加するエンドポイント """
POST_FILE_PATH = "/xbrl/ix/file_path/"
""" IX_FILE_PATHテーブルにデータを追加するエンドポイント """
POST_QUALITATIVE = "/xbrl/qualitative/list/"
""" QUALITATIVEテーブルに複数データを追加するエンドポイント """
POST_TITLE_SUMMARY = "/ix/summary/ix_title_summary/item/"

# UPDATE エンドポイント
UPDATE_HEAD_ACTIVE = "/xbrl/ix/head/active/"
""" IX_HEAD_TITLEテーブルを有効化するエンドポイント """
UPDATE_HEAD_GENERATE = "/xbrl/ix/head/generate/"
""" IX_HEAD_TITLEテーブルを生成するエンドポイント """

# GET エンドポイント
IS_ACTIVE_HEAD = "/xbrl/ix/head/is_active/"
""" IX_HEAD_TITLEテーブルに有効なデータが存在するか確認するエンドポイント """
IS_EXITS_SOURCE_FILE_ID = "/xbrl/is/exits/source_file_id/"
""" SourceFileテーブルにSOURCE_FILE_IDが存在するか確認するエンドポイント """

# endregion

# region Jpx Table Endpoints

# POST エンドポイント
POST_JPX_STOCK_INFO = "/jpx/stock_info/"
""" JPX_STOCK_INFOテーブルにデータを追加するエンドポイント """
POST_JPX_STOCK_INFOS = "/jpx/stock_info/list/"
""" JPX_STOCK_INFOテーブルに複数データを追加するエンドポイント """
# GET エンドポイント
GET_JPX_STOCK_INFO = "/jpx/stock_info/"
""" JPX_STOCK_INFOテーブルのデータを取得するエンドポイント """
GET_JPX_STOCK_INFO_LIST = "/jpx/stock_info/"
""" JPX_STOCK_INFOテーブルの全てのデータを取得するエンドポイント """

# endregion


# region Wiki Endpoints
# GET エンドポイント
GET_WIKI_All = "/wiki/"
""" stock_wikiテーブルから全てのデータを取得するエンドポイント """
GET_WIKI_FROM_CODE = "/wiki/"
""" stock_wikiテーブルからコードを指定してデータを取得するエンドポイント """
# POST エンドポイント
POST_WIKI = "/wiki/"
""" stock_wikiテーブルにデータを追加するエンドポイント """
# endregion
