# ETM Timing and Identity Ruleset

This document defines the modular timing rules used in Euclidean Timing Mechanics (ETM). These rules support simulation and interpretation by both humans and AI logic systems. They define rotor identity, recruiter structure, and modular locking behavior.

---

## 1. Time and Space Units

- **Tick (t):** Discrete unit of time.
  - 1 tick = 1.3207 × 10⁻⁹ seconds
- **ETM Unit:** Discrete unit of length.
  - 1 unit = 0.3959 meters

All propagation and rhythm behavior is expressed as integer or modular steps through these units.

---

## 2. Rotor Identity Structure

Each rotor has the following attributes:

- **phase** ∈ [0.0, 1.0) (modular timing phase)
- **velocity**: number of ETM units per tick (default: 0.3959)
- **ancestry_tag**: unique identity label (e.g., "rotorA", "rotorX")
- **spin_tag**: one of {"up", "down", "none"}
- **position**: updated each tick by:
  ```
  position += velocity
  ```

---

## 3. Recruiter Field Structure

Recruiters are defined as spatial bands at fixed positions. Each recruiter band carries a phase function:

```
recruiter_phase(t, distance) = base_phase + (gradient × distance) + (rotation_bias × t)
```

- **gradient**: controls spatial curvature (e.g., 0.01–0.05)
- **rotation_bias**: defines recruiter twist over time (e.g., 0.0–0.2)
- **support_threshold**: number of recruiters that must agree for a rotor to lock (typically 3)

---

## 4. Locking Logic

Rotor locking occurs when:

1. Rotor is within range of recruiter bands.
2. For each recruiter, compute:
   ```
   phase_diff = abs((recruiter_phase - rotor_phase + 0.5) % 1.0 - 0.5)
   ```
3. If at least `support_threshold` recruiters have:
   ```
   phase_diff < phase_tolerance (e.g., 0.05)
   ```
   then the rotor is considered "locked".

On lock:
- Record tick and position
- Optionally record ancestry and spin

---

## 5. Reformation and Identity Return

Rotors may reform a modular identity after dropout if recruiter support and phase match are reestablished.

Optional exclusion rules may prevent reformation if:
- An identity with the same ancestry and spin already occupies the rhythm
- Recruiter memory prevents duplicate resonance

---

## 6. Derived Constants

Measured from simulation:

- **ε_ETM** ≈ 2.2 ticks/return (phase curvature)
- **μ_ETM** ≈ 2.9 ticks/return (rotation bias)
- **c_ETM** ≈ 0.3959 units/tick (speed of rotor through both fields)

Mapped to SI units:

- **ε₀** ≈ 2.91 × 10⁻⁹ s
- **μ₀** ≈ 3.83 × 10⁻⁹ s
- **c** = 299,792,458 m/s

---

## 7. Notes

- All behavior is modular and distributed. No centralized force or memory is required.
- Rotor identity, timing, and propagation emerge from local rhythm relationships.
- This ruleset is suitable for symbolic logic engines, reasoning systems, or physics simulators.

