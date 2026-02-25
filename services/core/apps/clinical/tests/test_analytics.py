"""
Tests for clinical analytics: clustering engine, stats module, traceback graph.
"""

import pytest
from datetime import date
from django.test import TestCase

from apps.clinical.models import (
    ClinicalCase,
    ClinicalExposure,
    OutbreakInvestigation,
    ReportingInstitution,
)
from apps.clinical.clustering import detect_clusters, _cluster_score, _temporal_concentration
from apps.clinical.stats import analyze_investigation, _odds_ratio, _or_95ci


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _inst():
    inst, _ = ReportingInstitution.objects.get_or_create(
        api_key_hash="a" * 64,
        defaults={"name": "Test Lab", "institution_type": "lab"},
    )
    return inst


def _case(**kwargs) -> ClinicalCase:
    defaults = dict(
        reporting_institution=_inst(),
        subject_hash="x" * 64,
        age_range="30-39",
        zip3="941",
        geohash="9q5f2",
        onset_date=date(2026, 2, 1),
        symptoms=["diarrhea", "fever"],
        pathogen="Salmonella",
        illness_status="confirmed",
    )
    defaults.update(kwargs)
    return ClinicalCase.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

class TestOddsRatio(TestCase):
    def test_basic_or(self):
        # a=10, b=5, c=2, d=8  → OR = (10*8)/(5*2) = 8
        assert _odds_ratio(10, 5, 2, 8) == pytest.approx(8.0)

    def test_zero_denominator_returns_none(self):
        assert _odds_ratio(10, 0, 2, 8) is None

    def test_ci_symmetric_around_log_or(self):
        import math
        lo, hi = _or_95ci(20, 10, 5, 15)
        assert lo is not None and hi is not None
        assert lo < 1.0 or hi > 1.0  # CI exists
        # CI is asymmetric on natural scale but symmetric on log scale
        log_mid = (math.log(lo) + math.log(hi)) / 2
        assert log_mid == pytest.approx(math.log(_odds_ratio(20, 10, 5, 15)), abs=0.01)

    def test_zero_cell_ci_returns_none(self):
        lo, hi = _or_95ci(0, 10, 5, 15)
        assert lo is None
        assert hi is None


# ---------------------------------------------------------------------------
# Clustering algorithm
# ---------------------------------------------------------------------------

class TestClusteringEngine(TestCase):
    @pytest.mark.django_db
    def test_temporal_concentration_single_date(self):
        # All cases on same day → max concentration score = 10
        dates = [date(2026, 2, 1)] * 5
        assert _temporal_concentration(dates) == pytest.approx(10.0)

    @pytest.mark.django_db
    def test_temporal_concentration_spread(self):
        # Cases spread over 30 days → lower concentration
        dates = [date(2026, 1, i) for i in range(1, 31)]
        score = _temporal_concentration(dates)
        assert score < 5.0

    @pytest.mark.django_db
    def test_detect_creates_investigation(self):
        # Create 3 cases with same pathogen + geohash prefix
        for i in range(3):
            _case(
                subject_hash=f"{i:x}" * 16,
                geohash="9q5f2",
                pathogen="Salmonella",
                onset_date=date(2026, 2, 1),
            )

        result = detect_clusters(lookback_days=30)
        assert result["created"] >= 1
        # Investigation should exist now
        assert OutbreakInvestigation.objects.filter(
            auto_generated=True, pathogen__iexact="salmonella"
        ).exists()

    @pytest.mark.django_db
    def test_detect_skips_small_clusters(self):
        # Only 2 cases — below threshold of 3
        for i in range(2):
            _case(
                subject_hash=f"aa{i}" * 16,
                geohash="zzzz1",
                pathogen="NorovirusTest",
                onset_date=date(2026, 2, 10),
            )

        before = OutbreakInvestigation.objects.filter(pathogen__iexact="norovirustest").count()
        detect_clusters(lookback_days=30)
        after = OutbreakInvestigation.objects.filter(pathogen__iexact="norovirustest").count()
        assert before == after

    @pytest.mark.django_db
    def test_detect_links_cases_to_investigation(self):
        cases = [
            _case(
                subject_hash=f"bb{i}" * 16,
                geohash="9q8v1",
                pathogen="E. coli O157:H7",
                onset_date=date(2026, 2, 5),
            )
            for i in range(4)
        ]
        detect_clusters(lookback_days=30)
        for c in cases:
            c.refresh_from_db()
            assert c.investigation_id is not None

    @pytest.mark.django_db
    def test_detect_idempotent_on_second_run(self):
        for i in range(3):
            _case(
                subject_hash=f"cc{i}" * 16,
                geohash="9q5e1",
                pathogen="Listeria",
                onset_date=date(2026, 2, 8),
            )

        result1 = detect_clusters(lookback_days=30)
        result2 = detect_clusters(lookback_days=30)

        # Second run should update, not create a second investigation
        assert result1["created"] == 1
        assert result2["created"] == 0
        assert result2["updated"] == 1


