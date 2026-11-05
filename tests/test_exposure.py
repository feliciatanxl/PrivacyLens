"""Unit tests for AI Exposure Reconstruction Engine (Main USP)."""
from backend.services.exposure_engine import explain_exposure


class TestExposureEngine:

    def test_school_and_location_routine_combination(self):
        findings = [
            {'category': 'School uniform'},
            {'category': 'School badge / logo'},
            {'category': 'Street sign / Location clue'},
            {'category': 'Schedule / Routine clue'},
        ]
        res = explain_exposure(findings)
        assert res['risk_level'] in ('high', 'critical')
        assert len(res['possible_connections']) >= 2
        assert len(res['exposure_scenarios']) >= 1
        scenario_titles = [s['title'] for s in res['exposure_scenarios']]
        assert any('School Affiliation' in t for t in scenario_titles)
        assert any('Routine' in t for t in scenario_titles)

    def test_identity_and_location(self):
        findings = [
            {'category': 'Human face'},
            {'category': 'Possible address'},
        ]
        res = explain_exposure(findings)
        assert res['risk_level'] == 'high'
        assert any('location clue' in c for c in res['possible_connections'])

    def test_credentials_critical(self):
        findings = [
            {'category': 'Credential assignment'},
            {'category': 'Email address'}
        ]
        res = explain_exposure(findings)
        assert res['risk_level'] == 'critical'
        assert any('Credential' in s['title'] for s in res['exposure_scenarios'])

    def test_empty_findings(self):
        res = explain_exposure([])
        assert res['risk_level'] == 'low'
        assert len(res['possible_connections']) == 0
