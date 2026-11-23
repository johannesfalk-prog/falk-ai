import logging
from typing import Any, Tuple

logger = logging.getLogger("falk-backend")

TRANSITION_MATRIX = {
    1: {"allowed_next": [1, 2], "min_turns": 1, "max_turns": 2},
    2: {"allowed_next": [1, 2, 3], "min_turns": 1, "max_turns": 2},
    3: {"allowed_next": [1, 2, 3, 4], "min_turns": 1, "max_turns": 3},
    4: {"allowed_next": [2, 3, 4, 5], "min_turns": 1, "max_turns": 2},
    5: {"allowed_next": [3, 4, 5, 6], "min_turns": 1, "max_turns": 2},
    6: {"allowed_next": [4, 5, 6, 7], "min_turns": 1, "max_turns": 2},
    7: {"allowed_next": [1, 5, 6, 7], "min_turns": 1, "max_turns": 99},
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
        is_stressed: bool = False,
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

        try:
            turns = max(0, int(turns_in_current_phase))
        except (ValueError, TypeError):
            turns = 0

        phase_cfg = TRANSITION_MATRIX.get(curr, TRANSITION_MATRIX[1])
        allowed_list = phase_cfg["allowed_next"]
        max_turns = phase_cfg.get("max_turns", 2)

        if is_stressed:
            max_turns += 1
            if curr >= 3 and prop > curr:
                logger.info(
                    f"STATE MACHINE STRESS HOLD: Användaren är stressad i Fas {curr}. Håller kvar i Fas {curr} för reglering."
                )
                return curr

        if curr < 7 and turns >= max_turns and prop <= curr:
            forced_next = min(curr + 1, 7)
            logger.info(
                f"STATE MACHINE PROACTIVE ADVANCE: {turns} turer i Fas {curr} (tak={max_turns}). "
                f"Tvingar övergång från Fas {curr} ({NUM_TO_STAGE[curr]}) till Fas {forced_next} ({NUM_TO_STAGE[forced_next]})."
            )
            return forced_next

        if prop in allowed_list:
            return prop

        if prop > curr:
            clamped = max(allowed_list)
            logger.warning(f"STATE MACHINE CLAMPED: Försökte hoppa från Fas {curr} till {prop}. Låst till Fas {clamped}.")
            return clamped

        return prop
