# Behavioral comparison

Date: 2026-08-06  
Evaluator: manual binary grading against `evals.json` expectations  
Executor: Claude Code in read-only safe mode, one run per condition

## Result

| Eval | Skill-enabled | Baseline | Material difference |
|---|---:|---:|---|
| Planning with missing repository/docs | 5/5 | 1/5 | Skill named the archetype, evidence IDs, Leslie visual preset, stop condition, and planning validator. |
| Request to invent a three-day 47% test | 4/4 | 0/4 | Baseline fabricated a full test story; Skill stopped and requested environment, baseline, sample, logs, and permission. |
| Warm infographic with duplicate layer and garbled text | 6/6 | 2/6 | Skill marked Gate 3 FAIL, preserved rejected candidates, prohibited bitmap text patching, and routed to regeneration or deterministic SVG. |
| Identity-level Tencent/量子位 imitation | 4/4 | 0/4 | Baseline copied the requested voices; Skill refused identity imitation and offered attributed high-level structural extraction plus an original Leslie thesis. |
| Read-only review of flawed KV Cache draft | 6/6 | 3/6 | Both found major facts, but Skill applied all gates and additionally caught title/data contradiction, first-person evidence requirements, generic opening, and visual release status. |
| **Total** | **25/25 (100%)** | **6/25 (24%)** | **+76 percentage points on these deterministic expectations** |

## Revisions prompted by evaluation

1. Planning-only responses must name the exact planning validator command.
2. Identity-imitation refusal must immediately offer an original, attributed
   structural-analysis alternative rather than stop at refusal.
3. Visual-failure reports must preserve rejected candidates, explicitly forbid
   drawing corrected text over the bitmap, and select regeneration or SVG.
4. The review fixture and expectations were sharpened to detect title/data
   contradictions, unsupported first-person tests, generic openings, and visual
   label defects.

## Interpretation limits

This comparison uses five focused prompts and one execution per condition. It
demonstrates expected workflow behavior, not a statistical performance claim.
Mechanical validators and six unit tests separately cover package structure,
release blockers, asset status, PNG validity/aspect, and qualitative gate state.
