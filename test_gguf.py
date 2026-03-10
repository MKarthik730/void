"""
Patches the GGUF file to fix broken add_eos_token metadata.
Run once: python patch_gguf.py
"""
import struct
import shutil

INPUT  = r"D:\telugu-llama-7b-instruct-v0.1.Q4_K_M.gguf"
OUTPUT = r"D:\telugu-llama-fixed.gguf"

print(f"Copying {INPUT} -> {OUTPUT} ...")
shutil.copy2(INPUT, OUTPUT)
print("Copy done. Patching metadata...")

with open(OUTPUT, "rb") as f:
    data = bytearray(f.read())

def find_and_patch(data, key: str, new_value: int):
    key_bytes = key.encode("utf-8")
    key_len   = len(key_bytes)
    needle    = struct.pack("<Q", key_len) + key_bytes
    pos       = data.find(needle)
    if pos == -1:
        print(f"  Key '{key}' NOT FOUND")
        return False
    val_type_pos = pos + len(needle)
    val_type     = struct.unpack("<I", data[val_type_pos:val_type_pos+4])[0]
    val_pos      = val_type_pos + 4
    old_val      = data[val_pos]
    print(f"  '{key}' -> type={val_type}, old={old_val}, new={new_value}")
    data[val_pos] = new_value
    return True

find_and_patch(data, "tokenizer.ggml.add_eos_token", 0)
find_and_patch(data, "tokenizer.ggml.add_bos_token", 1)

with open(OUTPUT, "wb") as f:
    f.write(data)

print(f"\n✅ Done! Patched file: {OUTPUT}")
print("Now update your model_path to:")
print(f'  r"{OUTPUT}"')