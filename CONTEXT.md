# LLM Benchmark Context

This context describes the benchmark-domain language used by the local LLM benchmark suite. It exists so architecture reviews and refactors use the same terms for benchmark execution, artifacts, and runtime fit.

## Language

**Benchmark queue**:
The ordered set of model candidates derived from `compatible_models.py`, with stable identity and runtime metadata for each candidate.
_Avoid_: model list, candidate array

**Model entry**:
One normalized record in the benchmark queue, including requested name, queue ID, category, runtime, model reference, and status.
_Avoid_: model dict, row

**Runtime capability**:
The resolved fit of a model entry for local execution: provider source, runtime, loadability, benchability, and lifecycle requirements.
_Avoid_: provider check, runtime flags

**Model lifecycle**:
The acquisition and cleanup span for one model entry, including pull/load, optional runtime adapter, and delete/unload.
_Avoid_: download step, cleanup code

**Phase 1 benchmark pass**:
The per-model prompt pass that records streaming speed, latency, VRAM, structured-output success, checkpoints, and final CSV artifacts.
_Avoid_: run_benchmarks script, CSV phase

**Phase orchestration**:
The one-pull, three-tests, one-delete flow that runs Phase 1, llama-bench, promptfoo, and final report generation for each eligible model.
_Avoid_: mega script, pipeline glue

**Artifact store**:
The module that owns benchmark file paths and raw artifact reads/writes.
_Avoid_: results helper, file utility

**Result projection**:
The metric and prompt payload view derived from stored benchmark artifacts.
_Avoid_: report helper, metrics utility

**Progress projection**:
The status view derived from progress records, queue metadata, process state, and result projection.
_Avoid_: dashboard formatter, status helper

## Flagged Ambiguities

**Phase 2**:
Historically, the code used "Phase 2" for structured-output checks inside Phase 1 while the orchestrator labels llama-bench as Test B. Use **Phase 1 benchmark pass** for the CSV/structured-output pass, and use **llama-bench** for hardware throughput.

## Example Dialogue

Dev: "Why did this model skip llama-bench?"

Domain expert: "Check the model entry's runtime capability. If it is not benchable for llama-bench, the phase orchestration should skip the llama-bench adapter without duplicating runtime rules."

Dev: "Where should dashboard pass rate calculation live?"

Domain expert: "In result projection. The artifact store should only know where the promptfoo artifacts are and how to read them."
