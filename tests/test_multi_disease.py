"""The disease-agnostic claim, tested against both registered diseases.

The design stack previously claimed to be disease-agnostic on the strength of
one registry entry, while its own modules imported MS-specific scoring. These
tests hold the claim to something checkable: the same code path must derive a
sensible profile, Hamiltonian, and molecule for two diseases whose pathways,
therapeutic axes, and safety vocabularies have nothing in common.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.design.denovo import DesignWeights, run_design
from core.design.evidence import ASSESSMENT_AXES, evidence_status
from core.design.pharmacophores import load_library, unreachable_requirements
from core.design.quantum_assembly import build_selection_problem, solve_enumeration
from core.design.target_profile import build_target_profile
from core.models.disease import available_diseases, load_disease

ROOT = Path(__file__).resolve().parents[1]
DISEASES = ["multiple_sclerosis", "parkinsons", "alzheimers", "epilepsy", "guillain_barre"]


@pytest.fixture(scope="module")
def library():
    return load_library()


@pytest.mark.parametrize("identifier", DISEASES)
def test_registry_entry_loads_all_of_its_data(identifier):
    disease = load_disease(identifier)
    assert disease.signature().genes
    assert disease.network().number_of_nodes() > 0
    assert disease.panel()
    assert disease.druggability()


def test_registry_holds_more_than_one_disease():
    """The generality claim needs at least two instances to be checkable."""
    assert set(DISEASES) <= set(available_diseases())


def test_the_two_diseases_have_largely_different_safety_vocabularies():
    """Safety burden is a property of the disease, not of the scoring code.

    MS therapy is constrained by infection, malignancy, and autoimmunity;
    Parkinson's by dyskinesia, impulse-control disorders, and psychosis. The
    two overlap only on generic organ toxicity -- cardiac and hepatic -- which
    genuinely applies to both. What the registry has to carry is the majority
    that does not transfer.
    """
    ms = set(load_disease("multiple_sclerosis").risk_domains)
    pd = set(load_disease("parkinsons").risk_domains)
    assert ms - pd and pd - ms
    shared = ms & pd
    assert shared <= {"cardiac", "hepatic"}, f"unexpected shared domains: {shared}"
    assert len(shared) < min(len(ms), len(pd)) / 2


def test_the_two_diseases_share_no_therapeutic_axes():
    ms = set(load_disease("multiple_sclerosis").therapeutic_axes)
    pd = set(load_disease("parkinsons").therapeutic_axes)
    assert not (ms & pd)


def test_no_two_diseases_share_a_therapeutic_axis():
    """Pairwise, across every registered disease, not just the first two.

    The claim that the vocabulary belongs to the disease is only tested if a
    new entry cannot quietly reuse an old one's axes.
    """
    from itertools import combinations

    for a, b in combinations(DISEASES, 2):
        shared = set(load_disease(a).therapeutic_axes) & set(load_disease(b).therapeutic_axes)
        assert not shared, f"{a} and {b} share therapeutic axes: {shared}"


def test_risk_domains_overlap_only_on_generic_organ_toxicity():
    """Alzheimer's adds ARIA, bradycardia and cognitive worsening; none transfer.

    Cardiac, hepatic and gastrointestinal toxicity genuinely apply to every
    disease. Teratogenicity joined the generic set when epilepsy was registered:
    MS and epilepsy both weigh it (teriflunomide; valproate), because it applies
    to any chronic therapy in women of childbearing age. That was a decision to
    widen this test, made because the fourth disease genuinely shares the
    domain, and the alternative of renaming the domain to pass would have been
    the vocabulary check being gamed. Anything else two diseases share fails.
    """
    from itertools import combinations

    generic = {"cardiac", "hepatic", "gastrointestinal", "teratogenicity"}
    for a, b in combinations(DISEASES, 2):
        shared = set(load_disease(a).risk_domains) & set(load_disease(b).risk_domains)
        assert shared <= generic, f"{a} and {b} share non-generic risk domains: {shared - generic}"


@pytest.mark.parametrize("identifier", DISEASES)
def test_risk_weights_come_from_the_registry(identifier):
    disease = load_disease(identifier)
    assert set(disease.risk_weights) == set(disease.risk_domains)
    assert all(0.0 <= v <= 1.0 for v in disease.risk_weights.values())


def test_design_modules_do_not_import_disease_specific_scoring():
    """The import graph is part of the claim.

    A layer that says it is disease-agnostic while importing ``ms_scoring`` is
    not, whatever its registry contains.
    """
    for path in (ROOT / "core/design").glob("*.py"):
        assert "ms_scoring" not in path.read_text(), path
    assert "ms_scoring" not in (ROOT / "core/models/disease.py").read_text()


@pytest.mark.parametrize("identifier", DISEASES)
def test_each_disease_declares_a_novelty_reference_set(identifier):
    """Novelty is only as meaningful as the set it is measured against.

    Parkinson's shipped its first design campaign without one, so its designs
    were compared only against the pharmacophore library's own parent
    fragments. A candidate could be reported novel while closely resembling an
    approved drug for the disease -- with no symptom anywhere in the output.
    The reference set must exist and must actually cover the panel's small
    molecules.
    """
    disease = load_disease(identifier)
    structures = disease.known_structures()
    assert structures, f"{identifier} declares no known-structure reference set"
    named = {name for name, _ in structures}
    panel_names = {d["name"] for d in disease.panel()}
    assert len(named & panel_names) >= len(structures) // 2, (
        f"{identifier} reference set barely overlaps its own panel"
    )


@pytest.mark.parametrize("identifier", DISEASES)
def test_novelty_is_measured_against_real_drugs_not_only_fragments(identifier, library):
    """The reference set must add agents the fragment library does not contain.

    If every structure came from the library's own parents, registering the
    file would change nothing and the hole would still be open.
    """
    disease = load_disease(identifier)
    known = {smiles for _, smiles in disease.known_structures()}
    parents = {smiles for _, smiles in library.parent_structures()}
    assert known - parents


@pytest.mark.parametrize("identifier", DISEASES)
def test_profile_derives_and_ranks_for_each_disease(identifier, library):
    profile = build_target_profile(load_disease(identifier), top_n=12)
    assert profile.requirements
    priorities = [r.priority for r in profile.requirements]
    assert priorities == sorted(priorities, reverse=True)
    assert profile.property_window.rationale


@pytest.mark.parametrize("identifier", DISEASES)
def test_each_disease_has_a_fully_served_and_an_unserved_axis(identifier):
    """Every disease has effective symptomatic therapy and little disease modification.

    The gap analysis should find that shape without being told it: one axis
    fully served, and at least one that is mostly unmet.

    This originally asserted a gap of exactly 1.00. Epilepsy is the first disease
    with no axis at 1.00, because everolimus (approved for TSC-associated
    seizures) and retigabine (approved, then withdrawn in 2017) give even its
    unserved axes some approved cover. The threshold was relaxed to 0.8 for that
    reason, not to make a test pass: the shape claim still holds. It also
    exposes the withdrawal blind spot, since a withdrawn drug still counts as
    cover here.
    """
    profile = build_target_profile(load_disease(identifier), top_n=12)
    gaps = profile.axis_gaps
    assert min(gaps.values()) == pytest.approx(0.0)
    assert max(gaps.values()) >= 0.8


def test_parkinsons_routes_around_its_least_tractable_central_target():
    """Alpha-synuclein is the central protein in PD and is not small-molecule tractable.

    The profile must not put a designed arm on it just because its leverage is
    high -- the same guard that keeps MS designs off CD20.
    """
    disease = load_disease("parkinsons")
    assert disease.druggability()["SNCA"]["small_molecule_tractability"] < 0.3
    profile = build_target_profile(disease, top_n=8)
    assert "SNCA" not in profile.genes


def test_alzheimers_routes_around_both_of_its_defining_proteins():
    """Tau and APP are the disease and are the two proteins a small molecule reaches worst.

    Tau is intrinsically disordered and APP is a substrate, not an enzyme. The
    profile must reach amyloid and tau through the secretases and the tau
    kinases instead, exactly as the clinical field has tried to, and must not
    point a designed arm at either protein because its leverage is high.
    """
    disease = load_disease("alzheimers")
    druggability = disease.druggability()
    assert druggability["MAPT"]["small_molecule_tractability"] < 0.3
    assert druggability["APP"]["small_molecule_tractability"] < 0.3
    profile = build_target_profile(disease, top_n=14)
    assert "MAPT" not in profile.genes and "APP" not in profile.genes
    assert {"BACE1", "GSK3B"} <= set(profile.genes)


def test_alzheimers_tractability_is_scored_in_the_direction_the_signature_wants():
    """An inhibitor-only target that must go UP is not a tractable target.

    AKT1, BCL2, CAMK2A, GPX4, SIRT1 and HMOX1 all have small-molecule precedent
    as inhibitors, and all need to increase in Alzheimer's. Scoring them at
    their inhibitor precedent would put an arm on a target the chemistry cannot
    drive in the wanted direction.
    """
    disease = load_disease("alzheimers")
    signature = disease.signature()
    druggability = disease.druggability()
    for gene in ("AKT1", "BCL2", "CAMK2A", "GPX4", "SIRT1", "HMOX1"):
        assert signature.desired[gene] == 1
        assert druggability[gene]["small_molecule_tractability"] < 0.4, gene


def test_alzheimers_panel_names_every_amyloid_antibody_as_low_cns_but_not_zero():
    """Anti-amyloid antibodies reach the brain at about one per cent and still work.

    Modelling them at zero exposure would rank the only approved
    disease-modifying agents below drugs that failed; modelling them like small
    molecules would overstate them. The registry states the reasoning.
    """
    disease = load_disease("alzheimers")
    panel = {d["name"]: d for d in disease.panel()}
    for name in ("Lecanemab", "Donanemab", "Aducanumab", "Gantenerumab"):
        assert 0.0 < panel[name]["cns_penetration"] <= 0.2
        assert panel[name]["route"] in ("infusion", "subcutaneous")
    assert "antibod" in disease.delivery.sanctuary_rationale


def test_epilepsy_scores_tractability_in_the_wanted_direction():
    """Targets that must be RAISED and have only inhibitor precedent are hard targets.

    GAD1/2, KCC2, EAAT2, Kir4.1 and Nav1.1 all need to go up in epilepsy. The
    channel targets that must be blocked or opened (Nav1.2, Kv7, alpha2delta)
    are among the most tractable in the registry, and the contrast is the point.
    """
    disease = load_disease("epilepsy")
    signature = disease.signature()
    druggability = disease.druggability()
    for gene in ("GAD1", "GAD2", "SLC12A5", "SLC1A2", "KCNJ10", "SCN1A", "TSC2"):
        assert signature.desired[gene] == 1
        assert druggability[gene]["small_molecule_tractability"] < 0.4, gene
    for gene in ("SCN2A", "KCNQ2", "CACNA2D1", "CA2"):
        assert druggability[gene]["small_molecule_tractability"] >= 0.85, gene


def test_epilepsy_excludes_pairs_that_share_a_sodium_channel_mechanism():
    """Rational polytherapy avoids two sodium-channel blockers; the screen should too.

    Carbamazepine and lamotrigine act on the same channel family and share a
    safety class, so the redundancy rule must exclude them. Carbamazepine with a
    mechanistically different agent must not be excluded.
    """
    from core.biology.combination_scoring import CombinationConfig, redundancy_flags

    panel = {d["name"]: d for d in load_disease("epilepsy").panel()}
    config = CombinationConfig()
    same = redundancy_flags([panel["Carbamazepine"], panel["Lamotrigine"]], config)
    different = redundancy_flags([panel["Carbamazepine"], panel["Levetiracetam"]], config)
    assert same["excluded_from_primary_ranking"] and not different["excluded_from_primary_ranking"]


def test_epilepsy_names_teratogenicity_as_its_heaviest_risk():
    """Valproate's fetal risk reshaped prescribing, and the registry must say so."""
    disease = load_disease("epilepsy")
    assert max(disease.risk_weights, key=disease.risk_weights.get) == "teratogenicity"
    panel = {d["name"]: d for d in disease.panel()}
    assert panel["Valproate"]["safety_burden"]["teratogenicity"] == 1.0


