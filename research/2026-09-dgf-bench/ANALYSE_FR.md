# Analyse finale des 300 dossiers — 23 septembre 2026

Analyse hors ligne de `experiments/run_20260922_214402_941347/results`, après la reprise terminée le 23 septembre à 12:07 UTC (16:07 à Dubaï). Aucun appel payant, aucune modification des réponses, du dataset ou du barème. Cette analyse remplace les conclusions de disponibilité du rapport partiel du même jour, qui reste un document historique.

## Conclusion

**Gemini est le meilleur sur le protocole testé ; Luna obtient un meilleur compromis coût/score strict que DeepSeek.** L'expérience est presque complète : **899 exécutions évaluables sur 900**, sur les trois routes. Une erreur fournisseur Gemini reste exclue. Les 299 dossiers communs permettent une comparaison appariée substantielle.

Le résultat central est la différence entre **choisir la bonne décision** et **produire un dossier de décision entièrement conforme**. Gemini choisit toutes les décisions attendues dans ses 1 694 gates évaluables, mais échoue à la conformité des preuves dans 85 d'entre elles. Ses 95,0 % de gates strictement réussies deviennent 76,9 % de projets dont toutes les gates réussissent.

Ces résultats portent sur l'application de règles explicites à des dossiers synthétiques, avec des faits structurés accessibles. Ils ne démontrent pas une compétence générale d'expert sur des dossiers réels, une capacité à réaliser les corrections, ou une diminution mesurée des FTE.

## 1. Complétude et intégrité

- Dataset : 300 projets, 100 Buy, 100 Integrate, 100 Build ; chaque modèle reçoit les mêmes dossiers.
- DeepSeek et Luna : 300/300 dossiers ; Gemini : 299/300 (100 Buy, 99 Integrate, 100 Build).
- Gates évaluables : 5 094 sur 5 100 prévues. Toutes les gates des 899 dossiers évaluables ont été tentées.
- Version unique : `DGF-decision-v8.2-authorized-review` ; température 0, mode de transmission `agent`, vision `auto`, 8 192 tokens de sortie, maximum 20 tours et 40 appels d'outil.
- Empreintes des sources et du dataset actuel identiques à `protocol_identity.json`. L'empreinte du dataset a été calculée dans l'ordre du manifeste, comme le runner.
- Totaux de gates, succès stricts et indicateurs de réussite de route cohérents dans les 899 scores.
- Recalcul hors ligne de cinq dossiers ciblés : reproduction exacte des scores de gate enregistrés (les quatre dossiers contenant les critical misses, plus un échec de preuve Gemini). Ce contrôle est ciblé, pas une réévaluation indépendante des règles métier.
- Aucun désaccord d'identifiant de modèle ni coût inconnu enregistré. Aucun dossier classé `AGENT_FAILURE` ; cela ne signifie pas que toutes les réponses sont substantielles ou correctes.
- Coût des registres de consommation : **87,015829172 USD**, cohérent avec le compteur global. La dernière reprise utilisait un plafond de 110 USD, 12 workers et 4 workers par modèle. Les 4 723,858 secondes des dernières statistiques décrivent cette reprise seulement, pas la durée cumulée de l'étude.

Les anciens fichiers `paper_outputs/` datent du 22 septembre et décrivent seulement 78 dossiers évaluables. **Ne pas les utiliser pour le paper final.** Les exports recalculés sont dans [analysis_20260923_final]().

## 2. Résultats principaux

| Modèle | Dossiers évaluables | Gates strictement correctes | IC 95 % du CSR | Toutes les gates du dossier correctes | Décisions correctes seules | Coût connu |
|---|---:|---:|---:|---:|---:|---:|
| DeepSeek v4.1 Flash | 300 | 1 261 / 1 700 = **74,18 %** | 71,88–76,47 % | 74 / 300 = **24,67 %** | 1 619 / 1 700 = 95,24 % | 10,09 USD |
| Gemini 3.8 Flash | 299 | 1 609 / 1 694 = **94,98 %** | 93,86–96,04 % | 230 / 299 = **76,92 %** | 1 694 / 1 694 = 100,00 % | 71,88 USD |
| GPT-5.6 Luna | 300 | 1 416 / 1 700 = **83,29 %** | 81,29–85,24 % | 127 / 300 = **42,33 %** | 1 668 / 1 700 = 98,12 % | 5,05 USD |

