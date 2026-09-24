"""Render explanatory diagrams of the frozen benchmark's verification sequence.

Run: python assets/readme/build_verification_figures.py --render-png
English versions serve the README; French versions explain the same flow.
No inference, scoring, or experimental artifact modification is performed.
"""
from __future__ import annotations

import argparse
from build_research_figures import BLUE, INK, MUTED, Figure

GREEN = '#287d68'
AMBER = '#986323'


def timing(fr=False):
    title = 'À quel moment vérifie-t-on l’agent ?' if fr else 'When is the agent checked?'
    f = Figure(820, title, title,
               'DGF-BENCH / CONTRÔLES ET CHRONOLOGIE' if fr else 'DGF-BENCH / CHECKS AND TIMING')
    f.text(48, 128,
           'Deux contrôles distincts : les actions pendant la revue, puis les résultats du parcours.' if fr else
           'Two distinct checks: tool actions during a review, then results after the dossier’s route.', 21, MUTED)
    cards = [
        (48, '01 / PENDANT CHAQUE GATE' if fr else '01 / DURING EACH GATE',
         'L’outil contrôle la demande' if fr else 'The tool checks the request',
         ['Exemple : demander une approbation conditionnelle.',
          'Le mandat couvre-t-il cette gate et cette phase ?',
          'Tous les problèmes sont-ils inclus et éligibles ?',
          'Des conditions non vides sont-elles fournies ?'] if fr else
         ['Example: request a conditional approval.',
          'Does the mandate cover this gate and phase?',
          'Are all open findings covered and eligible?',
          'Are nonempty conditions supplied?']),
        (716, '02 / APRÈS LE PARCOURS DU DOSSIER' if fr else '02 / AFTER THE DOSSIER’S ROUTE',
         'Le correcteur évalue chaque gate' if fr else 'The scorer evaluates every gate',
         ['Un programme Python compare la réponse à la référence.',
          'Il examine la décision et les problèmes identifiés,',
          'les actions proposées, les preuves et l’autorisation.',
          'Il utilise aussi la trace des appels aux outils.'] if fr else
         ['A Python program compares the output to the reference.',
          'It checks the decision and identified findings,',
          'proposed actions, evidence, and authorization.',
          'It also inspects the recorded tool calls.']),
    ]
    for x, label, heading, lines in cards:
        f.rect(x, 172, 636, 314, '#f1f6f9', '#c9d9e3')
        f.text(x+24, 205, label, 14, BLUE, weight='700', spacing='1')
        f.text(x+24, 248, heading, 26, INK, weight='700')
        f.lines(x+24, 294, lines, 19, step=32)
    for x, w, text, color, fill in [
        (72, 268, 'Demande exécutée' if fr else 'Request executed', GREEN, '#e4f2ec'),
        (360, 300, 'Ou demande rejetée' if fr else 'Or request rejected', AMBER, '#fbefdc'),
        (740, 588, 'Résultat de conformité pour chaque gate' if fr else 'A conformity result for every gate', BLUE, '#e4eef5'),
    ]:
        f.rect(x, 432, w, 36, fill, fill, 5)
        f.text(x+w/2, 456, text, 18, color, weight='700', anchor='middle')
    f.text(48, 537, 'DÉROULEMENT D’UN DOSSIER' if fr else 'ONE DOSSIER, IN ORDER', 14, BLUE, weight='700', spacing='1')
    labels = [
        ['Revue gate 1', 'Réponse + trace'], ['Gates suivantes', 'Réponses de l’agent'],
        ['Gate General', 'Consolidation'], ['Scoring du parcours', 'Toutes les gates évaluées'],
    ] if fr else [
        ['Gate 1 review', 'Output + trace'], ['Following gates', 'Actual agent outputs'],
        ['General gate', 'Consolidation'], ['Route scoring', 'Every gate evaluated'],
    ]
    for i, (heading, detail) in enumerate(labels):
        x = 48 + 334*i
        f.rect(x, 565, 302, 92, '#e7f1f5' if i==3 else '#fcfdfd', '#c9d9e3')
        f.text(x+151, 601, heading, 21, INK, weight='700', anchor='middle')
        f.text(x+151, 634, detail, 18, MUTED, anchor='middle')
        if i<3:
            f.path(f'M{x+305} 611 H{x+326}', '#627f90', arrow=True)
    f.lines(48, 703,
            ['Les gates suivantes reçoivent les réponses réelles de l’agent, y compris leurs erreurs.',
             'Le correcteur final ne les réécrit pas avant leur transmission.'] if fr else
            ['Later gates receive the agent’s actual reviews, including any errors.',
             'The final scorer does not rewrite these reviews before they are passed onward.'], 20, step=30)
    f.footer('Code : synthetic_environment.py → benchmark_runner.py → score_submission.py (version figée).' if fr else
             'Code: synthetic_environment.py → benchmark_runner.py → score_submission.py (frozen benchmark version).')
    return f.save('verification-timing' + ('-fr' if fr else ''))


