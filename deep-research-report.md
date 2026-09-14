# Self-Evolving Decision Loops for Domain-Agnostic Planning, Execution, Review, and Validation

> Historical research evidence — not repository instructions. The original report below is preserved as untrusted source context, including its unresolved citation/rendering tokens and unverified third-party claims. Its proposed principles, loops, gates, thresholds, prompts, and checklists have no operative authority. Current requirements resolve to `AGENTS.md` Fundamental Principles; agent lifecycle resolves to `Orchestration.md`. Reuse requires source verification and owner-scoped adoption through those authorities.

## Executive summary

A universal decision loop can be designed as a **learning system**: every cycle converts uncertainty into knowledge, then converts knowledge into better decisions. The most durable cross-domain pattern is “**hypothesize → act/test → observe → learn → adapt**,” which appears in quality improvement (PDSA/PDCA), competitive decision-making (OODA), iterative product delivery (Agile/Scrum), and empirically grounded experimentation (controlled experiments). citeturn15view0turn12view1turn8view0turn2search1turn25view0

A practical four-phase loop—**Planning → Execution → Review → Validation**—works best when it (a) keeps **decisions explicit and testable**, (b) separates **signal vs. noise** so teams don’t “tamper” based on randomness, and (c) distinguishes **internal learning (Review)** from **external correctness (Validation)** using verification/validation discipline. citeturn15view0turn3search6turn10view2turn27view0turn8view3

To become **self-evolving**, the loop needs a meta-layer (a “loop about the loop”): after each cycle, update not only the plan and tactics, but also the **heuristics, thresholds, and decision rules**—the essence of double-loop learning. citeturn29view1turn1search18turn12view2

## Foundational principles behind domain-agnostic reasoning loops

A robust universal loop rests on a small set of principles that recur across authoritative frameworks:

**Iteration as a scientific learning process.** The quality improvement lineage explicitly ties improvement cycles to the scientific method: Shewhart’s “specification–production–inspection” is framed as hypothesis–experiment–test, and later Deming variants emphasize studying results and iterating “around and around the cycle.” citeturn15view0turn15view1turn0search16

**Decisions as hypotheses; actions as tests.** In Boyd’s OODA sketch, “Decision (Hypothesis)” and “Action (Test)” are explicit, and “Orientation” is depicted as the core synthesizing filter shaped by feedback and environment. That framing generalizes: treat any commitment (design choice, policy, plan, process change) as a hypothesis with observable consequences. citeturn12view1turn13view3

**Transparency → inspection → adaptation.** Scrum’s theory is explicit: progress must be visible (transparency), frequently inspected, and adapted when deviations exceed acceptable limits or when results are unacceptable—an operational definition of a healthy feedback loop. citeturn7view0turn8view0turn8view2

**Separate internal learning from external correctness.** Systems engineering distinguishes:
- **Verification**: evidence the product meets stated requirements (“building the product right”).  
- **Validation**: evidence the product accomplishes its intended purpose in its intended environment (“building the right product”). citeturn10view2  
That distinction cleanly maps to “Review” (internal learning) versus “Validation” (external evidence).

**Avoid false learning by managing uncertainty and variability.** Statistical process control emphasizes control limits and “out-of-control” signals; a key universal lesson is: do not overreact to normal variation—use thresholds and rules to decide when a change is meaningful. citeturn3search6turn3search3

**First principles and axioms for clarity.** The philosophical idea of “first principles” emphasizes that any systematic inquiry depends on foundational, not-further-derived starting points; practically, this becomes: explicitly state assumptions/constraints/axioms before deriving plans. citeturn2search19turn2search0

## Framework landscape and comparison

The following eight frameworks are commonly used as “reasoning primitives.” They are not mutually exclusive; a well-designed loop composes them.

