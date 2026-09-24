# Revue des deux manuscrits et du README — 24 septembre 2026

**Résultat : revue du contenu et vérifications locales terminées ; accès public vérifié.** Les chiffres principaux ne changent pas. Le dépôt était initialement privé. Après autorisation explicite de l'auteur le 24 septembre 2026, il a été rendu public. Le dépôt, la page de release, le README et les 24 téléchargements de release répondent sans authentification. Les deux PDF et les deux paquets arXiv minimaux ont aussi été téléchargés sans connexion : leurs empreintes correspondent aux fichiers vérifiés localement.

## Remplacement ultérieur du deuxième manuscrit

À la demande de l'auteur, le deuxième article de 22 pages a ensuite été remplacé par **The Last Human Gate: Forward Deployed Engineering for Governance Automation**, une version initialement courte de 12 pages, puis développée en **25 pages** à sa demande. Le présent rapport décrit la revue des versions antérieures ; la [note de réécriture](../paper2/REVIEW_RESPONSE.md), le [rapport actuel](../paper2/arxiv_verification.json) et la [fiche de dépôt](../paper2/ARXIV_SUBMISSION.md) font référence pour le nouveau deuxième article. Les données expérimentales et le premier PDF de 66 pages sont conservés.

## Périmètre

- Premier manuscrit : tous les 37 fichiers TeX réellement inclus, sections, annexes, tableaux, 48 références bibliographiques et notes mathématiques associées. PDF final de 66 pages ; notes de 3 pages.
- Deuxième manuscrit : les 14 fichiers TeX inclus, tableaux et matrices, 16 références ; PDF final de 22 pages.
- README principal lu en entier, ses 11 illustrations, les 65 chemins locaux distincts, les ancres et les commandes. Documentation de liaison et consignes de compilation actualisées.
- Résultats originaux, comparateur déterministe, audits des preuves, approbations, sources Procurement, répétitions, inventaire des sources et statut des travaux préparés.

## Corrections

| Élément | Correction |
|---|---|
| Notes mathématiques | Le lemme de concavité n'affirme plus une équivalence sans condition excluant les densités plates. La condition supplémentaire de la réciproque est explicite. |
| Notes mathématiques | Les conditions de Hessienne définie négative sont qualifiées de suffisantes pour un maximum strict, et non nécessaires à tous les maxima stricts. |
| Premier manuscrit | Une table de positionnement présentait des conséquences sur le travail comme mesurées ; elle décrit désormais le cadre comptable effectivement proposé. |
| Premier manuscrit | La description de l'article 22 du RGPD précise les effets juridiques ou similaires significatifs et les exceptions/sauvegardes, après vérification d'EUR-Lex. |
| Premier manuscrit | Le paramètre « difficulté 4 » et le rééchantillonnage conditionné aux décisions sont expliqués sans prétendre à une échelle de difficulté validée. |
| Premier manuscrit | La légende obsolète annonçant une illustration de 26 occurrences ailleurs dans le paper est retirée. Les trois routes évaluées restent 6 + 6 + 5 gates. |
| Premier manuscrit | La figure de trajectoire ne coupe plus l'introduction de l'annexe du contrat. La portée réelle des tests de reproduction est précisée. |
| Deuxième manuscrit | Le projet General-only décrit les historiques normalisés, la sélection sur désaccord, le maintien des approbations, le target commun et les effets possibles du feedback des outils. Il reste non exécuté. |
| Deuxième manuscrit | Le vérificateur contrôle aussi les 75 cellules effectivement imprimées des matrices de confusion et les comptes/statuts du projet General. |
| README | Le classement par gates est distingué des routes : Luna et DeepSeek sont à égalité à 4/15 routes au troisième repeat. Les nombres de pages sont actualisés. |
| Commandes du README | Les 25 options ont été vérifiées dans la version Git publiée, et pas seulement le répertoire de travail. Le lanceur publié ne charge pas automatiquement `.env` : la variable d'environnement ou la saisie masquée sont recommandées. NumPy et Matplotlib sont ajoutés à la commande d'installation avant les tests du paper ; la source figée reste la référence pour reproduire l'expérience. |
| Schéma partagé | Les faits accessibles aux agents sont distingués de la clé des réponses réservée à l'évaluateur, dans le SVG, le PNG et les deux PDF. |
| Compilation et documentation | Marges du deuxième PDF corrigées à 2,54 cm, références mises en forme, deux paquets arXiv minimaux vérifiés, notes de sources obsolètes corrigées. |

Les scénarios FDE/FTE et l'hypothèse historique de −80 % de FTE en 2033 restent présents. Cette hypothèse n'est pas convertie en résultat mesuré. Aucune évaluation humaine, aucun recrutement et aucun nouvel appel de modèle n'ont été ajoutés.

## Vérifications réalisées

1. Les trois archives originales sont contrôlées par SHA-256 et inventaire, puis les agrégats sont recalculés avec la source figée : 899 runs évaluables, 5 094 gates, 299 cas communs et USD 87.015829172 retrouvés.
2. Le contrôle déterministe est rescorré sur les 300 dossiers avec le scorer figé : 1 700/1 700 gates et 300/300 routes, identiques aux résultats enregistrés.
3. Les 690 classifications de l'audit sont recomputées depuis les checkpoints. Les 135 empreintes des scores répétés, le tirage des 15 dossiers, les coûts des ledgers et les intervalles bootstrap à 10 000 tirages sont vérifiés.
4. Les dix tests de calcul synthétique passent. Des recalculs indépendants confirment les comptes de FTE, coûts, configurations, seuils binomiaux et bornes de fiabilité. La version publiée du script reproduit les mêmes valeurs que le fichier local.
5. Les références internes se résolvent. Les vérifications externes ciblées utilisent des sources primaires ; ce contrôle ne prétend pas revalider intégralement les 64 entrées bibliographiques des deux textes.
6. Les 66 et 22 pages ainsi que les trois pages de notes sont inspectées ; les pages corrigées sont revues après recompilation. Aucun débordement ni référence indéfinie dans les PDF finaux. Un avertissement LaTeX de boîte insuffisamment remplie demeure dans le premier build, sans défaut visible.
7. Les deux ZIP minimaux sont extraits séparément puis compilés trois fois. Le texte extrait correspond exactement à celui des PDF finaux. Les paquets contiennent respectivement 44 et 17 fichiers.

Les rapports techniques et empreintes sont dans [paper/arxiv_verification.json](../paper/arxiv_verification.json), [paper2/arxiv_verification.json](../paper2/arxiv_verification.json) et [paper2/verification.json](../paper2/verification.json). Les données originales et leurs scores sont conservés.

## Accès et limites

Le scan de motifs de secrets a couvert les 30 commits accessibles au début de la revue, 4 297 blobs Git uniques, HEAD/index et les fichiers modifiés pertinents, y compris les contenus ZIP et XML des DOCX. Aucun motif ciblé n'a été détecté. Cela n'est pas une garantie exhaustive de confidentialité ; un passage public exposerait également l'historique et les métadonnées de provenance conservées dans les archives.

La vérification d'accès public a été effectuée sans authentification après le changement de visibilité. Elle résout le défaut d'accès constaté pendant la revue. Cette revue ne constitue ni une soumission arXiv, ni une décision de ses modérateurs, ni une validation indépendante des politiques métier du générateur.