CSR : décision, findings, actions proposées, preuves et autorisation doivent tous être corrects. La réussite de route utilise ce même critère strict à chaque gate ; ce n'est pas une mesure de remédiation exécutée. Les moyennes pondérées de score (95,02 %, 99,68 %, 97,67 %) ne doivent pas être présentées comme des taux de réussite complète.

Les intervalles du CSR rééchantillonnent les dossiers entiers à l'intérieur des routes (2 000 tirages, graine 81931). Les intervalles de réussite de route sont des intervalles de Wilson : DeepSeek 20,13–29,84 %, Gemini 71,82–81,34 %, Luna 36,87–47,99 %. Ce sont des incertitudes descriptives pour cette population synthétique, sans correction des biais de génération ou du protocole.

### Comparaison sur les mêmes 299 dossiers

Sur 1 694 gates par modèle : DeepSeek 74,09 %, Gemini 94,98 %, Luna 83,23 %. Le classement reste identique après exclusion du dossier manquant chez Gemini.

| Différence appariée de CSR | Écart en points | IC 95 % en points |
|---|---:|---:|
| Gemini − DeepSeek | +20,90 | +18,30 à +23,44 |
| Gemini − Luna | +11,75 | +9,62 à +13,93 |
| Luna − DeepSeek | +9,15 | +6,67 à +11,63 |

Méthode : 10 000 tirages bootstrap appariés par dossier, stratifiés Buy/Integrate/Build, graine NumPy 81931. Un dossier rééchantillonné apporte toutes ses gates et les résultats des trois modèles ensemble. Les écarts observés dépassent l'incertitude d'échantillonnage estimée dans ce cadre ; ils ne permettent pas un classement universel des modèles.

## 3. Différences entre routes et gates

| Route | DeepSeek : CSR / routes réussies | Gemini : CSR / routes réussies | Luna : CSR / routes réussies |
|---|---:|---:|---:|
| Buy | 67,83 % / 13 sur 100 | 97,67 % / 87 sur 100 | 74,67 % / 20 sur 100 |
| Integrate | 78,17 % / 32 sur 100 | 95,12 % / 75 sur 99 | 87,67 % / 52 sur 100 |
| Build | 77,00 % / 29 sur 100 | 91,60 % / 68 sur 100 | 88,40 % / 55 sur 100 |

| Gate | DeepSeek CSR | Gemini CSR | Luna CSR |
|---|---:|---:|---:|
| Architecture | 75,00 % | 85,43 % | 89,50 % |
| Compliance | 88,00 % | 100,00 % | 96,00 % |
| General | 68,67 % | 87,96 % | 61,67 % |
| IT | 87,00 % | 100,00 % | 97,67 % |
| Legal | 68,50 % | 99,50 % | 80,50 % |
| Procurement | 43,00 % | 96,00 % | 33,00 % |
| Security | 72,33 % | 98,66 % | 92,00 % |
| Tech Readiness | 71,00 % | 89,00 % | 97,00 % |

Luna dépasse Gemini en CSR sur Architecture et Tech Readiness, mais ces différences locales ne constituent pas une démonstration de supériorité dans ces spécialités. Les règles, dossiers et exigences de preuve diffèrent entre gates. Procurement et General sont les principaux points faibles de Luna ; Procurement pénalise aussi DeepSeek.

## 4. Pourquoi le CSR échoue

Les causes ci-dessous peuvent se cumuler.

