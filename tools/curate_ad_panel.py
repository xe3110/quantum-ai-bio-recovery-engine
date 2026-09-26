"""Curate and validate the Alzheimer's disease candidate panel.

The third disease in the registry. Multiple sclerosis is peripheral-plus-CNS
autoimmunity, Parkinson's is a dopaminergic and lysosomal neurodegeneration,
and Alzheimer's adds the case neither covers: the two proteins that define the
pathology (amyloid-beta and tau) are the two a small molecule reaches worst,
and the disease-modifying agents that have finally reached the clinic are
antibodies whose dose-limiting toxicity (amyloid-related imaging
abnormalities) has no analogue in either earlier vocabulary.

Nothing in Alzheimer's care is constrained by infection, malignancy, dyskinesia
or impulse-control disorders. It is constrained by ARIA, bradycardia and
syncope with cholinesterase inhibitors, and the cognitive cost of anything
anticholinergic in a population that is already losing cognition.

As with the MS and PD curation tools, this **fails the build** if any target
gene is absent from the disease signature, so a typo cannot enter the panel
silently.

Run: python -m tools.curate_ad_panel
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNATURE = ROOT / "data/ad_expression.csv"
OUT = ROOT / "data/drugs/alzheimers_panel_v1.json"

RISK_DOMAINS = (
    "aria", "bradycardia_syncope", "cognitive_worsening", "falls_sedation",
    "infusion_hypersensitivity", "cardiac", "hepatic", "gastrointestinal",
)
AXES = (
    "cholinergic_symptomatic", "amyloid_modification", "tau_modification",
    "synaptic_excitotoxicity_protection", "microglial_immune_modulation",
    "metabolic_vascular_rescue",
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


DRUGS = [
 # --- symptomatic cholinergic and muscarinic ------------------------------
 d(name="Donepezil", mechanism_class="cholinesterase_inhibitor", primary_moa="Reversible acetylcholinesterase inhibition, plus sigma-1 agonism",
   evidence_tier="approved", indication="all_stages", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["cholinergic_symptomatic"], half_life_class="long",
   safety_classes=["cholinergic_excess"], target_uncertainty=0.1, pathways=["cholinergic_signalling"],
   risk={"gastrointestinal":0.5,"bradycardia_syncope":0.5,"falls_sedation":0.2},
   target_effects={"ACHE":-0.85,"BCHE":-0.15,"CHRM1":0.45,"CHRNA7":0.3,"CHRNA4":0.25,"SIGMAR1":0.2}),
 d(name="Rivastigmine", mechanism_class="cholinesterase_inhibitor", primary_moa="Pseudo-irreversible inhibition of both acetylcholinesterase and butyrylcholinesterase",
   evidence_tier="approved", indication="all_stages", route="transdermal", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["cholinergic_symptomatic"], half_life_class="short",
   safety_classes=["cholinergic_excess"], target_uncertainty=0.15, pathways=["cholinergic_signalling"],
   risk={"gastrointestinal":0.7,"bradycardia_syncope":0.4,"falls_sedation":0.2},
   target_effects={"ACHE":-0.8,"BCHE":-0.8,"CHRM1":0.4,"CHRNA7":0.25,"CHRNA4":0.2}),
 d(name="Galantamine", mechanism_class="cholinesterase_nicotinic_modulator", primary_moa="Acetylcholinesterase inhibition with allosteric potentiation of nicotinic receptors",
   evidence_tier="approved", indication="mild_to_moderate", route="oral", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["cholinergic_symptomatic"], half_life_class="short",
   safety_classes=["cholinergic_excess"], target_uncertainty=0.2, pathways=["cholinergic_signalling"],
   risk={"gastrointestinal":0.5,"bradycardia_syncope":0.5,"cardiac":0.2},
   target_effects={"ACHE":-0.7,"CHRNA7":0.45,"CHRNA4":0.4,"CHRM1":0.3}),
 d(name="Tacrine", mechanism_class="cholinesterase_inhibitor_hepatotoxic", primary_moa="First-generation cholinesterase inhibitor, withdrawn for hepatotoxicity",
   evidence_tier="approved", indication="withdrawn", route="oral", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["cholinergic_symptomatic"], half_life_class="short",
   safety_classes=["cholinergic_excess","hepatotoxicity"], target_uncertainty=0.2, pathways=["cholinergic_signalling"],
   risk={"hepatic":0.95,"gastrointestinal":0.6,"bradycardia_syncope":0.3},
   target_effects={"ACHE":-0.85,"BCHE":-0.7,"CHRM1":0.4,"CHRNA7":0.2}),
 d(name="Xanomeline-trospium", mechanism_class="M1_M4_agonist", primary_moa="Central M1/M4 muscarinic agonism with a peripheral antagonist to limit cholinergic effects",
   evidence_tier="phase_3", indication="psychosis_in_AD", route="oral", cns_penetration=0.7, compartment="both",
   therapeutic_axes=["cholinergic_symptomatic","amyloid_modification"], half_life_class="intermediate",
   safety_classes=["muscarinic_agonism"], target_uncertainty=0.3,
   pathways=["cholinergic_signalling","amyloid_processing"],
   risk={"gastrointestinal":0.6,"cardiac":0.3,"falls_sedation":0.2},
   target_effects={"CHRM1":0.8,"ADAM10":0.25,"GSK3B":-0.2,"APP":-0.15}),
 d(name="Encenicline", mechanism_class="alpha7_nicotinic_agonist", primary_moa="Partial agonism of the alpha-7 nicotinic receptor; stopped in phase 3",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.65, compartment="cns",
   therapeutic_axes=["cholinergic_symptomatic","synaptic_excitotoxicity_protection"], half_life_class="intermediate",
   safety_classes=["nicotinic_agonism"], target_uncertainty=0.4,
   pathways=["cholinergic_signalling"],
   risk={"gastrointestinal":0.7,"cardiac":0.1},
   target_effects={"CHRNA7":0.75,"BDNF":0.2,"AKT1":0.2,"CASP3":-0.15}),
 d(name="Memantine", mechanism_class="NMDA_antagonist", primary_moa="Uncompetitive NMDA receptor antagonism limiting extrasynaptic excitotoxicity",
   evidence_tier="approved", indication="moderate_to_severe", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["synaptic_excitotoxicity_protection"], half_life_class="long",
   safety_classes=["NMDA_antagonism"], target_uncertainty=0.2,
   pathways=["glutamatergic_synaptic","neuronal_injury_apoptosis"],
   risk={"falls_sedation":0.3,"gastrointestinal":0.1},
   target_effects={"GRIN1":-0.5,"GRIN2B":-0.7,"CASP3":-0.2,"BDNF":0.15}),
 # --- anti-amyloid antibodies -------------------------------------------
 d(name="Lecanemab", mechanism_class="anti_protofibril_antibody", primary_moa="Monoclonal antibody selective for soluble amyloid-beta protofibrils",
   evidence_tier="approved", indication="early_AD", route="infusion", cns_penetration=0.15, compartment="both",
   therapeutic_axes=["amyloid_modification","microglial_immune_modulation"], half_life_class="long",
   safety_classes=["amyloid_related_imaging_abnormalities"], target_uncertainty=0.3,
   pathways=["amyloid_processing","microglial_neuroinflammation"],
   risk={"aria":0.8,"infusion_hypersensitivity":0.35},
   target_effects={"APP":-0.5,"NEFL":-0.25,"GFAP":-0.25,"C1QA":-0.2,"AIF1":-0.15,"MAPT":-0.1}),
 d(name="Donanemab", mechanism_class="anti_pyroglutamate_antibody", primary_moa="Monoclonal antibody against pyroglutamate-modified amyloid-beta in plaque",
   evidence_tier="approved", indication="early_AD", route="infusion", cns_penetration=0.15, compartment="both",
   therapeutic_axes=["amyloid_modification","microglial_immune_modulation"], half_life_class="long",
   safety_classes=["amyloid_related_imaging_abnormalities"], target_uncertainty=0.3,
   pathways=["amyloid_processing","microglial_neuroinflammation"],
   risk={"aria":0.9,"infusion_hypersensitivity":0.3},
   target_effects={"APP":-0.6,"NEFL":-0.3,"GFAP":-0.3,"C1QA":-0.2,"AIF1":-0.2,"MAPT":-0.15}),
 d(name="Aducanumab", mechanism_class="anti_aggregated_amyloid_antibody", primary_moa="Monoclonal antibody against aggregated amyloid-beta; withdrawn by its sponsor in 2024",
   evidence_tier="approved", indication="withdrawn", route="infusion", cns_penetration=0.12, compartment="both",
   therapeutic_axes=["amyloid_modification"], half_life_class="long",
   safety_classes=["amyloid_related_imaging_abnormalities"], target_uncertainty=0.4,
   pathways=["amyloid_processing"],
   risk={"aria":0.95,"infusion_hypersensitivity":0.2},
   target_effects={"APP":-0.45,"NEFL":-0.2,"GFAP":-0.2}),
 d(name="Gantenerumab", mechanism_class="anti_aggregated_amyloid_antibody", primary_moa="Monoclonal antibody against aggregated amyloid-beta; phase 3 did not meet its primary endpoint",
   evidence_tier="phase_3", indication="failed", route="subcutaneous", cns_penetration=0.12, compartment="both",
   therapeutic_axes=["amyloid_modification"], half_life_class="long",
   safety_classes=["amyloid_related_imaging_abnormalities"], target_uncertainty=0.4,
   pathways=["amyloid_processing"],
   risk={"aria":0.85,"infusion_hypersensitivity":0.2},
   target_effects={"APP":-0.5,"NEFL":-0.2,"GFAP":-0.2,"AIF1":-0.15}),
 d(name="Solanezumab", mechanism_class="anti_monomeric_amyloid_antibody", primary_moa="Monoclonal antibody against soluble monomeric amyloid-beta; failed phase 3 twice",
   evidence_tier="phase_3", indication="failed", route="infusion", cns_penetration=0.1, compartment="peripheral",
   therapeutic_axes=["amyloid_modification"], half_life_class="long",
   safety_classes=["infusion_reaction"], target_uncertainty=0.45,
   pathways=["amyloid_processing"],
   risk={"infusion_hypersensitivity":0.2,"aria":0.05},
   target_effects={"APP":-0.3,"NEFL":-0.1}),
 d(name="Valiltramiprosate (ALZ-801)", mechanism_class="amyloid_oligomer_aggregation_inhibitor", primary_moa="Oral prodrug of tramiprosate blocking amyloid-beta oligomer formation",
   evidence_tier="phase_3", indication="disease_modifying", route="oral", cns_penetration=0.5, compartment="cns",
   therapeutic_axes=["amyloid_modification"], half_life_class="intermediate",
   safety_classes=["aggregation_inhibitor_class"], target_uncertainty=0.5,
   pathways=["amyloid_processing","lipid_apoe_metabolism"],
   risk={"gastrointestinal":0.3,"falls_sedation":0.1},
   target_effects={"APP":-0.35,"APOE":-0.2,"NEFL":-0.1}),
 # --- secretase modulation and APP expression -----------------------------
 d(name="Verubecestat", mechanism_class="BACE1_inhibitor", primary_moa="BACE1 inhibition lowering amyloid-beta production; failed phase 3 with cognitive worsening",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["amyloid_modification"], half_life_class="long",
   safety_classes=["BACE_class_cognitive_worsening"], target_uncertainty=0.35,
   pathways=["amyloid_processing"],
   risk={"cognitive_worsening":0.6,"falls_sedation":0.4,"hepatic":0.2},
   target_effects={"BACE1":-0.9,"APP":-0.3,"ADAM10":0.15}),
 d(name="Semagacestat", mechanism_class="gamma_secretase_inhibitor", primary_moa="Gamma-secretase inhibition; phase 3 halted for worsened cognition and skin cancer",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["amyloid_modification"], half_life_class="short",
   safety_classes=["notch_inhibition","skin_malignancy"], target_uncertainty=0.35,
   pathways=["amyloid_processing"],
   risk={"cognitive_worsening":0.9,"gastrointestinal":0.3,"hepatic":0.1},
   target_effects={"PSEN1":-0.8,"NCSTN":-0.6,"APH1A":-0.5,"APP":-0.3}),
 d(name="Buntanetap", mechanism_class="APP_translation_inhibitor", primary_moa="Inhibits translation of APP and tau mRNA through 5' untranslated iron-responsive elements",
   evidence_tier="phase_3", indication="disease_modifying", route="oral", cns_penetration=0.65, compartment="cns",
   therapeutic_axes=["amyloid_modification","tau_modification"], half_life_class="short",
   safety_classes=["APP_translation_modulation"], target_uncertainty=0.5,
   pathways=["amyloid_processing","tau_pathology"],
   risk={"gastrointestinal":0.2},
   target_effects={"APP":-0.5,"MAPT":-0.3,"IL1B":-0.15,"TNF":-0.15}),
 # --- tau -----------------------------------------------------------------
 d(name="BIIB080 (MAPT antisense)", mechanism_class="MAPT_antisense_oligonucleotide", primary_moa="Intrathecal antisense oligonucleotide lowering tau expression",
   evidence_tier="phase_2", indication="disease_modifying", route="intrathecal", cns_penetration=1.0, compartment="cns",
   therapeutic_axes=["tau_modification"], half_life_class="long",
   safety_classes=["intrathecal_procedure"], target_uncertainty=0.4,
   pathways=["tau_pathology"],
   risk={"infusion_hypersensitivity":0.3,"falls_sedation":0.1},
   target_effects={"MAPT":-0.9,"NEFL":-0.25,"GFAP":-0.1}),
 d(name="Bepranemab", mechanism_class="anti_tau_antibody", primary_moa="Monoclonal antibody against the mid-region of extracellular tau",
   evidence_tier="phase_2", indication="disease_modifying", route="infusion", cns_penetration=0.1, compartment="both",
   therapeutic_axes=["tau_modification"], half_life_class="long",
   safety_classes=["infusion_reaction"], target_uncertainty=0.5,
   pathways=["tau_pathology"],
   risk={"infusion_hypersensitivity":0.3},
   target_effects={"MAPT":-0.45,"NEFL":-0.15}),
 d(name="Hydromethylthionine (LMTM)", mechanism_class="tau_aggregation_inhibitor", primary_moa="Methylene-blue-derived tau aggregation inhibitor; phase 3 missed its primary endpoint",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["tau_modification"], half_life_class="intermediate",
   safety_classes=["methylene_blue_class"], target_uncertainty=0.5,
   pathways=["tau_pathology","endolysosomal_autophagy"],
   risk={"gastrointestinal":0.4,"falls_sedation":0.1},
   target_effects={"MAPT":-0.5,"MAP1LC3B":0.25,"SQSTM1":-0.2}),
 d(name="Tideglusib", mechanism_class="GSK3_inhibitor", primary_moa="Irreversible GSK-3 inhibition limiting tau phosphorylation; failed phase 2",
   evidence_tier="phase_2", indication="failed", route="oral", cns_penetration=0.5, compartment="both",
   therapeutic_axes=["tau_modification"], half_life_class="short",
   safety_classes=["kinase_inhibition"], target_uncertainty=0.45,
   pathways=["tau_pathology","microglial_neuroinflammation"],
   risk={"hepatic":0.4,"gastrointestinal":0.2},
   target_effects={"GSK3B":-0.85,"MAPT":-0.4,"NFKB1":-0.2,"BDNF":0.15}),
 d(name="Saracatinib", mechanism_class="FYN_inhibitor", primary_moa="Src-family kinase inhibition, uncoupling amyloid-beta signalling from NMDA receptors and tau",
   evidence_tier="phase_2", indication="failed", route="oral", cns_penetration=0.5, compartment="both",
   therapeutic_axes=["tau_modification","synaptic_excitotoxicity_protection"], half_life_class="intermediate",
   safety_classes=["kinase_inhibition"], target_uncertainty=0.45,
   pathways=["tau_pathology","glutamatergic_synaptic"],
   risk={"gastrointestinal":0.4,"hepatic":0.3},
   target_effects={"FYN":-0.8,"MAPT":-0.2,"GRIN2B":-0.25}),
 d(name="Blarcamesine (ANAVEX2-73)", mechanism_class="sigma1_agonist", primary_moa="Sigma-1 receptor agonism restoring autophagy and mitochondrial and ER homeostasis",
   evidence_tier="phase_3", indication="disease_modifying", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["tau_modification","metabolic_vascular_rescue"], half_life_class="intermediate",
   safety_classes=["sigma1_agonism"], target_uncertainty=0.5,
   pathways=["neurotrophic_support","endolysosomal_autophagy"],
   risk={"falls_sedation":0.4,"gastrointestinal":0.1},
   target_effects={"SIGMAR1":0.8,"MTOR":-0.2,"MAP1LC3B":0.3,"BECN1":0.25,"BDNF":0.25,"CASP3":-0.2}),
 # --- microglia and innate immunity ---------------------------------------
 d(name="Masitinib", mechanism_class="CSF1R_KIT_inhibitor", primary_moa="Tyrosine kinase inhibition damping microglial and mast-cell activation",
   evidence_tier="phase_3", indication="disease_modifying", route="oral", cns_penetration=0.3, compartment="both",
   therapeutic_axes=["microglial_immune_modulation"], half_life_class="short",
   safety_classes=["kinase_inhibition","neutropenia"], target_uncertainty=0.5,
   pathways=["microglial_neuroinflammation"],
   risk={"hepatic":0.4,"gastrointestinal":0.4},
   target_effects={"CSF1R":-0.6,"FYN":-0.3,"AIF1":-0.3,"CD68":-0.25,"IL6":-0.2,"TNF":-0.2,"GFAP":-0.15}),
 d(name="Neflamapimod", mechanism_class="p38alpha_inhibitor", primary_moa="Brain-penetrant p38 alpha inhibition, aimed at endosomal dysfunction in cholinergic neurons",
   evidence_tier="phase_2", indication="disease_modifying", route="oral", cns_penetration=0.65, compartment="cns",
   therapeutic_axes=["microglial_immune_modulation","cholinergic_symptomatic"], half_life_class="short",
   safety_classes=["kinase_inhibition","p38_hepatotoxicity"], target_uncertainty=0.5,
   pathways=["microglial_neuroinflammation","endolysosomal_autophagy"],
   risk={"hepatic":0.3,"gastrointestinal":0.1},
   target_effects={"MAPK14":-0.85,"IL1B":-0.3,"TNF":-0.3,"RAB5A":-0.4,"CHAT":0.25,"NFKB1":-0.15}),
 d(name="AL002", mechanism_class="TREM2_agonist_antibody", primary_moa="Agonist antibody supporting protective microglial responses; missed its phase 2 endpoint",
   evidence_tier="phase_2", indication="failed", route="infusion", cns_penetration=0.1, compartment="both",
   therapeutic_axes=["microglial_immune_modulation"], half_life_class="long",
   safety_classes=["infusion_reaction"], target_uncertainty=0.55,
   pathways=["microglial_neuroinflammation"],
   risk={"infusion_hypersensitivity":0.3,"aria":0.4},
   target_effects={"TREM2":0.7,"TYROBP":0.4,"C1QA":-0.15,"IL1B":-0.15}),
 d(name="NLRP3 inhibitor (class exemplar)", mechanism_class="NLRP3_inhibitor", primary_moa="Inflammasome blockade upstream of IL-1beta; evidence extrapolated from other indications",
   evidence_tier="phase_2", indication="disease_modifying", route="oral", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["microglial_immune_modulation"], half_life_class="intermediate",
   safety_classes=["innate_immune_suppression"], target_uncertainty=0.5,
   pathways=["microglial_neuroinflammation"],
   risk={"gastrointestinal":0.2,"hepatic":0.2},
   target_effects={"NLRP3":-0.85,"CASP1":-0.7,"IL1B":-0.7,"IL6":-0.35,"AIF1":-0.3,"GFAP":-0.2,"TNF":-0.2}),
 d(name="Naproxen", mechanism_class="NSAID_COX_inhibitor", primary_moa="Cyclooxygenase inhibition; failed the ADAPT prevention trial",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.3, compartment="peripheral",
   therapeutic_axes=["microglial_immune_modulation"], half_life_class="intermediate",
   safety_classes=["NSAID_class"], target_uncertainty=0.4,
   pathways=["microglial_neuroinflammation"],
   risk={"gastrointestinal":0.6,"cardiac":0.4},
   target_effects={"PTGS2":-0.6,"IL1B":-0.25,"TNF":-0.2,"IL6":-0.2,"NFKB1":-0.15,"GFAP":-0.1}),
 # --- metabolic, vascular, and proteostatic ----------------------------------
 d(name="Semaglutide", mechanism_class="GLP1_agonist", primary_moa="GLP-1 receptor agonism with anti-inflammatory and insulin-sensitising effects; did not slow progression in phase 3",
   evidence_tier="phase_3", indication="failed", route="subcutaneous", cns_penetration=0.15, compartment="both",
   therapeutic_axes=["metabolic_vascular_rescue","microglial_immune_modulation"], half_life_class="long",
   safety_classes=["incretin_effects"], target_uncertainty=0.45,
   pathways=["insulin_metabolic","microglial_neuroinflammation","mitochondrial_bioenergetics"],
   risk={"gastrointestinal":0.6,"falls_sedation":0.2},
   target_effects={"GLP1R":0.8,"INSR":0.3,"IRS1":0.3,"AKT1":0.3,"GSK3B":-0.25,"TNF":-0.25,"IL1B":-0.25,"BDNF":0.25,"NLRP3":-0.2,"PPARGC1A":0.25,"CASP3":-0.2}),
 d(name="Pioglitazone", mechanism_class="PPARG_agonist", primary_moa="PPAR-gamma agonism improving insulin sensitivity; failed phase 3 in mild cognitive impairment",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.35, compartment="both",
   therapeutic_axes=["metabolic_vascular_rescue","microglial_immune_modulation"], half_life_class="intermediate",
   safety_classes=["fluid_retention"], target_uncertainty=0.45,
   pathways=["insulin_metabolic","mitochondrial_bioenergetics"],
   risk={"cardiac":0.5,"falls_sedation":0.3},
   target_effects={"PPARG":0.75,"PPARGC1A":0.4,"TNF":-0.25,"IL1B":-0.25,"NFKB1":-0.25,"INSR":0.2,"AIF1":-0.2,"BACE1":-0.15}),
 d(name="Intranasal insulin", mechanism_class="insulin_receptor_agonist", primary_moa="Nose-to-brain insulin delivery correcting central insulin resistance",
   evidence_tier="phase_2", indication="disease_modifying", route="intranasal", cns_penetration=0.8, compartment="cns",
   therapeutic_axes=["metabolic_vascular_rescue"], half_life_class="short",
   safety_classes=["hypoglycaemia"], target_uncertainty=0.5,
   pathways=["insulin_metabolic"],
   risk={"falls_sedation":0.1},
   target_effects={"INSR":0.6,"IRS1":0.5,"AKT1":0.4,"GSK3B":-0.3,"SLC2A1":0.15,"BDNF":0.15}),
 d(name="Metformin", mechanism_class="biguanide_AMPK_activator", primary_moa="Indirect AMPK activation improving metabolic signalling",
   evidence_tier="phase_2", indication="disease_modifying", route="oral", cns_penetration=0.3, compartment="peripheral",
   therapeutic_axes=["metabolic_vascular_rescue"], half_life_class="short",
   safety_classes=["biguanide_class"], target_uncertainty=0.5,
   pathways=["mitochondrial_bioenergetics","insulin_metabolic"],
   risk={"gastrointestinal":0.3},
   target_effects={"PRKAA1":0.6,"PPARGC1A":0.3,"MTOR":-0.3,"IRS1":0.2,"SIRT1":0.2}),
 d(name="Atorvastatin", mechanism_class="HMGCR_inhibitor", primary_moa="HMG-CoA reductase inhibition; failed the LEADe trial",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.25, compartment="peripheral",
   therapeutic_axes=["metabolic_vascular_rescue"], half_life_class="intermediate",
   safety_classes=["statin_class"], target_uncertainty=0.45,
   pathways=["lipid_apoe_metabolism"],
   risk={"hepatic":0.2,"falls_sedation":0.05},
   target_effects={"HMGCR":-0.85,"LDLR":0.35,"NOS2":-0.15}),
 d(name="Nilvadipine", mechanism_class="CaV1_blocker", primary_moa="L-type calcium channel blockade with reported amyloid-clearance effects; failed phase 3",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.5, compartment="both",
   therapeutic_axes=["metabolic_vascular_rescue"], half_life_class="short",
   safety_classes=["vasodilation"], target_uncertainty=0.45,
   pathways=["calcium_homeostasis"],
   risk={"falls_sedation":0.5,"cardiac":0.3},
   target_effects={"CACNA1C":-0.7,"RYR2":-0.15,"TNF":-0.1}),
 d(name="Resveratrol", mechanism_class="sirtuin_activator", primary_moa="Putative SIRT1 and AMPK activation; no cognitive benefit in phase 2",
   evidence_tier="phase_2", indication="failed", route="oral", cns_penetration=0.3, compartment="peripheral",
   therapeutic_axes=["metabolic_vascular_rescue"], half_life_class="short",
   safety_classes=["nutraceutical"], target_uncertainty=0.55,
   pathways=["mitochondrial_bioenergetics","oxidative_stress"],
   risk={"gastrointestinal":0.2},
   target_effects={"SIRT1":0.5,"PPARGC1A":0.3,"NFE2L2":0.2,"PRKAA1":0.2,"SOD2":0.15,"TNF":-0.15}),
 d(name="Vitamin E (alpha-tocopherol)", mechanism_class="lipophilic_antioxidant", primary_moa="Chain-breaking lipid antioxidant; slowed functional decline in mild-to-moderate AD",
   evidence_tier="phase_3", indication="adjunct", route="oral", cns_penetration=0.3, compartment="both",
   therapeutic_axes=["metabolic_vascular_rescue"], half_life_class="long",
   safety_classes=["nutraceutical_high_dose"], target_uncertainty=0.5,
   pathways=["oxidative_stress"],
   risk={"cardiac":0.2},
   target_effects={"GPX4":0.25,"SOD1":0.15,"CAT":0.15,"NOS2":-0.15}),
 d(name="Rapamycin (sirolimus)", mechanism_class="mTOR_inhibitor", primary_moa="mTORC1 inhibition inducing autophagy and TFEB-driven lysosomal biogenesis",
   evidence_tier="phase_2", indication="disease_modifying", route="oral", cns_penetration=0.4, compartment="both",
   therapeutic_axes=["tau_modification","metabolic_vascular_rescue"], half_life_class="long",
   safety_classes=["mTOR_immunosuppression"], target_uncertainty=0.5,
   pathways=["endolysosomal_autophagy"],
   risk={"gastrointestinal":0.3,"hepatic":0.2,"cardiac":0.2},
   target_effects={"MTOR":-0.75,"TFEB":0.35,"BECN1":0.3,"MAP1LC3B":0.35,"SQSTM1":-0.3}),
]

CONTROLS = {
    "positive_redundancy": ["Donepezil", "Rivastigmine"],
    "negative_efficacy": ["Solanezumab", "Verubecestat", "Naproxen", "Atorvastatin", "Pioglitazone"],
    "safety_penalty": ["Tacrine", "Semagacestat", "Aducanumab"],
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
            f"Panel references genes absent from the AD signature: {unknown}\n"
            "Add them to data/ad_expression.csv or correct the symbol."
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
            "generated_by": "tools/curate_ad_panel.py",
            "disease": "alzheimers",
            "purpose": "Mechanism-curated candidate panel for research prioritisation. Not a prescribing, efficacy, or co-administration dataset.",
            "curation_rule": "Approved symptomatic and anti-amyloid therapies plus disease-modifying candidates, weighted deliberately toward agents that failed in phase 2/3. Alzheimer's has the longest record of failed disease-modification trials of any neurodegenerative disease, which makes it the strongest source of negative controls declared so far.",
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
            "caveat": "Directional target effects are curated hypotheses, not measured pharmacology. Amyloid-beta is a cleavage product with no transcript, so the anti-amyloid antibodies are scored on APP and downstream injury and glial markers as a proxy for amyloid burden. Every record requires independent verification before publication use.",
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
