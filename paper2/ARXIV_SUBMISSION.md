# Dépôt arXiv de la version courte de The Last Human Gate

**Nouvelle version du 24 septembre 2026 : 28 pages, 5 figures, 14 références.** Elle remplace l'ancien deuxième paper. Aucune soumission arXiv n'a été effectuée ici.

## Fichiers et métadonnées

Téléverser le **[ZIP source actualisé](https://github.com/jeremy1392/dgf-agentic-bench/releases/download/dgf-bench-300-20260923/DGF_Bench_arXiv_source.zip)**. La copie locale est dans `experiments/publication_20260924_second_paper/`. Le nom de l'archive et celui du PDF restent stables, mais leur contenu est entièrement actualisé. **Remplacer les fichiers déjà téléversés et les anciennes métadonnées dans le brouillon arXiv.**

Le titre à saisir est **The Last Human Gate: Forward Deployed Engineering for Governance Automation**. L'auteur est **Jeremy Canale**. Le fichier [arxiv_metadata.txt](arxiv_metadata.txt) fournit le résumé anglais du PDF en ASCII et le champ Comments. Laisser Journal-ref, DOI et Report-no vides tant qu'ils n'existent pas.

Le ZIP contient 19 dépendances : 16 fichiers TeX, deux figures PDF et une figure PNG. Deux autres figures, dont le schéma des trois parcours DGF en page 2, sont produites par TikZ dans les sources. Choisir `main.tex` et **PDFLaTeX**. La bibliographie est intégrée, sans BibTeX. arXiv demande les sources pour un article produit avec LaTeX ; ne déposer ni seulement le PDF ni l'archive élargie de documentation. [Instructions officielles](https://info.arxiv.org/help/submit/index.html).

## Positionnement et relation avec la version longue

La version courte est désormais le manuscrit principal recommandé pour la lecture et le dépôt. La version de 66 pages reste une présentation étendue de la même recherche. Les données et résultats se recouvrent largement : ne pas déposer les deux comme deux expériences indépendantes. arXiv peut demander de regrouper ou de versionner des soumissions trop similaires. [Politique sur les contenus dupliqués](https://info.arxiv.org/help/moderation/index.html#duplicated-content).

**cs.AI** est la catégorie principale proposée pour les contrats d'agents, les méthodes et le benchmark ; **cs.CY** est un classement secondaire envisageable pour la substitution du travail. C'est une recommandation, soumise à la décision d'arXiv. Le manuscrit contient des définitions, démonstrations, méthodes et résultats originaux ; le fait de le présenter ainsi ne préjuge pas de sa classification par les modérateurs. Les règles particulières applicables aux articles de position en informatique restent à connaître. [Annonce officielle](https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/).

Le choix de la licence revient à l'auteur. Cette préparation n'en sélectionne aucune. Consulter les [options arXiv](https://info.arxiv.org/help/license/index.html).

## Vérification du dépôt

Vérifier les [conditions de soumission et de modération](https://info.arxiv.org/help/moderation/index.html), puis utiliser le [formulaire arXiv](https://arxiv.org/submit/), importer les sources actuelles, renseigner les métadonnées et inspecter l'aperçu produit par arXiv. Contrôler le titre, les 28 pages, les cinq figures, les tableaux des résultats, les équations et les références. Les vérifications locales portent sur la compilation et l'intégrité des fichiers ; elles ne constituent pas une validation éditoriale par arXiv.

Le [rapport technique](arxiv_verification.json) et les [empreintes des fichiers](../research/2026-09-followup/second-paper-arxiv-SHA256SUMS.txt) identifient les livrables. Après une modification, compiler et vérifier le PDF, actualiser sa copie publiée puis régénérer le paquet depuis la racine :

```powershell
.venv/Scripts/python.exe research/2026-09-followup/package_first_paper_arxiv.py --manuscript second --pdf paper2/From_Governance_Reviews_to_Task_Substitution.pdf
```

Cette préparation ne garantit ni acceptation, ni audience, ni reconnaissance de l'importance de la contribution.
