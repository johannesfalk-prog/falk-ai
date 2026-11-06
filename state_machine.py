import logging

logger = logging.getLogger("falk-backend")

TRANSITION_MATRIX = {
    1: {"allowed_next": [1, 2], "min_turns": 1},
    2: {"allowed_next": [1, 2, 3], "min_turns": 1},
    3: {"allowed_next": [1, 2, 3, 4], "min_turns": 1},
    4: {"allowed_next": [2, 3, 4, 5], "min_turns": 1},
    5: {"allowed_next": [3, 4, 5, 6], "min_turns": 1},
    6: {"allowed_next": [4, 5, 6, 7], "min_turns": 1},
    7: {"allowed_next": [1, 5, 6, 7], "min_turns": 1}
}

class FalkStateMachine:
    @staticmethod
    def resolve_next_phase(current_phase: int, proposed_phase: int, turns_in_current_phase: int, crisis_status: str) -> int:
        if crisis_status in ["ACUTE_CRISIS", "FAIL_SAFE_CAUTION"]:
            logger.warning(f"🚨 STATE MACHINE OVERRIDE: Kris status {crisis_status}. Tvingar återgång till Fas 1.")
            return 1

        try:
            curr = int(current_phase)
            if curr < 1 or curr > 7:
                curr = 1
        except:
            curr = 1

        try:
            prop = int(proposed_phase)
            if prop < 1 or prop > 7:
                prop = 1
        except:
            prop = 1

        allowed_list = TRANSITION_MATRIX.get(curr, TRANSITION_MATRIX[1])["allowed_next"]

        if prop in allowed_list:
            return prop

        # Om föreslagen fas är högre än tillåtet, tvinga max tillåtna steg (t.ex. från 1 till 2)
        if prop > curr:
            clamped = max(allowed_list)
            logger.warning(f"🛡️ STATE MACHINE CLAMPED: Försökte hoppa från Fas {curr} till {prop}. Låst till Fas {clamped}.")
            return clamped

        return prop