def test_guillain_barre_is_the_only_peripheral_disease():
    """The CNS gate is a registry decision, and one disease must switch it off.

    Guillain-Barre attacks peripheral nerve, so nothing has to cross the
    blood-brain barrier. It is the first registered disease to exercise the
    branch of the delivery logic that the other four never reach, and the
    profile's property window must reflect that (no CNS floor).
    """
    peripheral = load_disease("guillain_barre")
    assert not peripheral.delivery.requires_cns_exposure
    window = build_target_profile(peripheral, top_n=12).property_window
    assert window.cns_mpo_floor == 0.0
    for identifier in ("multiple_sclerosis", "parkinsons", "alzheimers", "epilepsy"):
        assert load_disease(identifier).delivery.requires_cns_exposure, identifier


def test_guillain_barre_routes_around_its_protein_therapeutic_targets():
    """The disease's centre of gravity is C1q, C5, IgG and FcRn, and none is a small-molecule target.

    Immunoglobulin, plasma exchange and the antibody candidates all act there.
    The profile must reach the disease through targets on its edges (the C5a
    receptor, sodium channels, Kv1.1) and must not point a designed arm at
    the protein targets because their leverage is high.
    """
    disease = load_disease("guillain_barre")
    druggability = disease.druggability()
    for gene in ("C1QA", "C5", "FCGRT", "IGHG1"):
        assert druggability[gene]["small_molecule_tractability"] < 0.3, gene
    profile = build_target_profile(disease, top_n=14)
    assert not {"C1QA", "C5", "FCGRT", "IGHG1"} & set(profile.genes)
    assert "C5AR1" in profile.genes


