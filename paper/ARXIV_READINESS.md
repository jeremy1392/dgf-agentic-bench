# Préparation de *The Last Human Gate* pour arXiv

**Statut : préparation seulement. Aucune soumission arXiv effectuée.** Ce document distingue les règles publiées par arXiv des recommandations propres à ce manuscrit. Les références officielles ont été consultées le 24 septembre 2026.

**Point de diffusion à résoudre :** la revue complète a constaté que le dépôt GitHub est privé et que ses liens renvoient HTTP 404 sans authentification. Les fichiers sont présents sur GitHub, mais les PDF annonçant des sources publiques ne doivent pas être déposés tels quels avant ouverture de l'accès ou adaptation de cette déclaration. Le passage public attend une décision explicite de l'auteur. Voir le [rapport de revue](../docs/REVIEW_PAPERS_README_20260924.md).

**Vérifications locales terminées :** premier PDF de 66 pages, marges de 2,54 cm, 10 vérifications des calculs théoriques réussies, 48 clés bibliographiques sans référence manquante. Son ZIP final contient 44 dépendances (37 fichiers TeX et 7 figures). L'extraction dans un dossier vierge puis trois compilations PDFLaTeX produisent le même texte que le PDF publié, sans référence indéfinie ni débordement. Le rendu des 66 pages a été inspecté. [Rapport et empreintes](arxiv_verification.json). La compilation par les serveurs d'arXiv reste à effectuer lors du dépôt.

## Positionnement recommandé

Pour le premier manuscrit, **cs.CY — Computers and Society** paraît le choix principal le plus cohérent avec l'analyse de l'organisation, du travail humain et des conséquences de l'automatisation. **cs.AI** peut être proposé en classement secondaire si sa contribution sur les agents et le benchmark est suffisamment centrale. C'est une appréciation éditoriale, pas une décision d'arXiv ni un moyen de contourner la modération. Le deuxième manuscrit, centré sur DGF-Bench et ses mesures, correspond plus directement à cs.AI.