| Modèle | Gates en échec | Preuve imparfaite | Mauvaise décision | Findings imparfaits | Actions imparfaites | Autorisation incorrecte | Preuve comme seule cause |
|---|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek | 439 | 354 | 81 | 73 | 73 | 34 | 338 (77,0 %) |
| Gemini | 85 | 85 | 0 | 0 | 0 | 0 | 85 (100 %) |
| Luna | 284 | 251 | 32 | 37 | 37 | 34 | 221 (77,8 %) |

Le contrôle des preuves exige des références effectivement lues et des extraits exacts contenant les champs/valeurs observés attendus. Les diagnostics regroupent les extraits manquants ou invalides et les références absentes ou non observées. **Il serait excessif de qualifier tous ces échecs de simples fautes de format**, ou de conclure qu'ils correspondent tous à une mauvaise compréhension métier.

Pour Gemini, les 85 échecs sont concentrés notamment sur General (36), Architecture (29) et Tech Readiness (11). Le détail vérifié sur `DGF-BLD-035201_build` montre la bonne décision et les bons findings/actions, avec un extrait non conforme pour `ARCH-API-001`.

La règle de preuve doit rester celle annoncée pour ce run. Une évaluation sémantique alternative peut être ajoutée dans une analyse secondaire explicitement distincte ; elle ne doit pas remplacer après coup le score principal.

## 5. Erreurs critiques et approbations incorrectes

- **DeepSeek : 1 critical miss et 1 false approval**, sur la même gate Architecture du dossier `DGF-INT-035136_integrate`. Un chevauchement d'adressage (`ARCH-IP-001`) exigeait `NO_GO` ; la réponse soumise est `GO`, sans findings ni preuve, avec une justification « placeholder » et confiance 0. Le trace montre une soumission produite par le modèle lors de la finalisation forcée au dernier tour. Le harness l'accepte syntaxiquement et le score la pénalise. Ce cas mesure aussi la capacité à terminer correctement dans la limite de tours, pas seulement le raisonnement sur les réseaux.
- **Luna : 3 critical misses et 1 false approval.** Sur `DGF-INT-035197_integrate`, la gate Legal soumet `GO` alors que le DPA manquant exige `REWORK` (`LEGAL-DPA-001`). Sa justification reconnaît elle-même que `REWORK` est correct : le verdict structuré contredit le texte. Sur `DGF-INT-035105_integrate`, le finding de sécurité `SEC-NET-001` manque. Sur `DGF-INT-035158_integrate`, le finding final `GEN-UPSTREAM-NOGO` manque ; cette erreur de consolidation peut inclure la propagation d'une décision amont incorrecte et ne doit pas être interprétée automatiquement comme une erreur indépendante supplémentaire.
- **Gemini : aucun critical miss ni false approval observé** sur les dossiers évaluables. Cette absence observée ne prouve pas un risque nul hors de cet échantillon.

Le référentiel tient compte des approbations conditionnelles réellement autorisées : les nombres de dispositions de référence effectives peuvent donc différer entre modèles. Utilisations enregistrées d'approbation conditionnelle : DeepSeek 202, Gemini 398, Luna 353. Il ne faut pas comparer les seules fréquences d'approbation comme si toutes les références étaient immuables et identiques.

## 6. Échec restant, reprises et coûts

Le seul dossier non évaluable est Gemini / `DGF-INT-035128_integrate`, dès `INTEGRATE-01-IT-1` : `Provider returned finish_reason=error`. Le score final conserve plusieurs réponses fournisseur en erreur. C'est une exclusion d'infrastructure, pas une décision incorrecte. Les anciennes erreurs 403 archivées dans les traces appartiennent aux tentatives antérieures ; il ne faut pas les recompter comme autant de dossiers actuellement manquants.

Deux possibilités scientifiquement défendables : conserver et déclarer cette exclusion (299 dossiers appariés), ou tenter une reprise ciblée documentée de ce dossier. **Il n'est pas nécessaire de relancer les 899 dossiers terminés.** Aucune reprise n'a été exécutée dans cette analyse.

