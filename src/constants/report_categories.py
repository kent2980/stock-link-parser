class ReportCategories:
    """決算短信報告書の報告詳細区分を定義します。"""

    EDJP = "edjp"
    """ 日本基準 """
    EDUS = "edus"
    """ 米国基準 """
    EDIF = "edif"
    """ 国際会計基準 """
    EDIT = "edit"
    """ 国際会計基準 """
    RVDF = "rvdf"
    """ 配当予想修正に関するお知らせ """
    RVFC = "rvfc"
    """ 業績予想修正に関するお知らせ """
    REJP = "rejp"
    """ REIT決算短信 """
    RRDF = "rrdf"
    """ 分配予想の修正に関するお知らせ """
    RRFC = "rrfc"
    """ 運用状況の予想の修正に関するお知らせ """
    EFJP = "efjp"
    """ ETF決算短信 """

    @classmethod
    def field_values(cls):
        """すべての報告詳細区分を返します。"""
        return [
            cls.EDJP,
            cls.EDUS,
            cls.EDIF,
            cls.EDIT,
            cls.RVDF,
            cls.RVFC,
            cls.REJP,
            cls.RRDF,
            cls.RRFC,
            cls.EFJP,
        ]

    @classmethod
    def financial_reports(cls):
        """決算短信報告書の報告詳細区分を返します。"""
        return [
            cls.EDJP,
            cls.EDUS,
            cls.EDIF,
            cls.EDIT,
            cls.REJP,
            cls.EFJP,
        ]

    @classmethod
    def revision_reports(cls):
        """修正報告書の報告詳細区分を返します。"""
        return [
            cls.RVDF,
            cls.RVFC,
            cls.RRDF,
            cls.RRFC,
        ]