arXiv demande de limiter les classements secondaires aux communautés directement concernées ; les modérateurs peuvent modifier la classification. Voir les [règles de classement secondaire](https://info.arxiv.org/help/cross.html) et de [modération](https://info.arxiv.org/help/moderation/index.html).

Le **deuxième** manuscrit est désormais également préparé : 22 pages inspectées, marges de 2,54 cm et paquet minimal distinct de 17 fichiers (14 TeX et 3 figures). Sa compilation indépendante produit le même texte que son PDF final. [Rapport du deuxième manuscrit](../paper2/arxiv_verification.json). Le paquet minimal `DGF_Bench_arXiv_source.zip` convient à la compilation ; le paquet plus large `DGF_Bench_Second_Paper_Source.zip` conserve aussi la documentation et les protocoles.

L'auteur a communiqué un courriel confirmant son endorsement pour cs.AI. Son compte n'a pas été inspecté et sa couverture effective pour cs.CY n'a pas été vérifiée. Le formulaire de soumission précisera les conditions applicables. Un endorsement n'est ni une évaluation scientifique du texte ni une garantie de diffusion. Voir [l'endorsement](https://info.arxiv.org/help/endorsement.html).

## Règle concernant les articles de position

L'annonce officielle du 31 octobre 2025 indique que les articles de synthèse et de position en informatique doivent avoir été acceptés dans une revue ou conférence après une évaluation par les pairs, avec justificatif. Elle précise aussi que les articles scientifiques étudiant les effets des technologies sur la société, notamment en cs.CY, peuvent toujours être soumis sans cette évaluation préalable. Ce dernier point ne transforme pas toute opinion sur l'emploi en recherche originale.

Le manuscrit combine un modèle comptable, des propositions, des scénarios synthétiques, un benchmark et une thèse prospective. Ses résultats originaux doivent être identifiables, et les prévisions ne doivent pas être présentées comme des observations. Si les modérateurs le considèrent comme un article de position, l'exigence correspondante peut s'appliquer. Leur décision ne peut pas être prédite à partir du titre ou de l'endorsement. Voir [l'annonce officielle](https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/) et les [types de contenus](https://info.arxiv.org/help/policies/content-types.html).

Les règles consultées n'imposent pas une baseline humaine à chaque article de recherche original. L'absence de comparaison humaine reste une limite des conclusions possibles ; elle ne constitue pas, à elle seule, une interdiction générale de soumettre. Aucune étude humaine supplémentaire n'est ajoutée au programme par ce document.

## Articulation des deux manuscrits

Les deux textes utilisent les mêmes 899 runs initiaux du benchmark. Le premier porte principalement la contribution théorique et la comptabilité du travail ; le second approfondit l'évaluation empirique avec le contrôle déterministe, les répétitions et les audits. Décrire et citer ce partage explicitement ; ne pas présenter les deux publications comme deux réplications indépendantes.

Le partage de données n'est pas présenté par arXiv comme une interdiction automatique. En revanche, lorsque plusieurs soumissions sont trop similaires ou ressemblent à des révisions d'un même travail, arXiv peut demander leur regroupement ou leur versionnement. Voir [la politique sur les contenus dupliqués](https://info.arxiv.org/help/moderation/index.html#duplicated-content).

## Fichiers et mise en page

Les [exigences de format](https://info.arxiv.org/help/policies/format_requirements.html) demandent notamment un titre et une attribution, des références complètes, un texte exploitable automatiquement, une taille de police de 10 à 14 points et des marges d'au moins **1 pouce, soit 2,54 cm**. Il faut vérifier la version finale compilée après correction des marges. Aucun plafond général de 59 pages n'a été trouvé dans les règles consultées ; la longueur doit néanmoins servir la contribution.

Un article produit avec LaTeX doit être déposé avec ses sources, plutôt qu'avec son PDF seul. Le paquet minimal prévu contient `main.tex` à sa racine, les sections et fragments de tableaux réellement utilisés et les figures nécessaires. La bibliographie est intégrée dans `sections/91_references.tex` : aucun traitement BibTeX séparé n'est requis. Voir les [formats de soumission](https://info.arxiv.org/help/submit/index.html#formats-for-text-of-submission).

Les données expérimentales et scripts de reproduction restent dans le dépôt et ses releases ; ils ne sont pas nécessaires à la compilation de ce paquet minimal. Le texte doit les désigner comme ressources externes accessibles, sans promettre leur présence dans l'archive LaTeX. Les manifestes, checksums, notes de préparation, anciens builds et notices de licence du dépôt ne sont pas injectés dans le texte de l'article.

## Préparation du paquet final

Le script `research/2026-09-followup/package_first_paper_arxiv.py` suit les dépendances LaTeX, contrôle la casse des chemins, recherche les secrets selon le scanner de publication, vérifie le ZIP et produit des empreintes séparées. Il exige un PDF final explicitement fourni et ne compile ni ne soumet le manuscrit.

Après compilation et vérification du PDF final, depuis la racine du dépôt :

```powershell
.venv/Scripts/python.exe research/2026-09-followup/package_first_paper_arxiv.py --pdf paper/The_Last_Human_Gate.pdf
```

Les fichiers seront placés dans `experiments/publication_20260924_first_paper/`. Le manifeste `first_paper_arxiv_manifest.json` et `first-paper-SHA256SUMS.txt` seront également conservés dans `research/2026-09-followup/`. Une extraction dans un dossier vide suivie d'une compilation indépendante doit vérifier que l'archive suffit réellement à produire l'article. Le PDF rendu doit être relu avant dépôt.

Pour le deuxième manuscrit, le même script prend `--manuscript second --pdf paper2/From_Governance_Reviews_to_Task_Substitution.pdf` et écrit son paquet dans `experiments/publication_20260924_second_paper/`. Les deux paquets ne contiennent pas les données expérimentales, accessibles séparément dans la release. Vérifier l'accès à ces liens sans authentification avant toute soumission qui annonce des données publiques.

Le choix de la licence de dépôt appartient à l'auteur. Cette préparation ne choisit ni ne modifie la licence du manuscrit. arXiv exige un accord de distribution ; consulter ses [options de licence](https://info.arxiv.org/help/license/index.html) avant de valider le formulaire. La sélection d'une licence et le dépôt effectif n'ont pas été effectués ici.
