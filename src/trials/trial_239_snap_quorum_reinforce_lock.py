
# etm_trial239_snap_quorum_reinforce_lock.py

import json
from collections import defaultdict

SIZE = 17
NUM_STEPS = 1200
CENTER = SIZE // 2
PHI_INCREMENT = 0.05
TAU_Z = 0.975
TAU_E = 1.05
TAU_PHOTON = 1.00
TAU_NEUTRINO = 0.95
MEMORY_ECHO = 60
PHASE_TOL_STRICT = 0.03
PHASE_TOL_SNAP = 0.07
PHOTON_WINDOW = 20
LOCK_IN_DURATION = 20
REINFORCE_THRESHOLD = 2
QUORUM_REQUIRED = 2

def idx(x, y, z):
    return x * SIZE * SIZE + y * SIZE + z

ancestry_tag = "trial239_snap_quorum_reinforce_lock"

H1_pos = [CENTER - 2, CENTER, CENTER]
H2_pos = [CENTER + 2, CENTER, CENTER]
E1_pos = [CENTER - 3, CENTER, CENTER]
E2_pos = [CENTER + 3, CENTER, CENTER]
reconciliation_group = [
    (CENTER, CENTER, CENTER),
    (CENTER - 1, CENTER, CENTER),
    (CENTER + 1, CENTER, CENTER)
]

photon_ticks = list(range(50, 90, 2))
neutrino_ticks = list(range(200, 220))
neutrino_path = [(CENTER - 3 + i, CENTER, CENTER) for i in range(7)]

nodes = [{'module': 'None', 'memory': 0, 'phi': 0.0, 'tau': 1.0,
          'T': 0.0, 'ancestry': [], 'spin': None, 'age': 0}
         for _ in range(SIZE**3)]

photon_contact = defaultdict(list)
neutrino_contact = defaultdict(list)
reinforcement_score = defaultdict(int)
lock_tracker = defaultdict(int)

def place_moduleZ(pos, label):
    i = idx(*pos)
    nodes[i].update({
        'module': 'Z', 'memory': 200,
        'phi': 0.25, 'T': 0.50, 'tau': TAU_Z,
        'ancestry': [ancestry_tag, label, 'proton']
    })

def place_electron(pos, label, spin):
    i = idx(*pos)
    nodes[i].update({
        'module': 'G', 'memory': 80,
        'phi': 0.25, 'T': 0.50, 'tau': TAU_E,
        'ancestry': [ancestry_tag, label, 'electron'],
        'spin': spin
    })

place_moduleZ(H1_pos, 'H1')
place_moduleZ(H2_pos, 'H2')
place_electron(E1_pos, 'H1', 'up')
place_electron(E2_pos, 'H2', 'down')

trajectory = []
identity_locked = False
lock_in_tick = None

def ancestry_overlap(ancestry):
    return ancestry_tag in ''.join(ancestry) and 'H1' in ancestry and 'H2' in ancestry

