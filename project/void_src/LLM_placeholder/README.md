# LLM Folder

Place your fine-tuned Telugu LoRA adapter files here.

Expected files:
- adapter_config.json
- adapter_model.safetensors
- tokenizer.json
- tokenizer_config.json (must have "tokenizer_class": "LlamaTokenizer")
- README.md (optional)

This folder path is referenced in backend/.env as:
ADAPTER_PATH=../LLM
