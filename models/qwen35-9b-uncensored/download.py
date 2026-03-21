from huggingface_hub import hf_hub_download

repo_id = "HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive"
import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

print("Downloading main model Q4_K_M...")
hf_hub_download(
    repo_id=repo_id, 
    filename="Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf", 
    local_dir=".", 
    local_dir_use_symlinks=False
)

print("Downloading vision encoder (mmproj)...")
hf_hub_download(
    repo_id=repo_id, 
    filename="mmproj-Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-BF16.gguf", 
    local_dir=".", 
    local_dir_use_symlinks=False
)

print("All downloads completed successfully.")
