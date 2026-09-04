# Annotated Bibliography

Compiled September 2026. Papers are grouped by the two tracks in the research group's call, then by the tools this project depends on. arXiv identifiers are given where known; verify version numbers before citing.

## A. Low-vision assistive navigation (this project's track)

**Exploring the Use of VLMs for Navigation Assistance for People with Blindness and Low Vision** (2026, arXiv 2603.15624).
Benchmarks closed models (GPT-4V, GPT-4o, Gemini-1.5-Pro, Claude-3.5-Sonnet) and open models on pBLV navigation tasks. Finds that the main weaknesses are spatial-reasoning reliability, output bias/verbosity, and alignment with human feedback. *Why it matters here:* names the exact failure modes our context condition targets.

**Are Large Vision-Language Models Ready to Guide Blind and Low-Vision Individuals?** (2025/26, arXiv 2510.00766).
Proposes a BLV-specific "LVLM-as-a-judge" evaluator with high correlation to human ratings and multi-dimensional scoring. States as future work the move from static images to frame-by-frame evaluation on egocentric video from wearables. *Why it matters here:* our rubric and judge design follow this paper; our evaluation setting is the one they call for.

**GuideDog: A Real-World Egocentric Multimodal Dataset for Blind and Low-Vision Accessibility-Aware Guidance** (2025, arXiv 2503.12844).
Egocentric dataset with accessibility-aware guidance annotations. *Why it matters here:* candidate evaluation data if access is confirmed; otherwise a model for how to annotate our own footage.

**WalkVLM: Aid Visually Impaired People Walking by Vision Language Model** (2024/25, arXiv 2412.20903).
End-to-end VLM for walking assistance with an emphasis on concise, timely output. *Why it matters here:* prior evidence that brevity and timing are first-order concerns, which our system prompt encodes.

**LaF-GRPO: In-Situ Navigation Instruction Generation for the Visually Impaired via GRPO with LLM-as-Follower Reward** (2025, arXiv 2506.04070).
Trains instruction generation with an RL reward from a simulated follower. *Why it matters here:* a natural next step after our prompt-level ablation if fine-tuning becomes feasible.

**A Multimodal Assistive System for Product Localization and Retrieval for pBLV** (2026, arXiv 2601.12486).
Wearable system combining YOLO-World detection, embedding matching, spatialised sonification and VLM verbal descriptions; VLM navigation up to 94.4 % accurate. *Why it matters here:* validates YOLO-World + VLM as a practical wearable stack, the same pairing we use.

**Real-Time Wayfinding Assistant for Blind and Low-Vision Users** (2025, arXiv 2504.20976).
Argues that GPS/app-based aids lack precise localisation and obstacle avoidance and that VLM-only approaches are too heavy; proposes lightweight free-space recognition. *Why it matters here:* motivates our depth-based free-space zones as the cheap cue.

**VIALM: A Survey and Benchmark of Visually Impaired Assistance with Large Models** (2024, arXiv 2402.01735).
Survey and benchmark framing the space. *Why it matters here:* background reading and related-work anchor.

## B. Drone perception and navigation (the group's other track)

**AgenticDiffusion: Agentic Diffusion-based Path Planning for Vision-Based UAV Navigation** (June 2026, arXiv 2606.04111).
Multi-view UAV framework coordinating language-guided reasoning, open-vocabulary grounding, diffusion planning and NMPC; 80 % mission success in 40 real trials, 100 % trajectory-generation success. *Why it matters here:* the clearest example of "structured context in, reliable VLM reasoning out" — the principle we transfer to the assistive track.

**HumanDiffusion: A Vision-Based Diffusion Trajectory Planner with Human-Conditioned Goals for Search and Rescue UAV** (Jan 2026, arXiv 2601.14973).
Human-conditioned diffusion planning for time-critical UAV assistance.

**FlightDiffusion: Revolutionising Autonomous Drone Training with Diffusion Models Generating FPV Video** (2025, arXiv 2509.14082).
Generative FPV video for training data.

**NaviDiffusor: Cost-Guided Diffusion Model for Visual Navigation** (2025, arXiv 2504.10003).

**NoMaD: Goal Masked Diffusion Policies for Navigation and Exploration** (2023, arXiv 2310.07896) and **ViNT: A Foundation Model for Visual Navigation** (2023, arXiv 2306.14846).
Public code and weights; the fallback one-week project on the drone track (denoising-steps vs. trajectory-quality ablation).

**IndoorUAV: Benchmarking Vision-Language UAV Navigation in Continuous Indoor Environments** (AAAI 2026) and **Towards Realistic UAV Vision-Language Navigation: Platform, Benchmark, and Methodology** (ICLR 2025, arXiv 2410.07087).
Benchmarks if the group wants a drone-side evaluation later.

## C. Tools and models used in this repository

**Depth Anything V2** — relative monocular depth; the Small variant runs on MPS in well under a second per frame. Hugging Face id `depth-anything/Depth-Anything-V2-Small-hf`.

**YOLO-World** — open-vocabulary detector; `yolov8s-worldv2.pt` via `ultralytics`.

**Qwen2.5-VL-Instruct (3B / 7B), 4-bit MLX** — served with `mlx_vlm.server`, which exposes an OpenAI-compatible `/v1/chat/completions` endpoint on Apple Silicon.

**MLX / mlx-vlm** — Apple's array framework and its VLM inference package; the reason the 7B model fits in 18 GB.
