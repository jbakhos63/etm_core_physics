# Euclidean Timing Mechanics 

A fully discrete, modular, rhythm-based model of physics capable of deriving fundamental physical constants from timing behavior alone.

---

## 📄 Final ETM Documents

The complete and authoritative theory of Euclidean Timing Mechanics is available here:  
[📥 Download Euclidean_Timing_Mechanics.pdf](docs/Euclidean_Timing_Mechanics.pdf)

## 📄 Formal Derivation Paper

The complete mathematical derivation of fundamental physical constants from ETM logic is available here:

[👉 A Symbolic Axiomatic System for the Derivation of Physical Constants from Discrete Modular Logic (PDF)](docs/A_Symbolic_Axiomatic_System_for_the_Derivation_of_Physical_Constants_from_Discrete_Modular_Logic.pdf)

---

## 🧠 Model Summary

- **Ontology:** Discrete rhythms replace geometry. Recruiters replace fields. Identities are timing patterns.
- **Core Logic:**
  - Nodes tick under recruiter support
  - Phase alignment determines identity return
  - Echo fields guide rotor propagation
- **Constants Derived:**
  - Speed of light \( c \)
  - Permittivity \( \varepsilon_0 \)
  - Permeability \( \mu_0 \)
  - Planck's constant \( h \) and \( \hbar \)
  - Fine-structure constant \( \alpha \)
  - Gravitational constant \( G \)
  - Coulomb constant \( k_e \)

---

## 🧪 Reproducibility and Usage

This repository contains all code and logic needed to reproduce the results in the ETM paper.  
When unzipping, watch out for a duplication of the filename `etm_core_physics`.  
The unzip might nest a folder of the same name within itself.  
The relevant files will be in the lowest `etm_core_physics` folder.

### Folder Structure

- `trials/` – All new Python simulation scripts (trial_001 to trial_018)
- `oldtrials/` – All old Python simulation scripts (trial_001 to trial_208)
- `Results/` – Summarized output from each simulation
- `results99/` – This is a record of the original results of the author — Summarized output from over 200 old simulations
- `results100/` – This is a record of the original results of the author — Summarized output from each of 18 newly updated simulations
- `docs/` – Theoretical documentation and figures

### Running a Trial

From your terminal, navigate to the `trials/` folder and type as an example:

```bash
python trial_208_etm_speedoflight_constant.py

