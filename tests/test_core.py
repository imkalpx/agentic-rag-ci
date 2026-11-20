"""Offline unit tests for the pure parts of the pipeline.

None of these call Groq or Pinecone, so they run without API keys.
"""

from src.ingest import chunk_text, slugify
from src.report import groundedness
from src.retrieval import rrf_merge
from app.newsprint import esc, split_summary


# --- Chunking ---------------------------------------------------------------

def test_chunk_text_short_text_is_single_chunk():
    assert chunk_text("hello world", size=10, overlap=2) == ["hello world"]


def test_chunk_text_empty_returns_nothing():
    assert chunk_text("   ", size=10, overlap=2) == []


def test_chunk_text_overlaps_and_covers_all_words():
    words = [f"w{i}" for i in range(25)]
    chunks = chunk_text(" ".join(words), size=10, overlap=3)
    assert chunks[0].split() == words[:10]
    # each chunk starts `size - overlap` words after the previous one
    assert chunks[1].split()[0] == "w7"
    covered = {w for c in chunks for w in c.split()}
    assert covered == set(words)


def test_slugify():
    assert slugify("Mistral AI") == "mistral-ai"
    assert slugify("  OpenAI!! ") == "openai"


# --- Reciprocal Rank Fusion -------------------------------------------------

def test_rrf_rewards_documents_ranked_well_in_both_lists():
    semantic = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    bm25 = [{"id": "b"}, {"id": "d"}, {"id": "a"}]
    merged = rrf_merge([semantic, bm25])
    ids = [m["id"] for m in merged]
    assert set(ids) == {"a", "b", "c", "d"}
    assert ids[0] == "b"          # rank 2 + rank 1 beats rank 1 + rank 3
    assert ids[-1] in {"c", "d"}  # only appear in one list


def test_rrf_scores_use_k_constant():
    merged = rrf_merge([[{"id": "x"}]], k=60)
    assert abs(merged[0]["rrf"] - 1 / 61) < 1e-12


# --- Groundedness metrics ---------------------------------------------------

def test_groundedness_catches_invented_numbers():
    report = {"sections": [{
        "evidence_texts": ["Revenue grew to 3.4 billion in 2024."],
        "section": "\n".join([
            "- Revenue reached 3.4 billion in 2024 [1]",
            "- Market share is 72 percent, per analysts",
        ]),
    }]}
    m = groundedness(report)
    assert m["bullets"] == 2
    assert m["citation_coverage"] == 0.5
    # 3.4 and 2024 are in evidence, 72 is invented
    assert m["number_fidelity"] == round(2 / 3, 3)


def test_groundedness_with_no_numbers_is_fully_faithful():
    report = {"sections": [{"evidence_texts": ["x"],
                            "section": "- A qualitative point with a cite [1]"}]}
    assert groundedness(report)["number_fidelity"] == 1.0


# --- Newsprint helpers ------------------------------------------------------

def test_esc_escapes_html():
    assert "<script>" not in esc("<script>alert(1)</script>")


def test_split_summary_returns_two_strings():
    head, rest = split_summary("First sentence. Second sentence.")
    assert isinstance(head, str) and isinstance(rest, str)