# ---------------------------------------------------------------------------
# Stats module
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAnalyzeInvestigation(TestCase):
    def setUp(self):
        self.inv = OutbreakInvestigation.objects.create(
            title="Test Investigation",
            status="open",
            pathogen="Salmonella",
            auto_generated=False,
        )

    def _make_case(self, subject_suffix, symptoms, illness_status="confirmed", with_exposure=None):
        case = _case(
            subject_hash=f"{subject_suffix}" * 4,
            geohash="9q5f2",
            pathogen="Salmonella",
            onset_date=date(2026, 2, 1),
            symptoms=symptoms,
            illness_status=illness_status,
            investigation=self.inv,
        )
        if with_exposure:
            ClinicalExposure.objects.create(
                case=case,
                exposure_type=with_exposure,
                food_items=["chicken"],
                confidence="high",
            )
        return case

    def test_symptom_frequencies_returned(self):
        self._make_case("aa11111111111111", ["diarrhea", "fever"])
        self._make_case("bb22222222222222", ["diarrhea", "vomiting"])
        self._make_case("cc33333333333333", ["diarrhea"])

        result = analyze_investigation(self.inv.pk)
        symptom_map = {s["symptom"]: s for s in result["symptom_frequencies"]}

        assert "diarrhea" in symptom_map
        assert symptom_map["diarrhea"]["count"] == 3
        assert symptom_map["diarrhea"]["percent"] == pytest.approx(100.0)

    def test_exposure_analysis_returned(self):
        self._make_case("dd44444444444444", ["fever"], with_exposure="restaurant")
        self._make_case("ee55555555555555", ["fever"], with_exposure="restaurant")
        self._make_case("ff66666666666666", ["fever"], illness_status="suspected")

        result = analyze_investigation(self.inv.pk)
        exp_types = [e["exposure_type"] for e in result["exposure_analysis"]]
        assert "restaurant" in exp_types

    def test_case_summary_counts(self):
        self._make_case("gg77777777777777", ["fever"], illness_status="confirmed")
        self._make_case("hh88888888888888", ["fever"], illness_status="suspected")
        self._make_case("ii99999999999999", ["fever"], illness_status="ruled_out")

        result = analyze_investigation(self.inv.pk)
        summary = result["case_summary"]
        assert summary["confirmed"] >= 1
        assert summary["suspected"] >= 1
        assert summary["ruled_out"] >= 1
        assert summary["total"] >= 3

    def test_generated_at_present(self):
        result = analyze_investigation(self.inv.pk)
        assert "generated_at" in result
        assert result["generated_at"]


# ---------------------------------------------------------------------------
# Traceback graph
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestTracebackGraph(TestCase):
    def test_empty_investigation_returns_graph(self):
        from apps.clinical.traceback import build_traceback
        inv = OutbreakInvestigation.objects.create(
            title="Empty Inv",
            status="open",
            auto_generated=False,
        )
        graph = build_traceback(investigation_id=inv.pk)
        assert "nodes" in graph
        assert "edges" in graph
        assert "summary" in graph
        assert graph["summary"]["case_count"] == 0

    def test_graph_contains_case_nodes(self):
        from apps.clinical.traceback import build_traceback
        inv = OutbreakInvestigation.objects.create(
            title="Graph Test",
            status="open",
            auto_generated=True,
        )
        case = _case(subject_hash="jj" * 32, investigation=inv, geohash="9q5f2")

        graph = build_traceback(investigation_id=inv.pk)
        node_types = {n["type"] for n in graph["nodes"]}
        assert "case" in node_types
        assert graph["summary"]["case_count"] == 1

    def test_graph_with_exposure_and_recall(self):
        from apps.clinical.traceback import build_traceback
        from apps.recalls.models import Recall

        recall = Recall.objects.create(
            source=Recall.Source.FDA,
            external_id="TB-TEST-001",
            title="Traceback Recall",
            reason="Salmonella contamination",
            recalling_firm="Test Corp",
            status=Recall.Status.ACTIVE,
            affected_states=["CA"],
        )

        inv = OutbreakInvestigation.objects.create(
            title="Traceback Inv",
            status="open",
            auto_generated=True,
        )
        case = _case(subject_hash="kk" * 32, investigation=inv, geohash="9q5f2")
        exp = ClinicalExposure.objects.create(
            case=case,
            exposure_type="restaurant",
            geohash="9q5f",
            food_items=["chicken"],
            linked_recall=recall,
        )

        graph = build_traceback(investigation_id=inv.pk)
        node_types = {n["type"] for n in graph["nodes"]}
        assert "exposure" in node_types
        assert "recall" in node_types
        # Recall node label should contain recall title fragment
        recall_nodes = [n for n in graph["nodes"] if n["type"] == "recall"]
        assert any("Traceback Recall" in n["label"] for n in recall_nodes)