def test_guillain_barre_reference_set_is_small_because_the_treatments_are_not_small_molecules():
    """A structural fact about the disease, and a limit on what its novelty numbers mean."""
    disease = load_disease("guillain_barre")
    named = {name for name, _ in disease.known_structures()}
    assert "Intravenous immunoglobulin" not in named and "Plasma exchange" not in named
    assert len(named) < len(disease.panel()) / 2


def test_guillain_barre_weights_respiratory_depression_highest():
    """The disease weakens the respiratory muscles, so a sedating pain drug can tip a patient over."""
    disease = load_disease("guillain_barre")
    assert max(disease.risk_weights, key=disease.risk_weights.get) == "respiratory_depression"


def test_guillain_barre_excludes_the_two_alpha2delta_agents_as_duplicates():
    from core.biology.combination_scoring import CombinationConfig, redundancy_flags

    panel = {d["name"]: d for d in load_disease("guillain_barre").panel()}
    flags = redundancy_flags([panel["Gabapentin"], panel["Pregabalin"]], CombinationConfig())
    assert flags["excluded_from_primary_ranking"] and flags["same_mechanism"]


def test_gene_aliases_recover_a_target_the_interactome_names_differently():
    """STRING still calls glucocerebrosidase GBA; HGNC calls it GBA1.

    Unmapped, the most common genetic risk factor in PD would have zero
    network leverage and drop out of the profile silently.
    """
    disease = load_disease("parkinsons")
    assert disease.gene_aliases.get("GBA") == "GBA1"
    assert "GBA1" in disease.network()
    assert "GBA1" in build_target_profile(disease, top_n=14).genes