for step in range(NUM_STEPS):
    next_nodes = [dict(n) for n in nodes]

    for pos in [H1_pos, H2_pos]:
        i = idx(*pos)
        node = nodes[i]
        node['T'] += node['tau']
        if node['T'] >= 1.0:
            node['T'] -= 1.0
            node['phi'] = (node['phi'] + PHI_INCREMENT) % 1.0

    phi_avg = (nodes[idx(*H1_pos)]['phi'] + nodes[idx(*H2_pos)]['phi']) / 2
    T_avg = (nodes[idx(*H1_pos)]['T'] + nodes[idx(*H2_pos)]['T']) / 2
    ancestry_combined = list(set(nodes[idx(*H1_pos)]['ancestry'] + nodes[idx(*H2_pos)]['ancestry']))

    eligible_nodes = []
    for pos in reconciliation_group:
        i = idx(*pos)
        node = nodes[i]
        delta_phi = abs(node['phi'] - phi_avg)
        delta_T = abs(node['T'] - T_avg)
        catalyst = any((step - t) <= PHOTON_WINDOW for t in photon_contact[i]) or any((step - t) <= PHOTON_WINDOW for t in neutrino_contact[i])
        score = 0

        if ancestry_overlap(node['ancestry']):
            score += 1
        if catalyst:
            score += 1
        if delta_phi <= PHASE_TOL_STRICT and delta_T <= PHASE_TOL_STRICT:
            score += 2
        elif delta_phi <= PHASE_TOL_SNAP and delta_T <= PHASE_TOL_SNAP and catalyst:
            score += 1
            next_nodes[i]['phi'] = phi_avg
            next_nodes[i]['T'] = T_avg

        if score >= REINFORCE_THRESHOLD:
            eligible_nodes.append(i)

    if not identity_locked and len(eligible_nodes) >= QUORUM_REQUIRED:
        for i in eligible_nodes:
            if nodes[i]['module'] == 'R':
                lock_tracker[i] += 1
            else:
                lock_tracker[i] = 1
            next_nodes[i]['module'] = 'R'
            next_nodes[i]['memory'] = 200
            next_nodes[i]['ancestry'] = ancestry_combined + ['snap_quorum_reinforce']

        if all(lock_tracker[i] >= LOCK_IN_DURATION for i in eligible_nodes):
            for i in eligible_nodes:
                next_nodes[i]['module'] = 'H2'
                next_nodes[i]['memory'] = 300
                next_nodes[i]['ancestry'] = ancestry_combined + ['locked_identity', 'H2_module']
            identity_locked = True
            lock_in_tick = step

    for pos in reconciliation_group:
        i = idx(*pos)
        next_nodes[i].update({
            'module': 'E',
            'memory': MEMORY_ECHO,
            'phi': phi_avg,
            'T': T_avg,
            'tau': TAU_Z,
            'ancestry': ancestry_combined + ['reinforced_echo']
        })
        if step in photon_ticks:
            next_nodes[i].update({
                'module': 'B',
                'memory': MEMORY_ECHO,
                'phi': phi_avg,
                'T': T_avg,
                'tau': TAU_PHOTON,
                'ancestry': ancestry_combined + ['photon_ping']
            })
            photon_contact[i].append(step)

    if step in neutrino_ticks:
        path_index = step - neutrino_ticks[0]
        if 0 <= path_index < len(neutrino_path):
            x, y, z = neutrino_path[path_index]
            i = idx(x, y, z)
            next_nodes[i].update({
                'module': 'N',
                'memory': 30,
                'phi': phi_avg,
                'T': T_avg,
                'tau': TAU_NEUTRINO,
                'ancestry': ancestry_combined + ['neutrino_catalyst']
            })
            neutrino_contact[i].append(step)

    trajectory.append({
        'tick': step,
        'phi_avg': phi_avg,
        'T_avg': T_avg,
        'identity_locked': identity_locked
    })

    for i, node in enumerate(nodes):
        node['T'] += node['tau']
        if node['T'] >= 1.0:
            node['T'] -= 1.0
            node['phi'] = (node['phi'] + PHI_INCREMENT) % 1.0
        next_nodes[i]['T'] = node['T']
        next_nodes[i]['phi'] = node['phi']
        next_nodes[i]['memory'] -= 1
        if next_nodes[i]['memory'] <= 0:
            next_nodes[i]['module'] = 'None'
            next_nodes[i]['ancestry'] = []

    nodes = next_nodes

summary = {
    'trial': '239_snap_quorum_reinforce_lock',
    'tau_Z': TAU_Z,
    'tau_electron': TAU_E,
    'tau_photon': TAU_PHOTON,
    'tau_neutrino': TAU_NEUTRINO,
    'lock_in_tick': lock_in_tick,
    'identity_locked': identity_locked,
    'trajectory': trajectory
}

with open("etm_trial239_snap_quorum_reinforce_lock_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
