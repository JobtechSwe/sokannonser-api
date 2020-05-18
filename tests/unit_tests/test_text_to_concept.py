import pytest

from tests.integration_tests.search.test_query_rewrite import text_to_concept


@pytest.mark.unit
def test_clean_plus_minus():
    cleaned_text = text_to_concept.clean_plus_minus(
        '-mållare målare +undersköterska java-utvecklare -key account manager c-sharp -java -noggrann flexibel')
    assert cleaned_text == 'mållare målare undersköterska java-utvecklare key account manager c-sharp java noggrann flexibel'
