import logging

logger = logging.getLogger("falk-backend")

# WAYJS STATE TRANSITION MATRIX (Playbook Kap 5 & 7)
TRANSITION_MATRIX = {
    1: {"allowed_next": [1, 2], "min_turns": 1, "name": "TRYGGHET"},
    2: {"allowed_next": [1, 2, 3], "min_turns": 1, "name": "FÖRSTÅELSE"},
    3: {"allowed_next": [1, 2, 3, 4], "min_turns": 1, "name": "UTFORSKANDE"},
    4: {"allowed_next": [2, 3, 4, 5], "min_turns": 1, "name": "PERSPEKTIV"},
    5: {"allowed_next": [3, 4, 5, 6], "min_turns": 1, "name": "KLARHET"},
    6: {"allowed_next": [4, 5, 6, 7], "min_turns": 1, "name": "HANDLING"},
    7: {"allowed_next": [1, 5, 6, 7], "min_turns": 1, "name": "REFLEKTION"}
}

class FalkStateMachine:
    @staticmethod
    def resolve_next_phase(current_phase: int, proposed_phase: int, turns_in_current_phase: int, crisis_status: str) -> int:
        """
        Garanterar deterministiska fas-övergångar.
        Klipper olagliga kliv framåt och tvingar återgång till Fas 1 vid kris.
        """
        # 1. AKUT KRIS: Tvinga omedelbar återgång till Fas 1 (Trygghet)
        if crisis_status in ["ACUTE_CRISIS", "FAIL_SAFE_CAUTION"]:
            logger.warning(f"🔄 STATE MACHINE OVERRIDE: Kris status {crisis_status}. Tvingar återgång till Fas 1.")
            return 1

        current_phase = int(current_phase) if 1 <= int(current_phase) <= 7 else 1
        proposed_phase = int(proposed_phase) if 1 <= int(proposed_phase) <= 7 else 1

        config = TRANSITION_MATRIX.get(current_phase, TRANSITION_MATRIX[1])
        allowed = config["allowed_next"]

        # 2. Om föreslagen fas är tillåten och min_turns uppfylls
        if proposed_phase in allowed:
            if proposed_phase > current_phase and turns_in_current_phase < config["min_turns"]:
                logger.info(f"🛡️ STATE MACHINE: Bromsar kliv från Fas {current_phase} till {proposed_phase} (kräver minst {config['min_turns']} svarsrunda).")
                return current_phase
            return proposed_phase

        # 3. Klipp olagliga kliv framåt (t.ex. 1 -> 6 sätts till max tillåtna 2)
        if proposed_phase > current_phase:
            max_allowed_step = max(allowed)
            logger.warning(f"🚨 STATE MACHINE BLOCKED JUMP: Försökte hoppa från Fas {current_phase} till {proposed_phase}. Klippt till Fas {max_allowed_step}.")
            return max_allowed_step

        # 4. Tillåt backsteg (t.ex. 5 -> 2 vid otydlighet)
        return proposed_phase
