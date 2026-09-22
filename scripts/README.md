# Benchmark drivers

The scripts that produced the runs in `docs/RESULTS.md`. Each serves or loads one model at a
time and is resumable: rerunning continues from the rows already in `runs/<model>/<task>.jsonl`.

| script | what it runs |
|---|---|
| `run_local_models.sh` | the original chain: all five local models, each served by `mlx_vlm.server` |
| `run_remaining_models.sh` | the two the first chain failed on, with the causes fixed (see below) |

`run_local_models.sh` is kept as it was when it produced the three Qwen runs, including the two
faults it hit, so the log in `docs/PROGRESS.md` matches a script in the repository:

- its readiness loop waits 600 s for a server, which is less than a cold 4.26 GB download takes,
  and it then kills that download in cleanup — this is why LLaVA produced nothing;
- it serves every model over HTTP, which InternVL3-2B cannot be (the server generates on a pool
  thread and its prompt cache dies with `There is no Stream(gpu, 2) in current thread`).

`run_remaining_models.sh` fixes both: weights are fetched to completion before the server starts,
with a 30 min window for the load, and InternVL3-2B runs on the in-process `mlx-direct` backend
with no server at all.

## A trap worth knowing: `hf download` does not resume

Each attempt writes a **new** `<etag>.<random>.incomplete` and starts from zero. An interrupted
download therefore leaves a multi-gigabyte orphan that nothing will ever pick up, and the next
attempt needs the model's full size again. Three interrupted attempts at LLaVA's 4.26 GB left
5.4 GB of dead partials and took the disk down to 1.9 GB free.

`run_remaining_models.sh` clears stale partials before fetching and again if the fetch fails, so
the space required is the size of the model rather than a multiple of it. The copy that actually
produced the InternVL3 run predates this guard; it was added after the behaviour was observed.
