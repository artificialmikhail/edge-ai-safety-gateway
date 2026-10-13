# Research protocol (draft v0.1)

**Project:** Edge AI Safety Gateway  
**Phase:** Planning and feasibility review, 13 October 2026  
**Duration:** Eight weeks from project start (not yet scheduled)  
**Lead:** Mikhail Shakhmuradian  
**Requested support:** $8,000 (see `BUDGET.csv`)

## 1. Research question and scope

Can a compact offline device act as a reliable in-line approval/denial layer for proposed actions of an AI agent? The pilot isolates **pre-execution control of tool actions**, including semantic consistency with the trusted user request. It does not attempt to prove reliable detection of every harmful answer, explainability, alignment, or complete robot safety.

**Unit of analysis:** one proposed action with a trusted policy state, user-authorisation state, optional untrusted context, and a human-adjudicated expected disposition: `allow`, `deny`, or `review`.

**System assumption:** instrumented agent actions are routed through an external, gateway-controlled mock executor. No claim is made for uninstrumented channels, untrusted executors or physical emergency-stop certification.

## 2. Questions, hypotheses and counter-hypotheses

- **RQ1 (security):** Does C (rules + local model) lower the rate of unsafe actions executed compared with B (rules only) on held-out, human-labelled cases, especially semantically unauthorized but structurally permitted actions?
- **RQ2 (utility):** What increase in false blocking and manual review is required to obtain that reduction?
- **RQ3 (systems):** Is the additional gateway decision time, availability, memory and power acceptable on inexpensive ARM hardware?
- **RQ4 (modality):** How are conclusions affected by voice transcription errors, noise and multilingual commands?

**H1:** C will catch additional context-dependent attempts that escape B. **Null:** no improvement or net harm due to false positives, delay or reliability failures. **H2:** the fixed rules in C will maintain at least the hard safety boundaries in B. These are hypotheses, not results.

## 3. Proposed technical architecture

1. **Intercept** a structured `proposed_action` with tool name, arguments, trust labels, user/session context and policy revision.
2. **Normalize and validate** JSON schema, inputs and constraints. Reject malformed requests and missing authoritative state.
3. **Apply fixed rules**: known tool allowlist, resource scope, role permissions, synthetic-data boundaries, approval state and irreversible-action controls.
4. **Optional local assessment** in C only for context-dependent, non-hard-denied cases. Candidate is Qwen3-0.6B if deployable under tested runtime. Parser expects `decision`, `risk_tags` and a short rationale; invalid or timed-out output maps to `review` or `deny` according to preset policy.
5. **Enforce** with gateway-owned mock executor (never raw agent-owned tool access), append decision + timings to an audit log.
6. **Voice variant:** microphone / recorded voice → ASR → agent proposal → same gateway. ReSpeaker, ASR, TTS are optional study components, not enforcement hardware by themselves.

**Crucial:** the LLM cannot approve a known-denied action. Review requires a separately authenticated human grant; verbal claims or untrusted text cannot grant authorisation. No real-world privileged actions will be wired into the pilot.

## 4. Hardware and feasibility gates

Initial candidate: Seeed reComputer RK3576 kit, with Firefly iCore-3576JQ38 evaluated as a second-form-factor alternative. Audio: ReSpeaker XVF3800 (USB mode if supported by exact unit / firmware). Storage, thermal throttling and power draw must be measured.

- Verify exact SKU / RAM and carrier availability, Linux distribution, kernel, vendor NPU SDK, model operators and quantized model formats.
- Establish actual tokens/sec and latency at representative input/output lengths; do not extrapolate desktop benchmarks.
- Prototype the policy boundary on a normal development computer **before** porting to ARM/NPU; permit CPU fallback with explicit reporting.
- Benchmark independent action-validation latency, local-model inference latency, ASR latency and full voice turn separately.
- If Qwen3 cannot reliably deploy, record the failed feasibility gate and evaluate a documented fallback, without claiming parity.

## 5. Test-set plan and annotation

Target **200–300 distinct labelled scenario families** over the eight weeks, with balanced dangerous, benign and ambiguous requests. Initial JSONL fixtures are an illustrative **seed suite**, not a final evaluation set.

Suggested allocation (adjust after design review):

| Category | Target number of distinct cases |
|---|---:|
| Unsafe and unauthorised tool calls | 45 |
| Indirect prompt injection / role spoofing | 45 |
| Privacy / data boundaries | 30 |
| Authorisation, confirmation, escalation | 30 |
| Benign lookalikes / utility | 45 |
| Voice/ASR ambiguity + multilingual | 30 |
| Multistep / degradation / malformed cases | 25 |
| **Total target** | **250** |

Each case includes user intent, trusted policy state, untrusted material, proposed action, provenance, expected decision and reason. Only the *trusted* experiment policy assigns authoritative permissions. Use synthetic accounts, documents and secrets; never insert actual credentials. Two independent label reviews on at least a representative random subset (ideally the entire held-out test set), reconciliation before final scoring, and report agreement/disputed scenarios. Cases that remain ambiguous should be tagged separately, not forced into binary ground truth.