Le coût total connu est 87,02 USD. En ordre de grandeur, cela représente 0,034 USD par dossier pour DeepSeek, 0,017 pour Luna et 0,240 pour Gemini. Le total Gemini inclut le dossier en erreur ; les coûts incluent les réponses enregistrées au fil des reprises. Gemini coûte environ 14,2 fois le total Luna, pour presque le même nombre de dossiers, et représente environ 82,6 % de la dépense.

Les scores signalent 2 réponses tronquées chez DeepSeek, 14 chez Gemini, aucune chez Luna. Une réponse tronquée ne signifie pas nécessairement un dossier final incomplet. Le routage fournisseur DeepSeek implique plusieurs hébergeurs ; Gemini est enregistré via Google AI Studio et Luna via OpenAI. Ces mesures caractérisent donc aussi les conditions d'exécution OpenRouter observées.

## 7. Diversité et portée scientifique

Le rapport de diversité du dataset indique 300 identifiants de projet distincts, 300 signatures d'architecture distinctes et 300 signatures globales des faits décisionnels. Il existe **267 combinaisons globales distinctes de findings**, donc pas 300 scénarios décisionnels entièrement uniques.

Toutes les règles applicables aux phases sélectionnées sont couvertes selon cet audit. L'entropie des décisions, normalisée et ajustée aux phases, va de 0,9971 à 1,0000. La couverture des décisions est donc très équilibrée par construction. Les faits pertinents ne sont pas tous uniques à chaque gate : 142 signatures pour 200 dossiers Compliance, 241 pour 300 Security, 285 pour 300 IT. Cela n'annule pas l'étude, mais interdit d'assimiler le nombre de noms ou de schémas distincts au nombre de problèmes indépendants.

Surtout, le protocole expose une politique décisionnelle explicite et des instantanés structurés `REVIEW_FACTS_*`. L'évaluateur utilise des règles issues du même système. Le benchmark mesure la capacité des agents à consulter les faits, appliquer ces règles, exercer les actions autorisées et produire un résultat traçable. Il ne mesure pas, à lui seul, la découverte de règles tacites ou l'extraction autonome de tous les faits à partir des seuls documents et images. Le mode vision disponible n'établit pas que les images ont été nécessaires à la réussite.

## 8. Ce que l'on peut écrire dans le paper

> Dans une évaluation synthétique portant sur 300 dossiers répartis entre trois routes de gouvernance, trois modèles ont produit 899 exécutions évaluables sur 900 prévues. Les taux de réussite stricte par gate étaient de 94,98 % pour Gemini, 83,29 % pour Luna et 74,18 % pour DeepSeek. Les taux de réussite de toutes les gates d'un dossier étaient respectivement de 76,92 %, 42,33 % et 24,67 %. Le classement était conservé sur les 299 dossiers communs. Les écarts entre conformité de la décision et conformité complète étaient largement associés aux exigences de preuve. Ces résultats concernent l'application de politiques explicites à des cas synthétiques et ne constituent pas une mesure d'automatisation opérationnelle ou de réduction des effectifs.

Avant soumission : intégrer les nouveaux exports plutôt que les rapports partiels, documenter les reprises et l'exclusion, figer le code exact et les données utiles à la reproduction, et séparer les résultats empiriques de l'hypothèse FTE 2033. Une validation indépendante des règles et une future comparaison avec experts humains ou dossiers réels renforceraient la validité externe.

## Fichiers de cette analyse

- [Graphique comparatif](results_overview.png) — [version SVG](results_overview.svg) / [version PDF](results_overview.pdf)
- [Tableaux recalculés et intervalles](PAPER_RESULTS.md)
- [Données agrégées](aggregate.json)
- [Diagnostics et résultats par route](diagnostics.json)
- [Différences appariées et intervalles](paired_comparisons.json)
- [Statistiques de la dernière reprise](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923)
- [Audit de diversité préexistant](dataset_diversity_report.json)
