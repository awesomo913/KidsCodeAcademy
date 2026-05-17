# From: build.py:57
# v0.7: validate sandbox JSONs before bundling — abort build on any malformed file.

def step_sandbox_lint() -> None:
    """v0.7: validate sandbox JSONs before bundling — abort build on any malformed file.

    Catches typos that the runtime would silently mask via the generic fallback
    string. Exit 1 from sandbox_lint.py propagates via subprocess.run(check=True).
    """
    log.info("=== step 1b: validating sandbox JSONs ===")
    run([sys.executable, "scripts/sandbox_lint.py", "--quiet"])
