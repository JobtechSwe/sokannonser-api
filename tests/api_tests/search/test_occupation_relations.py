import pytest

from tests.test_resources.helper import get_search
from tests.test_resources.concept_ids import occupation as occ
from tests.test_resources.concept_ids import occupation_field as field
from tests.test_resources.concept_ids import occupation_group as group


@pytest.mark.integration
@pytest.mark.parametrize("work, group, field", [
    (occ.personlig_assistent, group.personliga_assistenter, field.socialt_arbete),
    (occ.akutsjukskoterska_sjukskoterska__akutmottagning, group.ambulanssjukskoterskor_m_fl_,
     field.halso__och_sjukvard)

])
def test_search_occupation_name(session, work, group, field):
    """
    Do search with 'occupation-name' and check that 'occupation_group' & 'occupation_field' are correct
    """
    json_response = get_search(session, {'occupation-name': work})
    hits = json_response['hits']
    for hit in hits:
        assert hit['occupation']['concept_id'] == work
        assert hit['occupation_group']['concept_id'] == group
        assert hit['occupation_field']['concept_id'] == field


@pytest.mark.integration
@pytest.mark.parametrize("work, group, field", [
    ([occ.personlig_assistent], group.personliga_assistenter, field.socialt_arbete),
    ([occ.ambulanssjukskoterska, occ.akutsjukskoterska_sjukskoterska__akutmottagning],
     group.ambulanssjukskoterskor_m_fl_, field.halso__och_sjukvard)
])
def test_search_occupation_group(session, work, group, field):
    """
    Do search with 'occupation-name' and check that 'occupation_group' & 'occupation_field' are correct
    """
    json_response = get_search(session, {'occupation-group': group})
    hits = json_response['hits']
    for hit in hits:
        assert hit['occupation']['concept_id'] in work
        assert hit['occupation_group']['concept_id'] == group
        assert hit['occupation_field']['concept_id'] == field


@pytest.mark.integration
@pytest.mark.parametrize("work, group, field", [(
        [occ.personlig_assistent, occ.socialsekreterare, occ.stodassistent,
         occ.komminister, occ.skolkurator, occ.barnskotare, occ.stodpedagog, occ.vardare_arbetshandledare_boendestodjare],
        [group.personliga_assistenter, group.vardare__boendestodjare, group.praster, group.socialsekreterare, group.kuratorer, group.barnskotare, group.behandlingsassistenter_och_socialpedagoger_m_fl_],
        field.socialt_arbete),
    ([occ.akutsjukskoterska_sjukskoterska__akutmottagning, occ.sjukskoterska__grundutbildad,
      occ.skotare, occ.tandskoterska, occ.vardbitrade,      occ.underskoterska__hemtjanst_och_aldreboende,
      occ.operationssjukskoterska, occ.underskoterska__vard__o_specialavd__o_mottagning],
     [group.ambulanssjukskoterskor_m_fl_, group.grundutbildade_sjukskoterskor, group.skotare, group.tandskoterskor,
      group.vardbitraden, group.underskoterskor__hemtjanst__aldreboende_m_fl_],
     field.halso__och_sjukvard)
])
def test_search_occupation_field(session, work, group, field):
    """
    Do search with 'occupation-name' and check that 'occupation_group' & 'occupation_field' are correct
    """
    json_response = get_search(session, {'occupation-field': field})
    hits = json_response['hits']
    for hit in hits:
        try:
            assert hit['occupation'][
                       'concept_id'] in work, f"expected occ {work} but got {hit['occupation']['concept_id']}"
            assert hit['occupation_group'][
                       'concept_id'] in group, f"expected group {group} but got {hit['occupation_group']['concept_id']}"
            assert hit['occupation_field'][
                       'concept_id'] == field, f"expected field {field} but got {hit['occupation_field']['concept_id']}"
        except AssertionError as e:
            print()



@pytest.mark.slow
@pytest.mark.parametrize("retries", range(10))
def test_different_results(session, retries):
    """
    A case where the number of results were not as expected.
    Not reproduced by tests
    """
    params_group = {'occupation-group': 'DJh5_yyF_hEM'}
    result_group = get_search(session, params_group)
    n_group = result_group['total']['value']  # 57

    params_group_field = {'occupation-group': 'DJh5_yyF_hEM', 'occupation-field': 'apaJ_2ja_LuF'}
    result_group_field_1 = get_search(session, params_group_field)
    n_group_field = result_group_field_1['total']['value']  # 85

    params_field = {'occupation-field': 'apaJ_2ja_LuF'}
    result_field = get_search(session, params_field)
    n_field = result_field['total']['value']  # 85

    result_group_field_2 = get_search(session, params_group_field)
    n_group_field_2 = result_group_field_2['total']['value']  # 85

    assert n_group_field == n_group_field_2 == n_field
    assert n_group_field > n_group
