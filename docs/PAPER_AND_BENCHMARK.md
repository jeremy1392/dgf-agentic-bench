# Paper and benchmark relationship

The paper and DGF-Bench serve different roles.

## Paper

`paper/Every_Gate_Becomes_Software.pdf` develops the theoretical argument that Digital Governance Framework gates are information-transforming contracts and formalizes complete execution, labor accounting, handoff effects, route composition, and a falsifiable long-horizon claim.

The paper does **not** claim that the current repository proves universal real-world substitution. Its numerical workforce examples are synthetic calculations.

## DGF-Bench

DGF-Bench operationalizes the unit of analysis from the paper:

- a versioned case state;
- admissible evidence;
- gate-specific rules;
- inquiry and evidence requests;
- findings and dispositions;
- required actions;
- authority/authorization state;
- downstream handoff artifacts.

Cases are generated facts-first. Hidden reference outcomes are derived from the latent state rather than being independently randomized.

## What experiments can establish

Controlled model experiments can establish performance **within the declared synthetic case population**, for example:

- which gate families are easier or harder for current agents;
- whether agents miss critical evidence;
- how often agents falsely approve unsafe/incomplete cases;
- whether structured handoffs improve downstream execution;
- how gate-level reliability compounds across routes;
- quality/cost tradeoffs across model families.

These are empirical benchmark results. They are not by themselves proof that every real-world enterprise DGF can be fully automated.

## Suggested publication split

A natural publication strategy is:

1. **Every Gate Becomes Software** - theory, definitions, economics, workforce consequences, and falsifiable claim.
2. **DGF-Bench: Measuring Complete Automation of Enterprise Governance** - benchmark design, synthetic environment, model evaluations, ablations, and reproducibility artifacts.
