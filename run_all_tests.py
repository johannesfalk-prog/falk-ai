import subprocess
import sys

def run_step(title, command):
    print(f"\n==================================================================")
    print(f"🔄 KÖR: {title}")
    print(f"==================================================================")
    res = subprocess.run(command, shell=True)
    if res.returncode != 0:
        print(f"\n❌ ETT ELLER FLERA TESTER MISSLYCKADES I: {title}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    print("🦅 FALK AI / WAYJS – CENTRAL TEST RUNNER (KAPITEL 13)")
    
    # 1. Isolerad enhetstestning (0 ms)
    run_step("1. Isolerad enhetstestning i minnet", "python3 tests/unit/test_isolated_local.py")
    
    print("\n🏆 ALLA LOKALA ENHETSTESTER PASSERADE!")
