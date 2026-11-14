from explainer_studio.scene_kit import *


class EndCredits(EndCreditsScene):
    source_lines = [
        "Hugging Face, Transformers documentation, “Caching”: attention matrices, Cache class, generation loop",
        "NVIDIA Technical Blog, “Mastering LLM Techniques: Inference Optimization”: prefill, decode, KV caching",
        "A. Vaswani et al., “Attention Is All You Need” (2017): scaled dot-product attention",
        "Toy model, scores and token pieces: illustrative values computed by this project's lesson/mechanism.js",
    ]
    asset_name_by_file_path_map = {}
