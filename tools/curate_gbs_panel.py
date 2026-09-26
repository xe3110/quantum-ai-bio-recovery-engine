"""Curate and validate the Guillain-Barre syndrome candidate panel.

The fifth disease in the registry, and the first that is **peripheral**. The
four earlier diseases all set ``requires_cns_exposure``; Guillain-Barre attacks
peripheral nerve and nerve roots, so the delivery constraint is switched off and
the compartment term is scored as spread instead of CNS coverage. That is the
branch of the delivery logic no earlier disease exercised.

It is also the disease whose established treatments are not small molecules at
all. Intravenous immunoglobulin and plasma exchange, the two approved therapies,
are a biologic and a procedure; the newest candidates are antibodies and enzymes
against complement, IgG and FcRn. The evidence base is also small. Only a
handful of randomised trials exist, so the panel is deliberately short (16
agents) rather than padded with agents that have never been tested in the
disease. What is in it was checked against sources: which trials happened and how
they came out.

The safety vocabulary is unlike any earlier disease's: thromboembolism and renal
injury from immunoglobulin, meningococcal infection from complement inhibition,
treatment-related fluctuation (relapse after an initial response), and
respiratory depression, which matters because the disease itself weakens the
respiratory muscles.

As with the earlier curation tools, this **fails the build** if any target gene
is absent from the disease signature.

Run: python -m tools.curate_gbs_panel
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNATURE = ROOT / "data/gbs_expression.csv"
OUT = ROOT / "data/drugs/guillain_barre_panel_v1.json"

RISK_DOMAINS = (
    "thromboembolic_events", "renal_injury", "meningococcal_infection",
    "immune_haemolysis", "treatment_related_fluctuation",
    "respiratory_depression", "cardiac", "hepatic",
)
AXES = (
    "complement_inhibition", "antibody_clearance", "fc_receptor_modulation",
    "cytokine_immune_modulation", "conduction_restoration",
    "neuropathic_pain_relief", "nerve_repair_promotion",
)


def d(**kw):
    """Build one panel record, filling the risk vector with declared zeros."""
    burden = {k: 0.0 for k in RISK_DOMAINS}
    burden.update(kw.pop("risk", {}))
    kw["safety_burden"] = burden
    kw.setdefault("target_family", kw["mechanism_class"])
    kw.setdefault("pathways", [])
    kw["relevant_pathways"] = kw["pathways"]
    return kw


COMP = "complement_cascade"
FC = "autoantibody_fc_receptor"
CYT = "t_cell_cytokine"
BNB = "blood_nerve_barrier"
PAIN = "neuropathic_pain_excitability"
NODE = "nodal_paranodal"

DRUGS = [
 # --- the two approved disease-specific therapies -------------------------
 d(name="Intravenous immunoglobulin", mechanism_class="polyclonal_immunoglobulin", primary_moa="Pooled IgG: Fc-receptor blockade, complement scavenging, FcRn saturation and anti-idiotypic neutralisation",
   evidence_tier="approved", indication="standard_of_care", route="infusion", cns_penetration=0.02, compartment="peripheral",
   therapeutic_axes=["fc_receptor_modulation", "complement_inhibition", "antibody_clearance"], half_life_class="long",
   safety_classes=["immunoglobulin_product"], target_uncertainty=0.25, pathways=[FC, COMP, CYT],
   risk={"thromboembolic_events":0.6,"renal_injury":0.4,"immune_haemolysis":0.3,"treatment_related_fluctuation":0.3},
   target_effects={"FCGR2B":0.5,"FCGR3A":-0.4,"FCGR1A":-0.3,"FCGRT":-0.4,"C3":-0.3,"C1QA":-0.3,"IGHG1":-0.35,"TNF":-0.25,"IL6":-0.2,"FOXP3":0.2}),
 d(name="Plasma exchange", mechanism_class="plasmapheresis", primary_moa="Removes autoantibody, complement and cytokines from plasma",
   evidence_tier="approved", indication="standard_of_care", route="plasmapheresis", cns_penetration=0.02, compartment="peripheral",
   therapeutic_axes=["antibody_clearance", "complement_inhibition", "cytokine_immune_modulation"], half_life_class="short",
   safety_classes=["extracorporeal_procedure"], target_uncertainty=0.25, pathways=[FC, COMP, CYT],
   risk={"cardiac":0.5,"thromboembolic_events":0.3,"treatment_related_fluctuation":0.4},
   target_effects={"C3":-0.4,"C1QA":-0.35,"C5":-0.25,"IGHG1":-0.6,"TNF":-0.3,"IL6":-0.25,"IFNG":-0.2,"CXCL10":-0.2}),
 d(name="IVIG, second course (SID-GBS)", mechanism_class="polyclonal_immunoglobulin", primary_moa="A second immunoglobulin course for patients with a poor prognosis; the randomised trial found no benefit and more serious adverse events (35% against 16%), including thromboembolism",
   evidence_tier="phase_3", indication="failed", route="infusion", cns_penetration=0.02, compartment="peripheral",
   therapeutic_axes=["fc_receptor_modulation", "complement_inhibition", "antibody_clearance"], half_life_class="long",
   safety_classes=["immunoglobulin_product"], target_uncertainty=0.3, pathways=[FC, COMP, CYT],
   risk={"thromboembolic_events":0.9,"renal_injury":0.5,"immune_haemolysis":0.4,"treatment_related_fluctuation":0.3},
   target_effects={"FCGR2B":0.5,"FCGR3A":-0.4,"FCGR1A":-0.3,"FCGRT":-0.4,"C3":-0.3,"C1QA":-0.3,"IGHG1":-0.35,"TNF":-0.25,"IL6":-0.2,"FOXP3":0.2}),
 # --- antibody clearance candidates ---------------------------------------
 d(name="Efgartigimod", mechanism_class="fcrn_antagonist", primary_moa="FcRn antagonist lowering circulating IgG; approved for CIDP, in a randomised phase 2 against IVIG in GBS",
   evidence_tier="phase_2", indication="candidate", route="infusion", cns_penetration=0.02, compartment="peripheral",
   therapeutic_axes=["antibody_clearance"], half_life_class="short",
   safety_classes=["igg_lowering"], target_uncertainty=0.4, pathways=[FC],
   risk={"treatment_related_fluctuation":0.2},
   target_effects={"FCGRT":-0.85,"IGHG1":-0.6,"C1QA":-0.15}),
 d(name="Imlifidase", mechanism_class="igg_cleaving_enzyme", primary_moa="IgG-cleaving enzyme; a phase 2 with IVIG showed rapid recovery against an external comparison and was safe and well tolerated",
   evidence_tier="phase_2", indication="candidate", route="infusion", cns_penetration=0.02, compartment="peripheral",
   therapeutic_axes=["antibody_clearance", "fc_receptor_modulation"], half_life_class="short",
   safety_classes=["igg_cleaving"], target_uncertainty=0.45, pathways=[FC, COMP],
   risk={"treatment_related_fluctuation":0.5,"cardiac":0.2,"hepatic":0.1},
   target_effects={"IGHG1":-0.85,"FCGR3A":-0.2,"C1QA":-0.2,"C3":-0.15}),
 # --- complement ------------------------------------------------------------
 d(name="Eculizumab", mechanism_class="anti_c5_antibody", primary_moa="C5 antibody; a 33-patient randomised phase 2 (JET-GBS) was too small to prove efficacy, and it is approved in other diseases",
   evidence_tier="phase_2", indication="inconclusive", route="infusion", cns_penetration=0.02, compartment="peripheral",
   therapeutic_axes=["complement_inhibition"], half_life_class="long",
   safety_classes=["terminal_complement_inhibition"], target_uncertainty=0.4, pathways=[COMP],
   risk={"meningococcal_infection":0.95},
   target_effects={"C5":-0.9,"C5AR1":-0.5}),
 d(name="Tanruprubart (ANX005)", mechanism_class="anti_c1q_antibody", primary_moa="C1q antibody blocking the classical pathway; positive phase 3 (2.4-fold improvement on the GBS disability scale at week 8, p = 0.0058)",
   evidence_tier="phase_3", indication="candidate", route="infusion", cns_penetration=0.02, compartment="peripheral",
   therapeutic_axes=["complement_inhibition"], half_life_class="long",
   safety_classes=["classical_complement_inhibition"], target_uncertainty=0.3, pathways=[COMP],
   risk={"meningococcal_infection":0.3,"cardiac":0.1},
   target_effects={"C1QA":-0.9,"C1QB":-0.8,"C1QC":-0.8,"C1S":-0.5,"C3":-0.55,"C5":-0.45,"C5AR1":-0.3}),
 d(name="C5aR antagonist (avacopan-class exemplar)", mechanism_class="c5ar_antagonist", primary_moa="Oral C5a receptor antagonist; evidence extrapolated from ANCA vasculitis, with none in GBS",
   evidence_tier="phase_2", indication="disease_modifying", route="oral", cns_penetration=0.1, compartment="peripheral",
   therapeutic_axes=["complement_inhibition", "cytokine_immune_modulation"], half_life_class="intermediate",
   safety_classes=["c5ar_antagonism"], target_uncertainty=0.55, pathways=[COMP, CYT],
   risk={"hepatic":0.4,"meningococcal_infection":0.1},
   target_effects={"C5AR1":-0.85,"CD68":-0.2,"TNF":-0.15,"ICAM1":-0.15}),
 # --- immunomodulators that were tried, and failed ----------------------------
 d(name="Methylprednisolone", mechanism_class="glucocorticoid", primary_moa="Intravenous glucocorticoid; a 242-patient randomised trial found no benefit over placebo",
   evidence_tier="phase_3", indication="failed", route="infusion", cns_penetration=0.3, compartment="peripheral",
   therapeutic_axes=["cytokine_immune_modulation"], half_life_class="short",
   safety_classes=["glucocorticoid_class"], target_uncertainty=0.2, pathways=[CYT, BNB],
   risk={"cardiac":0.3,"thromboembolic_events":0.2,"hepatic":0.1},
   target_effects={"TNF":-0.4,"IL6":-0.4,"IL1B":-0.4,"MMP9":-0.35,"ICAM1":-0.3,"CCL2":-0.35,"CD68":-0.2,"NFKB1":-0.4,"FOXP3":0.2}),
 d(name="Interferon beta-1a", mechanism_class="type_i_interferon", primary_moa="Type I interferon; a randomised add-on to IVIG showed no significant improvement",
   evidence_tier="phase_2", indication="failed", route="subcutaneous", cns_penetration=0.05, compartment="peripheral",
   therapeutic_axes=["cytokine_immune_modulation"], half_life_class="intermediate",
   safety_classes=["interferon_class"], target_uncertainty=0.4, pathways=[CYT, BNB],
   risk={"hepatic":0.3,"cardiac":0.1},
   target_effects={"IFNG":-0.2,"IL10":0.3,"MMP9":-0.3,"ICAM1":-0.2,"CXCL10":0.25}),
 d(name="Fingolimod", mechanism_class="s1p_receptor_modulator", primary_moa="S1P receptor functional antagonist; failed a phase 3 in CIDP, a related chronic neuropathy (not GBS)",
   evidence_tier="phase_3", indication="failed_in_related_disease", route="oral", cns_penetration=0.4, compartment="both",
   therapeutic_axes=["cytokine_immune_modulation"], half_life_class="long",
   safety_classes=["s1p_modulator_class"], target_uncertainty=0.45, pathways=[CYT, BNB],
   risk={"cardiac":0.5,"hepatic":0.3},
   target_effects={"S1PR1":-0.8,"IFNG":-0.2,"IL17A":-0.25,"VCAM1":-0.15}),
 # --- symptomatic: pain and conduction ------------------------------------------
 d(name="Gabapentin", mechanism_class="alpha2delta_ligand", primary_moa="Alpha-2-delta-1 ligand; a placebo-controlled crossover trial in GBS pain, and more effective than carbamazepine in an ICU trial",
   evidence_tier="approved", indication="pain", route="oral", cns_penetration=0.5, compartment="both",
   therapeutic_axes=["neuropathic_pain_relief"], half_life_class="short",
   safety_classes=["alpha2delta_sedation"], target_uncertainty=0.2, pathways=[PAIN],
   risk={"respiratory_depression":0.5,"renal_injury":0.2},
   target_effects={"CACNA2D1":-0.7}),
 d(name="Pregabalin", mechanism_class="alpha2delta_ligand", primary_moa="Higher-affinity alpha-2-delta-1 ligand; used for GBS pain by extrapolation from other neuropathic pain",
   evidence_tier="approved", indication="pain", route="oral", cns_penetration=0.55, compartment="both",
   therapeutic_axes=["neuropathic_pain_relief"], half_life_class="short",
   safety_classes=["alpha2delta_sedation"], target_uncertainty=0.25, pathways=[PAIN],
   risk={"respiratory_depression":0.5,"renal_injury":0.2},
   target_effects={"CACNA2D1":-0.8}),
 d(name="Carbamazepine", mechanism_class="sodium_channel_blocker", primary_moa="Sodium channel blockade for pain; less effective than gabapentin in an ICU trial",
   evidence_tier="approved", indication="pain", route="oral", cns_penetration=0.6, compartment="both",
   therapeutic_axes=["neuropathic_pain_relief"], half_life_class="intermediate",
   safety_classes=["sodium_channel_blocker"], target_uncertainty=0.3, pathways=[PAIN, NODE],
   risk={"cardiac":0.3,"hepatic":0.3,"respiratory_depression":0.2},
   target_effects={"SCN9A":-0.6,"SCN10A":-0.5,"SCN8A":-0.45}),
 d(name="Amitriptyline", mechanism_class="tricyclic_antidepressant", primary_moa="Tricyclic with sodium channel block and monoamine reuptake inhibition, used for neuropathic pain; no trial in GBS",
   evidence_tier="approved", indication="pain", route="oral", cns_penetration=0.7, compartment="both",
   therapeutic_axes=["neuropathic_pain_relief"], half_life_class="long",
   safety_classes=["tricyclic_class"], target_uncertainty=0.4, pathways=[PAIN],
   risk={"cardiac":0.5,"respiratory_depression":0.2,"hepatic":0.1},
   target_effects={"SCN9A":-0.35,"SCN10A":-0.25}),
 d(name="Dalfampridine", mechanism_class="kv1_potassium_channel_blocker", primary_moa="Broad-spectrum potassium channel blocker improving conduction in demyelinated axons; approved to improve walking in MS, with no trial in GBS",
   evidence_tier="approved", indication="conduction", route="oral", cns_penetration=0.5, compartment="both",
   therapeutic_axes=["conduction_restoration"], half_life_class="short",
   safety_classes=["potassium_channel_blocker"], target_uncertainty=0.45, pathways=[NODE],
   risk={"renal_injury":0.3,"cardiac":0.1},
   target_effects={"KCNA1":-0.7}),
]

CONTROLS = {
    "positive_redundancy": ["Gabapentin", "Pregabalin"],
    "negative_efficacy": ["Methylprednisolone", "Interferon beta-1a", "Fingolimod"],
    "safety_penalty": ["Eculizumab", "IVIG, second course (SID-GBS)"],
}


def main() -> None:
    with SIGNATURE.open(newline="") as handle:
        signature_genes = {row["gene"] for row in csv.DictReader(handle)}

    unknown = sorted({
        gene for drug in DRUGS for gene in drug["target_effects"]
        if gene not in signature_genes
    })
    if unknown:
        raise SystemExit(
            f"Panel references genes absent from the GBS signature: {unknown}\n"
            "Add them to data/gbs_expression.csv or correct the symbol."
        )
    for drug in DRUGS:
        stray = set(drug["safety_burden"]) - set(RISK_DOMAINS)
        if stray:
            raise SystemExit(f"{drug['name']} declares unknown risk domains: {sorted(stray)}")
        stray_axes = set(drug["therapeutic_axes"]) - set(AXES)
        if stray_axes:
            raise SystemExit(f"{drug['name']} declares unknown axes: {sorted(stray_axes)}")
        for gene, value in drug["target_effects"].items():
            if not -1.0 <= value <= 1.0:
                raise SystemExit(f"{drug['name']} effect on {gene} outside [-1,1]: {value}")
    names = [d["name"] for d in DRUGS]
    if len(names) != len(set(names)):
        raise SystemExit("Duplicate drug name in panel")
    for group, members in CONTROLS.items():
        missing = [m for m in members if m not in names]
        if missing:
            raise SystemExit(f"Control group {group} names absent agents: {missing}")

    targeted = {g for d in DRUGS for g in d["target_effects"]}
    payload = {
        "metadata": {
            "panel_version": "1.0.0",
            "generated_by": "tools/curate_gbs_panel.py",
            "disease": "guillain_barre",
            "purpose": "Mechanism-curated candidate panel for research prioritisation. Not a prescribing, efficacy, or co-administration dataset.",
            "curation_rule": "Agents with a randomised trial or an approved role in Guillain-Barre syndrome, plus a small number of extrapolated candidates flagged as such. The evidence base is small, so the panel is short (16 agents) and is not padded with agents never tested in the disease. Each control was checked against a source. The three negative-efficacy controls are methylprednisolone (no benefit in a 242-patient trial), interferon beta-1a (no significant improvement as an add-on) and fingolimod (failed a phase 3 in CIDP, a related disease, not GBS itself). The two safety controls are eculizumab (boxed meningococcal warning) and the second IVIG course (35% against 16% serious adverse events).",
            "controls": CONTROLS,
            "statistics": {
                "n_drugs": len(DRUGS),
                "n_signature_genes": len(signature_genes),
                "n_genes_targeted": len(targeted),
                "signature_gene_coverage": round(len(targeted) / len(signature_genes), 3),
                "mechanism_classes": len({d["mechanism_class"] for d in DRUGS}),
                "evidence_tiers": {
                    tier: sum(1 for d in DRUGS if d["evidence_tier"] == tier)
                    for tier in ("approved", "phase_3", "phase_2", "preclinical")
                },
            },
            "caveat": "Directional target effects are curated hypotheses, not measured pharmacology. Immunoglobulin, plasma exchange and the antibody agents act on proteins, not transcripts, so they are scored through downstream proxy genes and the result for them is the least reliable. Every record requires independent verification before publication use.",
        },
        "drugs": DRUGS,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    stats = payload["metadata"]["statistics"]
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(f"  {stats['n_drugs']} agents, {stats['mechanism_classes']} mechanism classes")
    print(f"  {stats['n_genes_targeted']}/{stats['n_signature_genes']} signature genes targeted "
          f"({stats['signature_gene_coverage']})")
    print(f"  evidence tiers: {stats['evidence_tiers']}")


if __name__ == "__main__":
    main()
