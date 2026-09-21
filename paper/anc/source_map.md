# Source map

This file lists every external reference, how the manuscript uses it, the locator cited, and the
actual verification status. It distinguishes three states:

- **Checked online** – bibliographic details or content confirmed against a publisher, NBER, arXiv or
  ACL Anthology page during the review of 19–20 September 2026.
- **Known, not re-checked** – a well-known reference whose details were not re-verified online in
  that review.
- **Author to check** – a page- or section-level locator that must be confirmed against the document
  itself before submission.

Responsibility for every reference rests with the author.

## Closest economic models

| Reference | Use in the manuscript | Locator | Status |
|---|---|---|---|
| Gans & Goldfarb (2026), *O-Ring Automation*, NBER WP 34639 | Task qualities are complements; automating one task changes the return to automating others | abstract | Checked online (WP number, date, abstract) |
| Demirer, Horton, Immorlica, Lucier & Shahidi (2026), *Chaining Tasks, Redefining Work*, NBER WP 34859 | Ordered steps executed manually, with AI, or automated in chains; job boundaries and handoff costs; a step is more likely to be AI-executed when its neighbors are | abstract; Section 7 (Empirical Evaluation) | Checked online: WP number, abstract, Section 7 data sources (O*NET 27.3, Eloundou et al. exposure labels, Anthropic Economic Index, GPT-generated task ordering) and the neighbor prediction. Subsection numbers within Section 7 were not confirmed, so the manuscript cites Section 7 only |
| Ide & Talamàs (2025), *JPE* 133(12):3762–3800 | AI in knowledge hierarchies; autonomous vs. non-autonomous AI | abstract | Checked online (journal, volume, pages, abstract) |
| Shahidi, Rusak, Manning, Fradkin & Horton (2025), NBER WP 34468 | External channel: agents lower search, communication and contracting costs while adding market frictions | abstract | Checked online (WP number, abstract) |

## Organizational foundations

| Reference | Use | Locator | Status |
|---|---|---|---|
| Cooper (1990), *Business Horizons* 33(3):44–54 | Stages contain work; gates evaluate deliverables and decide go/hold/kill/recycle | p. 46 | Known, not re-checked. **Author to check p. 46** |
| Nigam & Caswell (2003), *IBM Systems Journal* 42(3):428–445 | Business artifacts as the unit of operational specification | whole article | Known, not re-checked |
| Garicano (2000), *JPE* 108(5):874–904 | Knowledge hierarchies; specialists handle exceptions | whole article | Checked online (journal, volume, pages) |
| Garicano & Rossi-Hansberg (2015), *Annual Review of Economics* 7:1–30 | Routine problems near production, exceptions to specialists, communication cost | Sections 1 and 3 | Known, not re-checked. **Author to check the section numbers** |
| Bainbridge (1983), *Automatica* 19(6):775–779 | Supervision, skill retention and recovery problems created by automation | pp. 775–777 | Known, not re-checked. **Author to check the page range** |
| Vu et al. (2025), arXiv:2504.03693v1 | Agentic BPM: history and practitioner perspectives | v1 | Known, not re-checked. Version 1 is cited on purpose; later versions carry a different title |
| Calvanese et al. (2026), *Information Systems* 140:102738 | Agentic BPM manifesto: process frames, autonomy, explanation, interaction, adaptation | abstract | Checked online (journal, volume, article number) |

## Economics of the firm and task-based economics

| Reference | Use | Locator | Status |
|---|---|---|---|
| Coase (1937), *Economica* 4(16):386–405 | Market versus firm coordination of transactions | pp. 389–394 | Known, not re-checked. **Author to check the page range** |
| Autor (2015), *JEP* 29(3):3–30 | Substitution coexists with complementarities and new demand | whole article | Known, not re-checked |
| Acemoglu & Restrepo (2019), *JEP* 33(2):3–30 | Displacement and reinstatement of labor | whole article | Known, not re-checked |
| Eloundou et al. (2024), *Science* 384(6702):1306–1308 | Exposure estimates concern potential task effects | whole article | Checked online (journal, volume, pages) |
| Brynjolfsson, Li & Raymond (2025), *QJE* 140(2):889–942 | Heterogeneous productivity effects of AI assistance | whole article | Known, not re-checked |

## Strategic behavior and accountability

| Reference | Use | Locator | Status |
|---|---|---|---|
| Holmström & Milgrom (1991), *JLEO* 7:24–52 | Multitask incentives: effort shifts toward rewarded activities | whole article | Known, not re-checked |
| Kleinberg & Raghavan (2019), EC '19, pp. 825–844 | Improvement versus gaming under a decision rule | whole article | Known, not re-checked (page range not confirmed) |
| Hardt, Megiddo, Papadimitriou & Wootters (2016), ITCS '16, pp. 111–122 | Strategic classification | whole article | Known, not re-checked |
| Novelli, Taddeo & Floridi (2024), *AI & Society* 39:1871–1882 | Accountability as answerability within an institutional arrangement | whole article | Known, not re-checked |