@pytest.mark.parametrize("identifier", DISEASES)
def test_hamiltonian_builds_and_solves_for_each_disease(identifier, library):
    profile = build_target_profile(load_disease(identifier), top_n=12)
    problem = build_selection_problem(profile, library, k=2, max_variables=8)
    best = solve_enumeration(problem, top=1)[0]
    assert best.feasible
    assert len(best.identifiers) == 2


@pytest.mark.parametrize("identifier", DISEASES)
def test_a_molecule_is_produced_for_each_disease(identifier, library):
    """The end-to-end claim: registry entry in, novel structure out."""
    from core.chemistry.molecule import parse_smiles

    disease = load_disease(identifier)
    profile = build_target_profile(disease, top_n=12)
    problem = build_selection_problem(profile, library, k=2, max_variables=8)
    arms = [s.identifiers for s in solve_enumeration(problem, top=1)]
    result = run_design(
        disease=disease, profile=profile, library=library, arm_sets=arms,
        weights=DesignWeights(), seed=7, top=3, iterations=20,
    )
    assert result["candidates"]
    for candidate in result["candidates"]:
        parse_smiles(candidate["smiles"])
        assert candidate["molecular_formula"]


@pytest.mark.parametrize("identifier", DISEASES)
def test_unreachable_requirements_are_reported_not_hidden(identifier, library):
    """A profile target with no chemical matter is the most useful thing a run says."""
    profile = build_target_profile(load_disease(identifier), top_n=14)
    unreachable = unreachable_requirements(library, profile.genes)
    assert isinstance(unreachable, list)
    assert not set(unreachable) - set(profile.genes)


