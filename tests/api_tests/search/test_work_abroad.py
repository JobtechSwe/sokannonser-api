import pytest
from tests.test_resources.helper import get_search, check_ads_for_country_in_address
import tests.test_resources.concept_ids.concept_ids_geo as geo
from sokannonser.settings import UNSPECIFIED_SWEDEN_WORKPLACE, ABROAD


@pytest.mark.parametrize("abroad", [True, False])
def test_in_sweden(session, abroad):
    """
    If param 'arbete-utomlands' is set to True AND no other geographical filters are used,
    only ads with workplace address outside Sweden should be shown
    """
    response = get_search(session, {ABROAD: abroad})
    assert response['total']['value'] > 0
    check_ads_for_country_in_address(response['hits'], abroad=abroad)


@pytest.mark.parametrize('geo_param', [
    {'municipality': geo.vasteras},
    {'municipality': [geo.uppsala, geo.linkoping]},
    {'region': geo.ostergotlands_lan},
    {'region': [geo.skane_lan, geo.norrbottens_lan]},
    {UNSPECIFIED_SWEDEN_WORKPLACE: True},
])
def test_abroad_and_local(session, geo_param):
    """
    if 'arbete-utomlands' is True AND any geographical filter is used (municipality, region, 'unspecified-sweden-workplace')
    the result should include hits for BOTH work abroad and for the Swedish geographical filter
    """
    params_abroad = {ABROAD: True}
    hits_abroad = get_search(session, params_abroad)['total']['value']

    hits_geo_only = get_search(session, geo_param)['total']['value']
    params_abroad.update(geo_param)
    hits_geo_and_abroad = get_search(session, params_abroad)['total']['value']

    assert hits_geo_only > 0
    assert hits_geo_and_abroad > hits_geo_only
    assert hits_geo_and_abroad > hits_abroad


@pytest.mark.parametrize('geo_param', [
    {'country': geo.norge},
    {'country': [geo.norge, geo.schweiz, geo.aland_tillhor_finland]}
])
def test_abroad_and_other_country(session, geo_param):
    """
    'arbete-utomlands' set to True alone OR in combination  with country filter for other countries
     should give the same number of results.
    """
    params_abroad = {ABROAD: True}
    hits_abroad = get_search(session, params_abroad)
    check_ads_for_country_in_address(hits_abroad['hits'], abroad=True)

    params_abroad.update(geo_param)
    hits_abroad_plus_country = get_search(session, params_abroad)
    assert hits_abroad['total']['value'] == hits_abroad_plus_country['total']['value']
    check_ads_for_country_in_address(hits_abroad_plus_country['hits'], abroad=True)


@pytest.mark.parametrize('geo_param', [
    {'municipality': geo.stockholm},
    {'municipality': [geo.sundsvall, geo.goteborg]},
    {'region': geo.vastra_gotalands_lan},
    {'region': [geo.blekinge_lan, geo.vasterbottens_lan]}
])
def test_abroad_false_does_not_affect_results(session, geo_param):
    """
    Search with municipality or region concept ids should not be affected if ARBETE_UTOMLANDS is False
    if the parameter ARBETE_UTOMLANDS is missing or False, the search result should not be affected
    """
    hits_1 = get_search(session, geo_param)['total']['value']
    geo_param.update({ABROAD: False})
    hits_2 = get_search(session, geo_param)['total']['value']
    assert hits_1 == hits_2
