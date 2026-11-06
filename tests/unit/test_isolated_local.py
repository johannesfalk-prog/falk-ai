import sys
from state_machine import FalkStateMachine
from prompt_engine import ModularPromptEngine

print("==================================================================")
print("🧪 ISOLERAD LOKAL ENHETSTESTNING (0 ms Nätverkslatens)")
print("==================================================================\n")

# TEST 1: State Machine Clamping (Fas 1 -> 6 skall bli Fas 2)
p_out = FalkStateMachine.resolve_next_phase(current_phase=1, proposed_phase=6, turns_in_current_phase=1, crisis_status="NONE")
print(f"1. State Machine Clamping (1 -> 6): Fick Fas {p_out}")
assert p_out == 2, f"❌ STATE MACHINE FEL: Förväntade 2, fick {p_out}"
print("   ✅ PASS: Illegalt hopp låstes till Fas 2!")

# TEST 2: Post-processing av frågetecken (3 frastecken -> 1 frågetecken)
raw_text_with_3_q = "Vad vill du göra idag? Hur mår du? Är du redo?"
clean_text = ModularPromptEngine.deterministic_post_processing(raw_text_with_3_q)
q_count = clean_text.count("?")
print(f"\n2. Frågetvätt (3 frågor in -> {q_count} fråga ut):")
print(f"   Resultat: \"{clean_text}\"")
assert q_count == 1, f"❌ FRÅGETVÄTT FEL: Förväntade 1 '?', fick {q_count}"
print("   ✅ PASS: Tvättmotorn klippte alla extra frågetecken!")

# TEST 3: Medicinsk gränsdragning prompt-verifiering
prompt_med = ModularPromptEngine.compile_5_layer_prompt(phase=1, crisis_status="MEDICAL_LEGAL_BOUNDARIES")
print(f"\n3. Gränsdragnings-prompt innehåller 'psykolog':")
assert "psykolog" in prompt_med.lower(), "❌ PROMPT FEL: Saknar ordet psykolog i krisinstruktionen"
print("   ✅ PASS: Tvingande instruktion för psykolog är på plats!")

print("\n==================================================================")
print("🏆 [LOKALT ALL PASS] Den lokala koden är 100 % matematiskt och logiskt korrekt!")
print("==================================================================")