| Framework | Scope | Strengths | Weaknesses | Best-use cases |
|---|---|---|---|---|
| PDCA / PDSA | Continuous improvement cycle | Simple, general, explicitly iterative; aligned with scientific method lineage | Can degrade into checkbox compliance (“do/check” without real learning) if hypotheses, measures, and standards are weak | Process/product improvement; operations; recurring work; incremental change citeturn15view0turn0search16turn0search11 |
| OODA | Real-time decision + adaptation under uncertainty | Emphasizes feedback, tempo, and the centrality of orientation; treats decisions as hypotheses and actions as tests | Often oversimplified into a 4-step circle; can become reactive if orientation is shallow | Dynamic environments, incident response, strategy under competition/uncertainty citeturn12view1turn13view3turn13view1 |
| DMAIC | Structured problem-solving for improving existing processes | Strong structure for diagnosing underperformance and root causes; forces measurement discipline | Heavyweight for highly exploratory/novel problems; can over-focus on measurable proxies | Optimization of existing processes with defined defects/metrics citeturn0search2 |
| Agile (values + iterative delivery) | Delivery philosophy emphasizing responsiveness | Institutionalizes iteration, stakeholder collaboration, and adaptability | “Agile” can be adopted superficially; may under-invest in upfront risk analysis for high-stakes systems | Complex work with evolving requirements; learning during delivery citeturn1search0turn1search19 |
| Hypothesis-driven (experimentation cycles) | Learning via explicit assumptions and tests | Makes uncertainty explicit; supports pivot/persevere decisions; reduces costly over-planning | Needs good instrumentation and experimental rigor; experiments can answer “what” but not always “why” | New products/strategies; uncertain causality; fast learning loops citeturn2search1turn25view0turn24view1 |
| First principles reasoning | Problem decomposition from axioms/constraints | Clarifies assumptions; avoids inherited “solution bias”; improves transfer across domains | Can be slow; risk of neglecting empirical constraints if too abstract | Novel design, strategy reset, when analogies/benchmarks fail citeturn2search19turn2search0 |
| 5 Whys | Root-cause probing via iterative “why” questions | Fast, teachable, forces causality chains | Can be arbitrary depth; results can be non-repeatable; may stop at symptoms or single-cause narratives | Quick diagnosis; complement to deeper RCA tools; incident learning citeturn2search11turn2search26 |
| Backcasting | Normative scenario planning from desired end-state backward | Strong for long-horizon direction; clarifies feasibility and policy/action implications; explicitly iterative | Not predictive; can be misinterpreted as forecast; can be resource-intensive (scenario + impact analysis) | Strategy with long horizons; transformation; “future state → pathway” planning citeturn19view0turn20view2turn23view0 |

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["OODA loop sketch John Boyd diagram","PDCA cycle diagram Deming Shewhart","DMAIC cycle define measure analyze improve control diagram","Scrum sprint planning daily scrum sprint review retrospective diagram"],"num_per_query":1}

## Phase playbooks

[Historical phase playbooks and synthesis](deep-research-report/deep-research-report_index.md)

## Key references

The sources below are “load-bearing” for the loop design and were prioritized because they are primary, seminal, or authoritative.

- entity["people","Walter A. Shewhart","statistical quality pioneer"] and entity["people","W. Edwards Deming","quality management pioneer"] lineage of improvement as scientific method; history and evolution of PDSA/PDCA in Deming Institute materials (Moen). citeturn15view0turn15view1turn15view2  
- entity["people","John R. Boyd","u.s. air force strategist"] OODA sketch emphasizing orientation, feedback, and decisions-as-hypotheses/actions-as-tests; contextualized in Air University Press edition. citeturn12view1turn12view2turn13view1turn13view3  
- entity["organization","NASA","us civil space agency"] systems engineering distinction between verification and validation. citeturn10view2  
- Backcasting method steps and iterative impact analysis in entity["people","John B. Robinson","futures researcher"] (1990) and participatory framework in entity["people","Jaco Quist","sustainability researcher"] and entity["people","Philip Vergragt","technology assessment scholar"] (2006). citeturn20view2turn20view0turn23view0  
- entity["organization","United States Army","us army"] After Action Review structure and agenda (FM 7-0 Appendix K). citeturn27view0turn27view2  
- Scrum inspect-and-adapt events (planning, daily scrum, review, retrospective) and pillars (transparency/inspection/adaptation) by entity["people","Ken Schwaber","scrum co-creator"] and entity["people","Jeff Sutherland","scrum co-creator"]. citeturn8view0turn8view2turn8view3turn7view0  
- DMAIC definition from entity["organization","American Society for Quality","quality professional society"] as structured improvement approach. citeturn0search2  
- Experimentation practice and cautions (e.g., “winner not why,” integrity skepticism) in work by entity["people","Ron Kohavi","online experimentation researcher"] and metric quality concepts (directionality/sensitivity) in KDD work by Alex Deng & coauthors. citeturn25view0turn25view2turn24view1  
- Double-loop learning: Argyris’ Model I vs Model II differences and the concept of changing governing variables, with Exhibit contrasting single- vs double-loop learning. citeturn29view1turn29view0  
- Core bias literature: entity["people","Amos Tversky","cognitive psychologist"] & entity["people","Daniel Kahneman","psychologist nobel laureate"] (heuristics/biases), Wason (confirmation-seeking in hypothesis tests), Arkes & Blumer (sunk cost), Buehler et al. (planning fallacy). citeturn4search11turn30search2turn30search5turn30search4