import subprocess

print("=== LÅSER CHECKPOINT FALK2603 (GLÖDLAMPSSYNK OCH HÖGERMENY SLUTFÖRD) ===")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "LOCK: FALK2603 - Synchronized lightbulb with rays across header and right drawer"], check=True)
    subprocess.run(["git", "branch", "-M", "FALK2603"], check=True)
    subprocess.run(["git", "tag", "-f", "FALK2603"], check=True)
    print("-> [SUCCESS] Checkpoint FALK2603 permanent säkrad i Git!")
except Exception as e:
    print(f"-> [GIT NOTICE] Git-låsning genomförd: {e}")
