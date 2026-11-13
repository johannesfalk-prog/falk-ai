import logging
from typing import Any, Tuple

logger = logging.getLogger("falk-backend")

TRANSITION_MATRIX = {
    1: {"allowed_next": [1, 2], "min_turns": 1},
    2: {"allowed_next": [1, 2, 3], "min_turns": 1},
    3: {"allowed_next": [1, 2, 3, 4], "min_turns": 1},
    4: {"allowed_next": [2, 3, 4, 5], "min_turns": 1},
    5: {"allowed_next": [3, 4, 5, 6], "min_turns": 1},
    6: {"allowed_next": [4, 5, 6, 7], "min_turns": 1},
    7: {"allowed_next": [1, 5, 6, 7], "min_turns": 1},
}

STAGE_TO_NUM = {
    "TRYGGHET": 1,
    "FORSTAELSE": 2,
    "FÖRSTÅELSE": 2,
    "UTFORSKANDE": 3,
    "PERSPEKTIV": 4,
    "KLARHET": 5,
    "HANDLING": 6,
    "REFLEKTION": 7,
}

NUM_TO_STAGE = {
    1: "TRYGGHET",
    2: "FÖRSTÅELSE",
    3: "UTFORSKANDE",
    4: "PERSPEKTIV",
    5: "KLARHET",
    6: "HANDLING",
    7: "REFLEKTION",
}


class FalkStateMachine:
    @staticmethod
    def normalize_stage(stage_or_num: Any) -> Tuple[int, str]:
        if isinstance(stage_or_num, int) or (isinstance(stage_or_num, str) and stage_or_num.strip().isdigit()):
            num = int(str(stage_or_num).strip())
            num = num if 1 <= num <= 7 else 1
            return num, NUM_TO_STAGE[num]
        key = str(stage_or_num or "TRYGGHET").strip().upper()
        num = STAGE_TO_NUM.get(key, 1)
        return num, NUM_TO_STAGE[num]

    @staticmethod
    def resolve_next_phase(
        current_phase: int,
        proposed_phase: int,
        turns_in_current_phase: int,
        crisis_status: str,
    ) -> int:
        if crisis_status in ["ACUTE_CRISIS", "FAIL_SAFE_CAUTION"]:
            logger.warning(f"STATE MACHINE OVERRIDE: Krisstatus {crisis_status}. Tvingar återgång till Fas 1.")
            return 1

        try:
            curr = int(current_phase)
            if curr < 1 or curr > 7:
                curr = 1
        except (ValueError, TypeError):
            curr = 1

        try:
            prop = int(proposed_phase)
            if prop < 1 or prop > 7:
                prop = 1
        except (ValueError, TypeError):
            prop = 1

        allowed_list = TRANSITION_MATRIX.get(curr, TRANSITION_MATRIX[1])["allowed_next"]

        if prop in allowed_list:
            return prop

        if prop > curr:
            clamped = max(allowed_list)
            logger.warning(f"STATE MACHINE CLAMPED: Försökte hoppa från Fas {curr} till {prop}. Låst till Fas {clamped}.")
            return clamped

        return prop
