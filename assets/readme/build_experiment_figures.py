"""Build explanatory experiment diagrams; no model calls or measured results.

Run: python assets/readme/build_experiment_figures.py --render-png
The architecture specimen is a separate, unchanged generated evidence artifact.
"""
from __future__ import annotations

import argparse

from build_research_figures import BLUE, GOLD, INK, MUTED, Figure


def overview():
    f = Figure(930, "From a fictional project to a scored review",
               "Six steps: generate project context, architecture, and evidence; let an AI investigate; record gate decisions; score against a hidden reference. The reference reaches the evaluator only.",
               "EXPERIMENT WALKTHROUGH / HOW THE TEST WORKS")
    f.text(48, 128, "The generator builds the case. The AI under test reviews it. The evaluator checks its work.", 21, MUTED)
    cards = [
        (48, 175, "01 / PROJECT CONTEXT", "A business scenario", ["Buy, integrate, or build", "Users, budget, data, owners", "Constraints and target dates"]),
        (493, 175, "02 / TECHNICAL DESIGN", "An architecture", ["Applications, networks, identity", "Data stores and information flows", "Backup and recovery design"]),
        (938, 175, "03 / REVIEW DOSSIER", "Evidence to examine", ["Project brief and review requests", "Diagrams, contracts, test records", "Some evidence may be incomplete"]),
        (48, 470, "04 / AI INVESTIGATION", "Read and cross-check", ["Inspect documents and diagrams*", "Query simulated company systems", "Resolve gaps and contradictions"]),
        (493, 470, "05 / GATE DECISIONS", "Explain and hand over", ["Findings, evidence, required actions", "Decision and authorization checks", "Earlier reviews inform later ones**"]),
        (938, 470, "06 / EVALUATION", "Compare with the reference", ["Decision, findings, actions, evidence", "Permissions and route completion", "Recorded cost and technical failures"]),
    ]
    for x, y, label, title, lines in cards:
        f.rect(x, y, 414, 217)
        f.text(x+22, y+34, label, 13, BLUE, weight="700", spacing="1")
        f.text(x+22, y+77, title, 23, INK, weight="700")
        f.lines(x+22, y+119, lines, 17, step=29)
    for y in (280, 575):
        for x in (465, 910):
            f.path(f"M{x} {y} H{x+21}", "#627f90", arrow=True)
    f.path("M1145 395 V428 H255 V462", "#627f90", arrow=True)
    f.rect(48, 727, 842, 77, "#fbf3e7", "#d8bb90")
    f.text(70, 756, "EVALUATOR ONLY / HIDDEN REFERENCE", 13, GOLD, weight="700", spacing="1")
    f.text(70, 786, "Known case facts + expected findings, actions, and decisions", 20, INK)
    f.path("M890 766 H1145 V695", GOLD, arrow=True, dash=True)
    f.text(48, 840, "* Image inspection depends on the vision setting and model.  ** In agent handoff mode.", 16, MUTED)
    f.footer("Sources: facts_engine.py · generate_dgfbench_v6.py · document_factory.py · openrouter_eval/ · evaluator.py")
    return f.save("experiment-walkthrough")


def worked_example():
    f = Figure(756, "A backup exists. But can the data actually be restored?",
               "Illustrative technical readiness review, not a measured model trace: backups are enabled but no successful restore test exists. The agent should investigate, cite evidence, request a restore test and choose REWORK if other checks pass.",
               "WORKED EXAMPLE / TECHNICAL READINESS")
    f.text(48, 128, "Illustrative scenario: backups are enabled; no successful restore test is available. Other checks pass.", 20, MUTED)
    panels = [
        (48, "1 / THE DOSSIER", "What the project presents", ["Architecture: a backup service", "Backup record: job is enabled", "Request: review readiness", "for production"]),
        (493, "2 / THE INVESTIGATION", "What the AI must verify", ["Read the supporting evidence", "Query get_backup_job", "Query get_restore_test", "Check that recovery was tested"]),
        (938, "3 / THE EXPECTED REVIEW", "What a justified answer says", ["Finding: no successful restore test", "Action: run a restore test", "Evidence: cite the inspected record", "Decision: REWORK"]),
    ]
    for x, label, title, lines in panels:
        f.rect(x, 181, 414, 268)
        f.text(x+22, 216, label, 13, BLUE, weight="700", spacing="1")
        f.text(x+22, 258, title, 22, INK, weight="700")
        f.lines(x+22, 302, lines, 18, step=32)
    for x in (465, 910):
        f.path(f"M{x} 319 H{x+21}", "#627f90", arrow=True)
    f.rect(48, 492, 1304, 110, "#fbf3e7", "#d8bb90")
    f.text(72, 526, "WHY THIS MATTERS", 13, GOLD, weight="700", spacing="1")
    f.text(72, 567, "Having a backup does not prove recovery works. A confident approval would miss the required check.", 21, INK)
    f.text(48, 645, "The evaluator checks the reasoning evidence and required action, as well as the decision.", 20, MUTED)
    f.footer("Rule: evaluator.py / TR-RESTORE-001 → RUN_RESTORE_TEST → REWORK. Example only; no model result is shown.")
    return f.save("experiment-restore-example")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-png", action="store_true")
    args = parser.parse_args()
    for path in (overview(), worked_example()):
        if args.render_png:
            import cairosvg
            cairosvg.svg2png(url=str(path), write_to=str(path.with_suffix(".png")), output_width=2100)
        print(path.name)