# ---------------------------------------------------------------------------
# Evidence and provenance
# ---------------------------------------------------------------------------

def test_every_pharmacophore_declares_its_evidence_and_primary_targets(library):
    for fragment in library.pharmacophores:
        assert fragment.evidence_tier in (
            "approved_drug", "clinical_candidate", "published_chemotype", "speculative"
        )
        assert fragment.primary_targets
        assert not set(fragment.primary_targets) - set(fragment.engages)


def test_a_binding_claim_outranks_a_downstream_claim_from_the_same_fragment(library):
    """Otherwise a scaffold of speculative inference scores like real pharmacology."""
    fragment = library.get("nrf2_fumarate")
    primary = fragment.claim_confidence("NFE2L2")
    downstream = fragment.claim_confidence("NQO1")
    assert primary > downstream > 0


def test_approved_chemotypes_outrank_speculative_ones(library):
    assert (
        library.get("maob_propargylamine").mean_confidence
        > library.get("sirt_polyphenol").mean_confidence
    )


def test_confidence_weighting_reduces_coverage_for_weak_evidence(library):
    """The optimiser must have a reason to prefer well-evidenced arms."""
    from core.design.quantum_assembly import combined_confidence, profile_coverage

    profile = build_target_profile(load_disease("multiple_sclerosis"), top_n=14)
    fragment = library.get("gpr17_indole_acid")
    unweighted = profile_coverage(fragment.engages, profile)
    weighted = profile_coverage(fragment.engages, profile, combined_confidence([fragment]))
    assert 0 < weighted < unweighted


def test_designs_carry_a_machine_readable_evidence_status(library):
    """Caveats in a protocol do not travel with the data; this field does."""
    status = evidence_status().as_dict()
    assert status["readiness"] == "hypothesis_only"
    assert set(status["unassessed"]) == set(ASSESSMENT_AXES)
    for axis in ("target_binding", "efflux_liability", "cardiac_safety", "synthetic_route"):
        assert axis in status["detail"]


def test_provenance_records_input_digests_and_a_dirty_tree_flag():
    """A revision hash from a modified tree describes code that never existed."""
    from core.provenance import run_provenance

    payload = run_provenance(
        [ROOT / "data/ms_expression_v3.csv"], command=["pytest"]
    )
    assert payload["artifact_class"] == "run_snapshot"
    assert payload["inputs"][0]["sha256"]
    assert "dirty" in payload["git"]
    assert payload["environment"]["chemistry_backend"]["active"] in ("rdkit", "local")


def test_input_digest_changes_when_a_file_changes(tmp_path):
    from core.provenance import file_digest

    path = tmp_path / "signature.csv"
    path.write_text("gene,logFC,desired_direction\nA,1.0,-1\n")
    before = file_digest(path)["sha256"]
    path.write_text("gene,logFC,desired_direction\nA,1.1,-1\n")
    assert file_digest(path)["sha256"] != before
