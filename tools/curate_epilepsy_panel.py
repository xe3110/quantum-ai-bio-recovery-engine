"""Curate and validate the epilepsy candidate panel.

The fourth disease in the registry, and the one that inverts the Alzheimer's
problem. In Alzheimer's the disease-defining proteins are the ones a small
molecule reaches worst. In epilepsy they are ion channels and receptors, the
most tractable class there is, and most approved drugs already act on them. The
panel is therefore dominated by approved agents (30 of 37), and the questions
change: which combinations of existing mechanisms add anything, given that
rational polytherapy is already standard practice, and what lies beyond the
crowded channel targets.

Epilepsy is also the first registered disease whose safety vocabulary centres on
teratogenicity, severe cutaneous hypersensitivity, retinal toxicity and
seizure aggravation, the last being an unusual case where a drug of the right
mechanism makes the disease worse in a particular syndrome.

As with the earlier curation tools, this **fails the build** if any target gene
is absent from the disease signature, so a typo cannot enter the panel silently.

Run: python -m tools.curate_epilepsy_panel
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIGNATURE = ROOT / "data/ep_expression.csv"
OUT = ROOT / "data/drugs/epilepsy_panel_v1.json"

RISK_DOMAINS = (
    "sedation_cognitive", "dermatologic_hypersensitivity", "teratogenicity",
    "hepatic", "hematologic", "behavioural_mood", "cardiac",
    "seizure_aggravation", "retinal_toxicity",
)
AXES = (
    "sodium_channel_stabilisation", "gabaergic_potentiation", "glutamate_attenuation",
    "vesicle_release_modulation", "calcium_channel_modulation",
    "potassium_channel_opening", "epileptogenesis_modification", "neuromodulatory_adjunct",
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


NA = "voltage_gated_sodium"
GABA = "gabaergic_inhibition"
GLU = "glutamatergic_excitation"
CA = "calcium_channels"
K = "potassium_channels"
VES = "synaptic_vesicle"
MTOR = "mtor_signalling"
INF = "neuroinflammation"
NEUMOD = "neuromodulatory_signalling"

DRUGS = [
 # --- sodium channel blockers ------------------------------------------------
 d(name="Carbamazepine", mechanism_class="sodium_channel_blocker_dibenzazepine", primary_moa="Use-dependent sodium channel block favouring the inactivated state",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation"], half_life_class="intermediate",
   safety_classes=["sodium_channel_blocker", "hla_cutaneous_hypersensitivity"], target_uncertainty=0.1, pathways=[NA],
   risk={"dermatologic_hypersensitivity":0.85,"hematologic":0.6,"sedation_cognitive":0.4,"teratogenicity":0.5,"hepatic":0.3,"cardiac":0.3,"seizure_aggravation":0.4},
   target_effects={"SCN2A":-0.7,"SCN8A":-0.7,"SCN3A":-0.6}),
 d(name="Oxcarbazepine", mechanism_class="sodium_channel_blocker_dibenzazepine", primary_moa="Prodrug of a 10-hydroxy metabolite blocking sodium channels; fewer interactions than carbamazepine",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation"], half_life_class="short",
   safety_classes=["sodium_channel_blocker", "hla_cutaneous_hypersensitivity"], target_uncertainty=0.15, pathways=[NA],
   risk={"dermatologic_hypersensitivity":0.6,"sedation_cognitive":0.4,"teratogenicity":0.4,"seizure_aggravation":0.4,"hepatic":0.1},
   target_effects={"SCN2A":-0.65,"SCN8A":-0.65,"SCN3A":-0.55}),
 d(name="Eslicarbazepine acetate", mechanism_class="sodium_channel_blocker_dibenzazepine", primary_moa="Once-daily prodrug of the S-enantiomer of the oxcarbazepine metabolite",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation"], half_life_class="intermediate",
   safety_classes=["sodium_channel_blocker"], target_uncertainty=0.2, pathways=[NA, CA],
   risk={"dermatologic_hypersensitivity":0.4,"sedation_cognitive":0.4,"cardiac":0.3,"seizure_aggravation":0.3},
   target_effects={"SCN2A":-0.6,"SCN8A":-0.6,"SCN3A":-0.5,"CACNA1H":-0.2}),
 d(name="Phenytoin", mechanism_class="sodium_channel_blocker_hydantoin", primary_moa="Use-dependent sodium channel block with a narrow, saturable therapeutic window",
   evidence_tier="approved", indication="focal_and_status", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation"], half_life_class="intermediate",
   safety_classes=["sodium_channel_blocker", "hydantoin_chronic_toxicity"], target_uncertainty=0.1, pathways=[NA],
   risk={"dermatologic_hypersensitivity":0.7,"sedation_cognitive":0.5,"teratogenicity":0.6,"hepatic":0.3,"cardiac":0.4,"hematologic":0.3,"seizure_aggravation":0.3},
   target_effects={"SCN2A":-0.7,"SCN8A":-0.65,"SCN3A":-0.55}),
 d(name="Lamotrigine", mechanism_class="sodium_channel_blocker_phenyltriazine", primary_moa="Sodium channel block with some inhibition of high-voltage calcium channels",
   evidence_tier="approved", indication="broad_spectrum", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation", "calcium_channel_modulation"], half_life_class="intermediate",
   safety_classes=["sodium_channel_blocker", "titration_cutaneous_hypersensitivity"], target_uncertainty=0.15, pathways=[NA, CA],
   risk={"dermatologic_hypersensitivity":0.9,"sedation_cognitive":0.2,"teratogenicity":0.2,"seizure_aggravation":0.3,"cardiac":0.2},
   target_effects={"SCN2A":-0.6,"SCN8A":-0.55,"SCN3A":-0.5,"CACNA1A":-0.3}),
 d(name="Lacosamide", mechanism_class="sodium_channel_slow_inactivation_enhancer", primary_moa="Enhances slow inactivation of sodium channels",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation"], half_life_class="intermediate",
   safety_classes=["sodium_channel_blocker", "pr_interval_prolongation"], target_uncertainty=0.2, pathways=[NA],
   risk={"cardiac":0.5,"sedation_cognitive":0.3,"dermatologic_hypersensitivity":0.1},
   target_effects={"SCN2A":-0.55,"SCN8A":-0.6,"SCN3A":-0.5}),
 d(name="Cenobamate", mechanism_class="dual_sodium_blocker_gabaa_modulator", primary_moa="Inhibits persistent sodium current and positively modulates GABA-A receptors",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation", "gabaergic_potentiation"], half_life_class="long",
   safety_classes=["sodium_channel_blocker", "gabaa_positive_modulation", "dress_hypersensitivity"], target_uncertainty=0.3, pathways=[NA, GABA],
   risk={"dermatologic_hypersensitivity":0.6,"cardiac":0.4,"sedation_cognitive":0.5,"hepatic":0.2},
   target_effects={"SCN2A":-0.5,"SCN8A":-0.55,"GABRA1":0.3,"GABRG2":0.25,"GABRB3":0.25}),
 d(name="Rufinamide", mechanism_class="sodium_channel_blocker_triazole", primary_moa="Prolongs the inactive state of sodium channels; used in Lennox-Gastaut syndrome",
   evidence_tier="approved", indication="lennox_gastaut", route="oral", cns_penetration=0.65, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation"], half_life_class="intermediate",
   safety_classes=["sodium_channel_blocker", "qt_shortening"], target_uncertainty=0.25, pathways=[NA],
   risk={"sedation_cognitive":0.3,"cardiac":0.3},
   target_effects={"SCN2A":-0.5,"SCN8A":-0.5}),
 # --- multi-target broad-spectrum -----------------------------------------
 d(name="Valproate", mechanism_class="broad_spectrum_valproate", primary_moa="Sodium and T-type calcium block, GABA-transaminase inhibition, and weak histone deacetylase inhibition",
   evidence_tier="approved", indication="broad_spectrum", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation", "gabaergic_potentiation", "calcium_channel_modulation"], half_life_class="intermediate",
   safety_classes=["valproate_class"], target_uncertainty=0.25, pathways=[NA, GABA, CA],
   risk={"teratogenicity":1.0,"hepatic":0.8,"sedation_cognitive":0.3,"hematologic":0.4,"behavioural_mood":0.2},
   target_effects={"SCN2A":-0.35,"CACNA1H":-0.3,"ABAT":-0.4,"GAD1":0.2,"HDAC1":-0.4}),
 d(name="Topiramate", mechanism_class="sulfamate_multitarget", primary_moa="Sodium block, GABA-A potentiation, AMPA/kainate antagonism and carbonic anhydrase inhibition",
   evidence_tier="approved", indication="broad_spectrum", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation", "gabaergic_potentiation", "glutamate_attenuation"], half_life_class="intermediate",
   safety_classes=["carbonic_anhydrase_inhibition", "cognitive_slowing"], target_uncertainty=0.3, pathways=[NA, GABA, GLU],
   risk={"sedation_cognitive":0.8,"teratogenicity":0.6,"behavioural_mood":0.4},
   target_effects={"SCN2A":-0.3,"GABRA1":0.25,"GRIA1":-0.4,"GRIK2":-0.4,"CA2":-0.4}),
 d(name="Zonisamide", mechanism_class="sulfonamide_multitarget", primary_moa="Sodium and T-type calcium channel block with weak carbonic anhydrase inhibition",
   evidence_tier="approved", indication="broad_spectrum", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["sodium_channel_stabilisation", "calcium_channel_modulation"], half_life_class="long",
   safety_classes=["carbonic_anhydrase_inhibition", "sulfonamide_hypersensitivity"], target_uncertainty=0.25, pathways=[NA, CA],
   risk={"sedation_cognitive":0.4,"dermatologic_hypersensitivity":0.4,"behavioural_mood":0.3},
   target_effects={"SCN2A":-0.4,"CACNA1G":-0.5,"CACNA1H":-0.45,"CA2":-0.4}),
 # --- GABAergic ------------------------------------------------------------
 d(name="Phenobarbital", mechanism_class="barbiturate_gabaa_modulator", primary_moa="Prolongs GABA-A channel opening",
   evidence_tier="approved", indication="broad_spectrum", route="oral", cns_penetration=0.8, compartment="cns",
   therapeutic_axes=["gabaergic_potentiation"], half_life_class="long",
   safety_classes=["gabaa_positive_modulation", "sedative_dependence"], target_uncertainty=0.1, pathways=[GABA, GLU],
   risk={"sedation_cognitive":0.9,"behavioural_mood":0.5,"teratogenicity":0.5,"hepatic":0.2},
   target_effects={"GABRA1":0.55,"GABRG2":0.4,"GABRB3":0.4,"GRIA1":-0.15}),
 d(name="Clobazam", mechanism_class="benzodiazepine_gabaa_modulator", primary_moa="Benzodiazepine-site GABA-A positive modulation",
   evidence_tier="approved", indication="lennox_gastaut", route="oral", cns_penetration=0.8, compartment="cns",
   therapeutic_axes=["gabaergic_potentiation"], half_life_class="long",
   safety_classes=["gabaa_positive_modulation", "sedative_dependence"], target_uncertainty=0.1, pathways=[GABA],
   risk={"sedation_cognitive":0.6,"behavioural_mood":0.3},
   target_effects={"GABRA1":0.5,"GABRG2":0.55,"GABRA2":0.4,"GABRA5":0.2}),
 d(name="Midazolam (nasal rescue)", mechanism_class="benzodiazepine_gabaa_modulator", primary_moa="Fast-acting benzodiazepine for seizure clusters",
   evidence_tier="approved", indication="rescue", route="intranasal", cns_penetration=0.85, compartment="cns",
   therapeutic_axes=["gabaergic_potentiation"], half_life_class="short",
   safety_classes=["gabaa_positive_modulation", "sedative_dependence"], target_uncertainty=0.1, pathways=[GABA],
   risk={"sedation_cognitive":0.7,"behavioural_mood":0.2},
   target_effects={"GABRA1":0.55,"GABRG2":0.55,"GABRA2":0.4,"GABRA5":0.25}),
 d(name="Vigabatrin", mechanism_class="GABA_transaminase_inhibitor", primary_moa="Irreversible GABA-transaminase inhibition, raising GABA",
   evidence_tier="approved", indication="infantile_spasms_and_refractory_focal", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["gabaergic_potentiation"], half_life_class="short",
   safety_classes=["gaba_reuptake_or_catabolism_inhibition", "visual_field_loss"], target_uncertainty=0.15, pathways=[GABA],
   risk={"retinal_toxicity":0.95,"seizure_aggravation":0.4,"sedation_cognitive":0.3,"behavioural_mood":0.4},
   target_effects={"ABAT":-0.9}),
 d(name="Tiagabine", mechanism_class="GAT1_inhibitor", primary_moa="GABA transporter GAT-1 inhibition",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["gabaergic_potentiation"], half_life_class="short",
   safety_classes=["gaba_reuptake_or_catabolism_inhibition"], target_uncertainty=0.2, pathways=[GABA],
   risk={"sedation_cognitive":0.5,"seizure_aggravation":0.4},
   target_effects={"SLC6A1":-0.8}),
 d(name="Ganaxolone", mechanism_class="neurosteroid_gabaa_modulator", primary_moa="Neurosteroid positive modulation of synaptic and extrasynaptic GABA-A receptors",
   evidence_tier="approved", indication="cdkl5_deficiency", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["gabaergic_potentiation"], half_life_class="short",
   safety_classes=["gabaa_positive_modulation"], target_uncertainty=0.35, pathways=[GABA],
   risk={"sedation_cognitive":0.6},
   target_effects={"GABRD":0.6,"GABRA1":0.35,"GABRG2":0.3}),
 d(name="Stiripentol", mechanism_class="aromatic_alcohol_gabaa_modulator", primary_moa="Positive GABA-A modulation with lactate dehydrogenase and CYP inhibition; used in Dravet syndrome",
   evidence_tier="approved", indication="dravet", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["gabaergic_potentiation"], half_life_class="intermediate",
   safety_classes=["gabaa_positive_modulation", "cyp_inhibition"], target_uncertainty=0.3, pathways=[GABA],
   risk={"sedation_cognitive":0.5,"behavioural_mood":0.1},
   target_effects={"GABRA1":0.4,"GABRB3":0.4,"GABRD":0.3}),
 d(name="Fenfluramine", mechanism_class="serotonin_releasing_agent", primary_moa="Serotonin release with 5-HT2C agonism and sigma-1 activity; used in Dravet syndrome",
   evidence_tier="approved", indication="dravet", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["neuromodulatory_adjunct"], half_life_class="intermediate",
   safety_classes=["serotonergic_valvulopathy"], target_uncertainty=0.35, pathways=[NEUMOD],
   risk={"cardiac":0.8,"sedation_cognitive":0.3},
   target_effects={"HTR2C":0.6,"SIGMAR1":0.4}),
 # --- glutamatergic --------------------------------------------------------
 d(name="Perampanel", mechanism_class="ampa_antagonist", primary_moa="Noncompetitive AMPA receptor antagonism",
   evidence_tier="approved", indication="focal_and_generalised", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["glutamate_attenuation"], half_life_class="long",
   safety_classes=["ampa_antagonism", "boxed_psychiatric_warning"], target_uncertainty=0.15, pathways=[GLU],
   risk={"behavioural_mood":0.9,"sedation_cognitive":0.5},
   target_effects={"GRIA1":-0.7,"GRIK2":-0.2}),
 d(name="Talampanel", mechanism_class="ampa_antagonist_early", primary_moa="AMPA receptor antagonist; a controlled trial in refractory partial epilepsy did not demonstrate efficacy",
   evidence_tier="phase_2", indication="failed", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["glutamate_attenuation"], half_life_class="short",
   safety_classes=["ampa_antagonism"], target_uncertainty=0.4, pathways=[GLU],
   risk={"sedation_cognitive":0.5},
   target_effects={"GRIA1":-0.6,"GRIK2":-0.2}),
 d(name="Ketamine", mechanism_class="nmda_antagonist_dissociative", primary_moa="NMDA channel block, used off-label in refractory status epilepticus",
   evidence_tier="phase_2", indication="refractory_status", route="infusion", cns_penetration=0.85, compartment="cns",
   therapeutic_axes=["glutamate_attenuation"], half_life_class="short",
   safety_classes=["dissociative_anaesthetic"], target_uncertainty=0.4, pathways=[GLU],
   risk={"behavioural_mood":0.5,"cardiac":0.3,"sedation_cognitive":0.4},
   target_effects={"GRIN1":-0.6,"GRIN2B":-0.7,"GRIN2A":-0.4}),
 d(name="Felbamate", mechanism_class="nmda_glycine_site_antagonist", primary_moa="NMDA glycine-site antagonism with GABA-A potentiation and sodium block; restricted for aplastic anaemia and hepatic failure",
   evidence_tier="approved", indication="restricted_refractory", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["glutamate_attenuation", "sodium_channel_stabilisation"], half_life_class="intermediate",
   safety_classes=["aplastic_anaemia_and_hepatic_failure"], target_uncertainty=0.3, pathways=[GLU, NA],
   risk={"hematologic":0.95,"hepatic":0.9,"sedation_cognitive":0.3},
   target_effects={"GRIN2B":-0.5,"GRIN1":-0.4,"SCN2A":-0.3,"GABRA1":0.2}),
 # --- vesicle, calcium, potassium ---------------------------------------------
 d(name="Levetiracetam", mechanism_class="SV2A_ligand", primary_moa="Binds synaptic vesicle protein 2A, modulating neurotransmitter release",
   evidence_tier="approved", indication="broad_spectrum", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["vesicle_release_modulation"], half_life_class="short",
   safety_classes=["SV2A_behavioural_adverse"], target_uncertainty=0.3, pathways=[VES, CA],
   risk={"behavioural_mood":0.7,"sedation_cognitive":0.4},
   target_effects={"SV2A":0.6,"CACNA1A":-0.15}),
 d(name="Brivaracetam", mechanism_class="SV2A_ligand", primary_moa="High-affinity SV2A ligand",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.75, compartment="cns",
   therapeutic_axes=["vesicle_release_modulation"], half_life_class="short",
   safety_classes=["SV2A_behavioural_adverse"], target_uncertainty=0.3, pathways=[VES, NA],
   risk={"behavioural_mood":0.5,"sedation_cognitive":0.35},
   target_effects={"SV2A":0.75,"SCN2A":-0.15}),
 d(name="Gabapentin", mechanism_class="alpha2delta_ligand", primary_moa="Binds the alpha-2-delta-1 subunit of voltage-gated calcium channels",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["calcium_channel_modulation"], half_life_class="short",
   safety_classes=["alpha2delta_sedation"], target_uncertainty=0.2, pathways=[CA],
   risk={"sedation_cognitive":0.5},
   target_effects={"CACNA2D1":-0.7,"CACNA1A":-0.15}),
 d(name="Pregabalin", mechanism_class="alpha2delta_ligand", primary_moa="Higher-affinity alpha-2-delta-1 ligand",
   evidence_tier="approved", indication="focal", route="oral", cns_penetration=0.65, compartment="cns",
   therapeutic_axes=["calcium_channel_modulation"], half_life_class="short",
   safety_classes=["alpha2delta_sedation"], target_uncertainty=0.2, pathways=[CA],
   risk={"sedation_cognitive":0.5,"behavioural_mood":0.3},
   target_effects={"CACNA2D1":-0.8,"CACNA1A":-0.2}),
 d(name="Ethosuximide", mechanism_class="t_type_calcium_blocker", primary_moa="T-type calcium channel block; first-line for absence seizures",
   evidence_tier="approved", indication="absence", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["calcium_channel_modulation"], half_life_class="long",
   safety_classes=["succinimide_class"], target_uncertainty=0.15, pathways=[CA],
   risk={"sedation_cognitive":0.3,"behavioural_mood":0.4},
   target_effects={"CACNA1G":-0.7,"CACNA1H":-0.7}),
 d(name="Retigabine (ezogabine)", mechanism_class="kv7_opener_carbamate", primary_moa="Kv7.2/7.3 opener; withdrawn worldwide in 2017 for retinal and skin pigmentation",
   evidence_tier="approved", indication="withdrawn", route="oral", cns_penetration=0.65, compartment="cns",
   therapeutic_axes=["potassium_channel_opening"], half_life_class="short",
   safety_classes=["kv7_opening", "pigmentation_toxicity"], target_uncertainty=0.2, pathways=[K],
   risk={"retinal_toxicity":0.85,"dermatologic_hypersensitivity":0.4,"sedation_cognitive":0.4},
   target_effects={"KCNQ2":0.85,"KCNQ3":0.85}),
 d(name="Azetukalner (XEN1101)", mechanism_class="kv7_opener_anilide", primary_moa="Potent Kv7.2/7.3 opener designed to avoid the pigmentation liability; positive phase 3 in focal seizures",
   evidence_tier="phase_3", indication="focal", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["potassium_channel_opening"], half_life_class="long",
   safety_classes=["kv7_opening"], target_uncertainty=0.3, pathways=[K],
   risk={"sedation_cognitive":0.4,"behavioural_mood":0.2},
   target_effects={"KCNQ2":0.9,"KCNQ3":0.9}),
 d(name="Acetazolamide", mechanism_class="carbonic_anhydrase_inhibitor", primary_moa="Carbonic anhydrase inhibition; adjunct including catamenial seizures",
   evidence_tier="approved", indication="adjunct", route="oral", cns_penetration=0.4, compartment="both",
   therapeutic_axes=["neuromodulatory_adjunct"], half_life_class="short",
   safety_classes=["carbonic_anhydrase_inhibition"], target_uncertainty=0.3, pathways=["metabolic_oxidative"],
   risk={"sedation_cognitive":0.2,"dermatologic_hypersensitivity":0.2},
   target_effects={"CA2":-0.8}),
 d(name="Cannabidiol", mechanism_class="cannabinoid_multitarget", primary_moa="Multi-target: GPR55 antagonism, TRPV1 modulation and adenosine reuptake effects; used in Dravet and Lennox-Gastaut syndromes",
   evidence_tier="approved", indication="dravet_lennox_gastaut", route="oral", cns_penetration=0.7, compartment="cns",
   therapeutic_axes=["neuromodulatory_adjunct", "epileptogenesis_modification"], half_life_class="long",
   safety_classes=["cannabinoid_class"], target_uncertainty=0.5, pathways=[NEUMOD, INF],
   risk={"hepatic":0.5,"sedation_cognitive":0.5},
   target_effects={"GPR55":-0.5,"TRPV1":-0.3,"ADORA1":0.2,"SCN2A":-0.2,"TNF":-0.15}),
 # --- epileptogenesis and disease modification -----------------------------------
 d(name="Everolimus", mechanism_class="mtor_inhibitor", primary_moa="mTORC1 inhibition; approved as adjunct for seizures in tuberous sclerosis",
   evidence_tier="approved", indication="tsc_associated_seizures", route="oral", cns_penetration=0.3, compartment="both",
   therapeutic_axes=["epileptogenesis_modification"], half_life_class="long",
   safety_classes=["mtor_immunosuppression"], target_uncertainty=0.25, pathways=[MTOR],
   risk={"hematologic":0.4,"hepatic":0.2,"dermatologic_hypersensitivity":0.2},
   target_effects={"MTOR":-0.8,"RPS6KB1":-0.7}),
 d(name="Bumetanide", mechanism_class="nkcc1_inhibitor", primary_moa="NKCC1 inhibition to restore chloride gradients; neonatal seizure trial missed its endpoint and was stopped for hearing loss",
   evidence_tier="phase_2", indication="failed", route="oral", cns_penetration=0.1, compartment="peripheral",
   therapeutic_axes=["epileptogenesis_modification"], half_life_class="short",
   safety_classes=["loop_diuretic"], target_uncertainty=0.5, pathways=["chloride_homeostasis"],
   risk={"cardiac":0.2,"sedation_cognitive":0.1},
   target_effects={"SLC12A2":-0.7}),
 d(name="Soticlestat", mechanism_class="ch24h_inhibitor", primary_moa="Cholesterol 24-hydroxylase inhibition reducing 24S-hydroxycholesterol; phase 3 missed its primary endpoints in Dravet and Lennox-Gastaut syndromes",
   evidence_tier="phase_3", indication="failed", route="oral", cns_penetration=0.65, compartment="cns",
   therapeutic_axes=["epileptogenesis_modification"], half_life_class="intermediate",
   safety_classes=["cholesterol_metabolism"], target_uncertainty=0.45, pathways=["metabolic_oxidative", GLU],
   risk={"sedation_cognitive":0.2},
   target_effects={"CYP46A1":-0.85,"GRIN2B":-0.25}),
 d(name="Anakinra", mechanism_class="il1_receptor_antagonist", primary_moa="IL-1 receptor antagonist; off-label in febrile infection-related epilepsy",
   evidence_tier="phase_2", indication="fires", route="subcutaneous", cns_penetration=0.1, compartment="peripheral",
   therapeutic_axes=["epileptogenesis_modification"], half_life_class="short",
   safety_classes=["injection_reaction"], target_uncertainty=0.5, pathways=[INF],
   risk={"hematologic":0.2},
   target_effects={"IL1R1":-0.8,"IL1B":-0.35}),
 d(name="P2X7 antagonist (class exemplar)", mechanism_class="p2x7_antagonist", primary_moa="Blocks the ATP-gated channel upstream of the inflammasome; evidence extrapolated from other indications",
   evidence_tier="phase_2", indication="disease_modifying", route="oral", cns_penetration=0.6, compartment="cns",
   therapeutic_axes=["epileptogenesis_modification"], half_life_class="intermediate",
   safety_classes=["innate_immune_suppression"], target_uncertainty=0.55, pathways=[INF],
   risk={"hematologic":0.1,"hepatic":0.1},
   target_effects={"P2RX7":-0.8,"IL1B":-0.5,"NLRP3":-0.3,"IL6":-0.2}),
]

CONTROLS = {
    "positive_redundancy": ["Carbamazepine", "Oxcarbazepine"],
    "negative_efficacy": ["Bumetanide", "Soticlestat", "Talampanel"],
    "safety_penalty": ["Felbamate", "Retigabine (ezogabine)", "Vigabatrin"],
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
            f"Panel references genes absent from the epilepsy signature: {unknown}\n"
            "Add them to data/ep_expression.csv or correct the symbol."
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
            "generated_by": "tools/curate_epilepsy_panel.py",
            "disease": "epilepsy",
            "purpose": "Mechanism-curated candidate panel for research prioritisation. Not a prescribing, efficacy, or co-administration dataset.",
            "curation_rule": "Approved antiseizure medications plus disease-modifying candidates. Unlike the neurodegenerative panels this one is dominated by approved agents (30 of 37), because epilepsy has many effective symptomatic drugs and almost no approved disease-modifying ones. It therefore carries three negative-efficacy controls, fewer than the other diseases, all of them verified failures.",
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
            "caveat": "Directional target effects are curated hypotheses, not measured pharmacology. Several mechanisms (SV2A, cenobamate's GABA-A action, cannabidiol) are not settled, and their target_uncertainty is set accordingly. Every record requires independent verification before publication use.",
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