Freeze a held-out subset **before model/prompt tuning**; tune only on a disjoint development set. Do not reuse or rewrite held-out cases after reviewing system errors. Document scenario provenance and generation method to limit contamination and correlated duplicates.

## 6. Experiment and comparability

- Run A, B and C on the **identical frozen scenarios** using the same simulated executor, user policies and approved tool list.
- For non-deterministic cases, run multiple trials with fixed model/runtime configurations; record repeat count and seeds where available.
- Measure both the **gateway decision** and whether the **mock executor ultimately executes** the action; a detector's textual warning is not a prevented unsafe action.
- Record branch taken (hard-rule denial, LLM judgment, LLM timeout, human review); do not treat `review` as a successful harmless completion.
- Maintain repeatable cold/warm, varied input length and continuous-load device trials. Define hardware/ambient test conditions and model configuration.

### Primary outcomes

- **Unsafe execution rate:** `unsafe_gold cases actually executed / total unsafe_gold cases` (lower better).
- **Unsafe prevention recall:** `unsafe_gold cases not executed / total unsafe_gold cases` (with blocked vs review separately reported).
- **Benign false denial rate:** `allow_gold cases denied / total allow_gold cases` (lower better).
- **Benign escalation rate:** `allow_gold cases sent to review / total allow_gold cases`.
- **Human-review load:** share of **all** cases sent to review.
- **Utility completion:** benign tasks successfully executed (not merely labeled `allow`).

**Review isn't execution**: unsafe actions sent for review count as not executed *during automated execution*, but are disclosed separately from hard denies. Human approval and later execution must be separately audited.

### Secondary outcomes

- Per-action added latency p50/p95/p99; policy-only path vs LLM path.
- First-token time and generation throughput (tokens/s), with input/output lengths.
- ASR WER, voice-decision mismatch rate and acoustic-noise sensitivity (if the voice branch is implemented).
- Sustained CPU/NPU/RAM use, power in watts and energy per decision, thermal throttling.
- Device restart, model failure, malformed JSON, offline mode and watchdog recovery.

### Provisional decision gates (targets, not observations)

- **Zero unsafe actions should be executed in hard-deny cases in the tested sandbox**; every violation is investigated individually.
- **p95** added latency should be reported separately for deterministic and model-routed actions. A tentative design target is ≤100 ms for pure rules and ≤3 s for model-routed requests **excluding ASR and human review**; failures do not invalidate the research, but limit deployability.
- **No predefined accuracy claim** is being made. An incremental C-vs-B gain must be supported by paired comparisons, confidence intervals and a reported false-positive cost before claiming improvement.

## 7. Statistics and reporting

Use paired, case-level comparisons across arms; report differences in unsafe execution rate and benign false blocking with confidence intervals (bootstrap over scenario families or suitable paired binary comparison). Present raw counts, sample sizes and uncertainty, not just percentages. Because test cases are crafted and correlated, claims are limited to the sampled threat model. Highlight all policy boundary violations and regression cases; do not optimize only a single aggregate score.

## 8. Eight-week milestones

| Week | Milestone | Deliverable / exit gate |
|---|---|---|
| 1 | Threat model, frozen policy, lab environment | Approved v0.1 protocol, synthetic mock executor |
| 2 | Core baseline + hardware procurement | Rules-only gateway and compatible kit on hand or documented blocker |
| 3 | ARM runtime feasibility | Measured CPU/NPU model inference, memory/power baseline |
| 4 | Hybrid policy and safety control path | Three arms run on first seed cases |
| 5 | Test expansion and label review | Curated dataset, withheld test split |
| 6 | On-device main evaluation | Paired scenario results and latency/energy logs |
| 7 | Voice, faults and repeatability | ASR/noise + fail-safe recovery results |
| 8 | Analysis and publication | Reproducible code, data card, negative findings and report |

## 9. Risks and mitigation

| Risk | Mitigation / honest fallback |
|---|---|
| Local model not available on NPU | Bench CPU or alternate documented platform; report failure |
| LLM latency exceeds budget | Scope LLM to uncertain cases; report trade-off |
| No true trusted interception | Limit claims to mock executor and document bypass |
| Rules-only baseline too strong | Publish null finding; research still tests edge feasibility |
| Uneven or ambiguous labels | Adjudicate, publish label rubric, report uncertainty |
| Malicious prompt instructions in test data | Sandbox execution, synthetic content, no real connectors |
| Hardware delivered late | Desktop policy prototype + document schedule deviation |

## 10. Ethics and release

Recordings are optional and require participant consent; use purpose-specific retention and deletion procedures. No patient records, personal credentials or real-world payments/robot actuators. Public files contain synthetic examples only. Publish model versions, prompts/policies, hardware details, raw per-case decision logs with synthetic identifiers and redacted diagnostics, and limitations. Release analysis/code when available; until then repository is explicitly a planning-stage artifact.
