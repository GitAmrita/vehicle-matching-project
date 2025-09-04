import random
import json
import os

# Load abbreviation mapping from JSON file
_ABBR_JSON_PATH = os.path.join(os.path.dirname(__file__), "make_abbreviations.json")
with open(_ABBR_JSON_PATH, "r", encoding="utf-8") as f:
    MAKE_ABBR_MAP = json.load(f)

# --- Noise generation functions ---

def typo_variant(word):
    if len(word) < 2:
        return word
    i = random.randint(0, len(word) - 2)
    return word[:i] + word[i+1] + word[i] + word[i+2:]

def generate_variants(model_name, make_name, year, n_variants=4):
    variants = set()
    variant_choices = []

    while len(variants) < n_variants:
        choice = random.choice(["typo_model", "typo_make", "abbrev", "reorder", "drop"])
        tokens = [str(year), make_name, model_name]

        if choice == "typo_model":
            variant = f"{year} {make_name} {typo_variant(model_name)}"
        elif choice == "typo_make":
            variant = f"{year} {typo_variant(make_name)} {model_name}"
        elif choice == "abbrev":
            abbr_make = MAKE_ABBR_MAP.get(make_name, make_name)
            variant = f"{year} {abbr_make} {model_name}"
        elif choice == "reorder":
            random.shuffle(tokens)
            variant = " ".join(tokens)
        elif choice == "drop":
            drop_idx = random.randint(0, 2)
            drop_tokens = [t for idx, t in enumerate(tokens) if idx != drop_idx]
            variant = " ".join(drop_tokens)
        else:
            continue

        if variant not in variants:
            variants.add(variant)
            variant_choices.append((variant, choice))

    return variant_choices
