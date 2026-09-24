# Dépôt arXiv du deuxième paper

Préparation du 24 septembre 2026. **Archive préparée et contrôlée localement ; aucune soumission effectuée.** Le titre actuel est **DGF-Bench: Rule Application and Evidence Reliability in Synthetic Governance Reviews**. Le nom historique du PDF, `From_Governance_Reviews_to_Task_Substitution.pdf`, est conservé pour les liens existants.

## Fichier à téléverser

Utiliser **[DGF_Bench_arXiv_source.zip](https://github.com/jeremy1392/dgf-agentic-bench/releases/download/dgf-bench-300-20260923/DGF_Bench_arXiv_source.zip)**. La copie locale se trouve dans `experiments/publication_20260924_second_paper/` à la racine du dépôt.

Cette archive contient 17 fichiers nécessaires à la compilation : 14 fichiers TeX et 3 figures. `main.tex` est à sa racine. Choisir **PDFLaTeX** ; la bibliographie est intégrée, sans étape BibTeX. Le PDF de contrôle comporte 22 pages. Les données et traces complètes restent accessibles dans la [release expérimentale](https://github.com/jeremy1392/dgf-agentic-bench/releases/tag/dgf-bench-300-20260923).

arXiv demande les sources pour un article produit avec LaTeX : téléverser ce ZIP, pas seulement le PDF ni l'archive plus large de documentation. Voir les [instructions de soumission](https://info.arxiv.org/help/submit/index.html).

## Point éditorial restant avant validation

À la demande de l'auteur, la déclaration d'aide à la rédaction a été retirée du deuxième manuscrit. **arXiv demande néanmoins de signaler dans le travail tout usage significatif d'IA générative.** L'assistance apportée à la rédaction et aux révisions dans ce projet relève de ce point. Cette fiche extérieure au manuscrit ne remplace pas une déclaration dans l'article. Le paquet passe les contrôles techniques ; il n'est pas présenté comme entièrement conforme à cette exigence éditoriale. Voir la [politique officielle](https://info.arxiv.org/help/moderation/index.html#policy-for-authors-use-of-generative-ai-language-tools).

Pour résoudre ce point avant le dépôt, une formulation courte et factuelle pourrait être réintroduite dans l'article : « Generative AI tools assisted manuscript preparation and revision; the author takes responsibility for the content. » Elle n'est pas intégrée au ZIP actuel. Si le texte est modifié, recompiler et régénérer l'archive avant de la téléverser.

## Métadonnées à copier

Le fichier [arxiv_metadata.txt](arxiv_metadata.txt) contient le titre, l'auteur, le résumé anglais et les commentaires. Son résumé reprend celui du PDF en texte ASCII, sans modification scientifique, et respecte la limite officielle de 1 920 caractères. Voir les [règles des métadonnées](https://info.arxiv.org/help/prep.html).

- Catégorie principale recommandée : **cs.AI — Artificial Intelligence**. C'est une recommandation de positionnement ; arXiv décide de la classification.
- Auteur : **Jeremy Canale**. Aucune affiliation institutionnelle n'est ajoutée.
- Laisser `Journal-ref`, `DOI` et `Report-no` vides en l'absence d'information réelle correspondante.
- Choisir personnellement la licence dans le formulaire. Aucune licence de dépôt n'a été sélectionnée ici ; consulter les [options proposées par arXiv](https://info.arxiv.org/help/license/index.html).

Après résolution du point éditorial : ouvrir le [formulaire arXiv](https://arxiv.org/submit/), renseigner les métadonnées, téléverser le ZIP, sélectionner `main.tex` et PDFLaTeX si demandé, puis inspecter le PDF compilé par arXiv. Vérifier les 22 pages, les trois figures, les tableaux, les références et les coordonnées avant la validation finale. La compilation locale ne remplace pas cette prévisualisation serveur.

## Articulation avec le premier article

| Manuscrit | Contribution principale | Données |
| --- | --- | --- |
| *The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance* | Contrats de décision, rôle des FDE, comptabilité du travail et scénarios d'effectifs | Benchmark initial et suivi communs |
| *DGF-Bench: Rule Application and Evidence Reliability in Synthetic Governance Reviews* | Méthode du benchmark, contrôle déterministe, diagnostics des preuves et des décisions, répétitions | Les mêmes dossiers, traces et résultats |

Les deux versions actuelles rapportent déjà le benchmark initial et les suivis. Les 135 répétitions ne sont donc pas une expérience exclusive au deuxième article. Celui-ci approfondit leur analyse. Ce partage est explicité dans le manuscrit ; il ne faut pas présenter les deux articles comme des réplications indépendantes. arXiv peut demander de regrouper ou de versionner des soumissions trop similaires. Voir la [politique sur les contenus dupliqués](https://info.arxiv.org/help/moderation/index.html#duplicated-content).

Formulation anglaise utilisable pour expliquer leur relation :

> This manuscript and The Last Human Gate: Forward Deployed Engineering and the Automation of Enterprise Governance share the September 2026 DGF-Bench experiment and follow-up records. The present paper develops the benchmark methodology, evidence diagnostics, deterministic control, and repeated-execution analysis. The companion develops the gate-as-contract framework, FDE implementation argument, and workforce accounting and scenarios. These are complementary analyses of shared data, not independent replications.

## Résumé accessible en français

L'expérience demande à trois modèles de jouer le rôle de relecteurs de projets : consulter un dossier fictif, appliquer les règles d'une étape de validation, décider et fournir les preuves de leur décision. Les 300 projets donnent 899 exécutions exploitables et 5 094 étapes évaluées. Le succès strict par étape atteint 94,98 % pour Gemini, 83,29 % pour Luna et 74,18 % pour DeepSeek. Une chaîne entière réussit moins souvent, puisqu'une seule étape ratée suffit à la faire échouer.

Un programme déterministe réussit les 1 700 étapes du même contrat à partir des règles et des faits structurés fournis. L'étude montre donc une capacité des modèles à exécuter ces tâches, sans démontrer qu'un LLM apporte un avantage sur ce programme dans cette configuration. L'audit distingue les défauts de format des preuves et les autres erreurs ; les 135 répétitions montrent aussi que la réussite n'est pas stable pour tous les dossiers. Le coût enregistré total est de 99,58 USD. L'expérience ne mesure ni les heures économisées dans une entreprise ni la réduction de ses effectifs.

## Contrôles et reproduction technique

Le [rapport de vérification](arxiv_verification.json) et le [manifeste avec empreintes](../research/2026-09-followup/second_paper_arxiv_manifest.json) identifient les fichiers livrés. L'archive est vérifiée après extraction et compilation dans un dossier vierge. Aucun nouvel appel de modèle n'est nécessaire.

Après toute modification, recompiler le PDF depuis `paper2/`, le contrôler visuellement, puis actualiser sa copie publiée. Depuis la racine du dépôt, régénérer ensuite le paquet :

```powershell
.venv/Scripts/python.exe research/2026-09-followup/package_first_paper_arxiv.py --manuscript second --pdf paper2/From_Governance_Reviews_to_Task_Substitution.pdf
```

Ce script prépare les sources ; il ne soumet rien et ne vérifie pas à lui seul la conformité éditoriale.
