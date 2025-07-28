import pprint
from pathlib import Path
from time import sleep

import pytest
import requests
from tqdm import tqdm

from app.ix_manager import (
    BaseXbrlManager,
    CalLinkManager,
    DefLinkManager,
    IXBRLManager,
    LabelManager,
    PreLinkManager,
)
from app.ix_models import XBRLModel
from app.ix_tag import IxHeader


@pytest.fixture
def xbrl_model_edjp(get_xbrl_edjp_zip, get_output_dir):
    print(f"get_xbrl_edjp_zip: {get_xbrl_edjp_zip}")
    print(f"get_output_dir: {get_output_dir}")
    return XBRLModel(get_xbrl_edjp_zip, get_output_dir)


@pytest.fixture
def xbrl_model_rvfc(get_xbrl_rvfc_zip, get_output_dir):
    return XBRLModel(get_xbrl_rvfc_zip, get_output_dir)


def test_xbrl_model_instance(xbrl_model_edjp):
    assert isinstance(xbrl_model_edjp, XBRLModel)


def test_ixbrl_manager(xbrl_model_edjp):
    assert xbrl_model_edjp.get_ixbrl() is not None
    manager = xbrl_model_edjp.get_ixbrl()
    if manager:
        header = manager.ix_header
        assert sorted(header.keys()) == sorted(IxHeader.keys())


def test_all_edjp(xbrl_model_edjp):
    model = xbrl_model_edjp
    print("Start test_all_edjp")
    print(model.ixbrl_manager.xbrl_type())
    assert model.ixbrl_manager.xbrl_type() == "決算短信（日本基準）"
    assert isinstance(model.ixbrl_manager, IXBRLManager)
    assert isinstance(model.label_manager, LabelManager)
    assert isinstance(model.def_link_manager, DefLinkManager)
    assert isinstance(model.pre_link_manager, PreLinkManager)
    assert isinstance(model.cal_link_manager, CalLinkManager)


def test_xbrl_dir(get_xbrl_zip_dir, get_output_dir):
    XBRLModel.xbrl_models(get_xbrl_zip_dir, get_output_dir)
    for model in XBRLModel.xbrl_models(get_xbrl_zip_dir, get_output_dir):
        assert isinstance(model, XBRLModel)
        for _, manager in model.get_all_manager().items():
            assert manager is not None
            assert isinstance(manager, BaseXbrlManager)
            for item in manager.items:
                if item.key == "href_master":
                    pprint.pprint(item.item)


def test_all_managers(xbrl_model_edjp):
    model = xbrl_model_edjp
    item = model.get_all_items()
    assert isinstance(item, list)