## Agent evaluations (motivation only; none supplies a model parameter)

| Reference | Use | Locator | Status |
|---|---|---|---|
| Drouin et al. (2024), WorkArena, ICML, PMLR 235:11642–11662 | Enterprise web tasks | whole paper | Known, not re-checked |
| Jha et al. (2025), ITBench, ICML, PMLR 267:27134–27197 | SRE, compliance and FinOps scenarios | whole paper | Known, not re-checked (page range not confirmed) |
| Kwa et al. (2025), arXiv:2503.14499v4 | Long software-task completion horizons | v4 | Checked online: v4 dated 10 July 2026 exists; recent versions are titled "...Long Software Tasks" |
| Fu et al. (2026), CI-Work, ACL 2026 Industry Track | Contextual integrity in enterprise agent workflows | whole paper | Checked online (venue, Anthology ID 2026.acl-industry.103); page range not confirmed |
| van der Aalst (2016), *Process Mining*, 2nd ed. | Event data reconstruct routes and visits, not unlogged effort | whole book | Known, not re-checked |

## Other factual statements

| Statement | Status |
|---|---|
| Azure AI Foundry was renamed Microsoft Foundry (announced November 2025) | Checked online |
| All page locators to Canale (2026) | Author's own document; reproduced in `dgf_source_excerpt.pdf` |

## References added for the thesis argument

| Reference | Use | Status |
|---|---|---|
| Kwa et al. (2025), NeurIPS 2025 Main Conference Track; arXiv:2503.14499v4 (10 July 2026) | Seven-month doubling of the 50% horizon; similar trend for the 80% horizon at roughly one fifth of the length | Checked online (venue, version, both statements) |
| METR (2026a), time-horizons dashboard, update of 8 May 2026 | Best model: 50% horizon of at least 16 hours (95% interval 8.5–55 h), 80% horizon of about 3 hours; measurements above 16 hours unreliable; domain variation | Checked online through the dashboard and secondary reports |
| METR (2026b), Time Horizon 1.1, 29 January 2026 | 196-day (seven-month) doubling; task-suite changes affect fitted levels | Checked online (doubling time); the METR limitations note of 22 January 2026 gives error bars of roughly a factor of two |
| Microsoft (2026), What is Microsoft Foundry? | Azure AI Foundry is now Microsoft Foundry | Checked online |
| SonarSource, Microsoft Azure Policy, Atlassian, AWS (two pages), Oracle, DTCC, Fannie Mae | Operational precedents in the precedents table | **Author to check**: URLs and the described mechanism were not opened during the review |
| Debenedetti et al. (2024), AgentDojo, arXiv:2406.13352 | Prompt injection through tool-returned data | Known, not re-checked (version number not confirmed) |
| GDPR Art. 22; NIS2 Art. 20; DORA Arts. 5 and 6(10); AI Act Arts. 6, 14 and Annex III | Legal limits of delegation | Known, not re-checked; requires legal review for any deployment |
| Demirer et al. (2026), Section 7 | Neighbor effect on AI execution | Section 7 and its data sources checked online; subsection numbering not confirmed |

## References added for the forward-deployed-engineer section

| Reference | Use | Status |
|---|---|---|
| Illinois Institute of Technology (2026), blog on the forward deployed engineer | Definition and origin of the role | Found online (title, date, definition); **author to open the page** |
| Allianz (2025), media-center article on Project Nemo | Seven agents, low-value food-spoilage claims in Australia, about 80% shorter processing, human final payout decision | Checked online (primary source and trade press) |
| Insurance Journal (2025); Reinsurance News (2026) | AIG agentic underwriting with Palantir and Anthropic; review of all submissions in some lines; multi-agent design; underwriter keeps the decision | Checked online (trade press reporting investor day and earnings call) |
| Upstart (2026), second-quarter results | More than 90% of loans fully automated, with the company's definition | Checked online (primary press release). The share of applications sent to manual review comes from press summaries of the earnings presentation: **author to check the presentation itself** |

| AWS (2026b), What is AWS Audit Manager? | Evidence collection that explicitly does not assess compliance | Checked online (URL and statement). The service closed to new customers in 2026; the documentation remains. |
| Fu et al. (2026), CI-Work | Contextual integrity in enterprise agents | Checked online (ACL 2026 Industry Track, pages 1483-1508, DOI) |
| Vu et al. (2025) | Agentic BPM, practitioner perspectives | Checked online; reference updated to the published BPM 2025 forum version, arXiv:2504.03693 |
