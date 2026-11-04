"""Surface statistics for the style signal, not evidence of authorship.

The score combines normalized sentence-length variation, word diversity, and
punctuation density. Short texts and changes in genre or editing can distort it.
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


def sentence_length_spread(text: str) -> float:
    """Coefficient of variation of sentence word counts; zero when fewer than two."""
    lengths = [len(words(sentence)) for sentence in sentences(text)]
    lengths = [length for length in lengths if length]
    if len(lengths) < 2:
        return 0.0
    return statistics.pstdev(lengths) / statistics.mean(lengths)


def type_token_ratio(text: str) -> float:
    """Unique lowercase words divided by all words; zero for no words."""
    tokens = words(text)
    return len(set(tokens)) / len(tokens) if tokens else 0.0


def punctuation_density(text: str) -> float:
    """Fraction of characters that are selected punctuation marks."""
    return sum(1 for char in text if char in ".,;:!?-\u2013\u2014") / len(text) if text else 0.0


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """Combine surface measures into an AI-likeness heuristic between zero and one."""
    # Missing sentence variation is unknown, not evidence of machine authorship.
    spread_component = 0.5 if len(sentences(text)) < 2 else 1 - min(sentence_length_spread(text) / 0.8, 1)
    diversity_component = 1 - type_token_ratio(text)
    punctuation_component = 1 - min(punctuation_density(text) / 0.12, 1)
    return round(0.4 * spread_component + 0.3 * diversity_component + 0.3 * punctuation_component, 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