def criteria(fr=False):
    title = 'Quand une gate est-elle conforme ?' if fr else 'What makes a gate pass?'
    f = Figure(1000, title, title,
               'DGF-BENCH / RÈGLE DE RÉUSSITE STRICTE' if fr else 'DGF-BENCH / STRICT SUCCESS RULE')
    f.text(48, 128,
           'Le correcteur compare le résultat de l’agent aux exigences du contrat de revue.' if fr else
           'The scorer compares the agent’s result with the requirements of the review contract.', 21, MUTED)
    inputs = [
        ('Résultat attendu' if fr else 'Expected result',
         ['Faits du cas + règles applicables', 'Approbations conditionnelles validées prises en compte'] if fr else
         ['Case facts + applicable policy', 'Validated conditional approvals taken into account']),
        ('Résultat de l’agent' if fr else 'Agent result',
         ['Décision, problèmes, actions, preuves, autorisation', 'Trace des sources consultées et des outils utilisés'] if fr else
         ['Decision, findings, actions, evidence, authorization', 'Trace of observed sources and tool use']),
    ]
    for i,(heading,lines) in enumerate(inputs):
        x=48+i*668
        f.rect(x, 170, 636, 135, '#f1f6f9', '#c9d9e3')
        f.text(x+24, 207, heading, 24, INK, weight='700')
        f.lines(x+24, 245, lines, 19, step=31)
        f.path(f'M{x+318} 308 V327 H700 V347', '#627f90', arrow=True)
    tests = [
        ('Décision', 'La disposition correspond-elle au résultat attendu ?'),
        ('Problèmes', 'Tous les problèmes attendus sont présents, sans ajout incorrect.'),
        ('Actions proposées', 'Les actions proposées correspondent exactement aux actions requises.'),
        ('Preuves', 'Sources réellement consultées et extraits conformes au contrat.'),
        ('Autorisation', 'Indicateur correct ; approbation conditionnelle revalidée si utilisée.'),
    ] if fr else [
        ('Decision', 'Does the disposition match the required outcome?'),
        ('Findings', 'All expected findings are present, with no incorrect additions.'),
        ('Proposed actions', 'The proposed action set matches the required action set.'),
        ('Evidence', 'Sources were actually observed; excerpts meet the evidence contract.'),
        ('Authorization', 'Correct indicator; conditional approval revalidated when used.'),
    ]
    for i,(heading,detail) in enumerate(tests):
        y=358+i*72
        f.rect(48, y, 1304, 60, '#fcfdfd', '#d5dfe6', 6)
        f.rect(64, y+12, 39, 36, '#e4eef5', '#e4eef5', 5)
        f.text(83.5, y+37, str(i+1), 18, BLUE, weight='700', anchor='middle')
        f.text(121, y+38, heading, 21, INK, weight='700')
        f.text(360, y+38, detail, 20, MUTED)
    f.rect(48, 740, 1304, 67, '#e4f2ec', '#a8cdbd')
    f.text(700, 782,
           'Les 5 contrôles passent → la gate réussit strictement' if fr else
           'All 5 checks pass → strict gate success', 26, GREEN, weight='700', anchor='middle')
    f.rect(48, 822, 1304, 55, '#e4eef5', '#b7cddd')
    f.text(700, 857,
           'Toutes les gates réussissent → le parcours complet réussit' if fr else
           'Every gate passes → complete-route success', 23, BLUE, weight='700', anchor='middle')
    f.text(48, 919,
           'Une décision de refus correcte peut réussir. Les réparations physiques sont hors de ce test.' if fr else
           'A correct refusal can pass. Performing the physical remediation is outside this test.', 20, MUTED)
    f.footer('Code : score_submission.py et approval_policy.py. Les critères décrivent le score strict d’origine.' if fr else
             'Code: score_submission.py and approval_policy.py. Criteria describe the original strict score.')
    return f.save('verification-criteria' + ('-fr' if fr else ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-png', action='store_true')
    args = parser.parse_args()
    for fr in (False, True):
        for path in (timing(fr), criteria(fr)):
            if args.render_png:
                import cairosvg
                cairosvg.svg2png(url=str(path), write_to=str(path.with_suffix('.png')), output_width=2100)
            print(path.name)


if __name__ == '__main__':
    main()
