import re
import math
from collections import Counter
import networkx as nx

# Built-in robust English stopword list for 100% offline, zero-dependency execution
STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "said", "also", "new", "one", "two", "mr", "ms", "will", "would", "us", "today", "per", "state"
])

def clean_and_tokenize(text):
    """Tokenizes text into words, removing punctuation and converting to lowercase."""
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def split_into_sentences(text):
    """Segments paragraph text into sentences using regex boundary detection."""
    text = text.strip()
    # Split on periods, exclamation marks, question marks followed by whitespace or end of string
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 15]
    return sentences

def compute_cosine_similarity(words1, words2):
    """Computes cosine similarity between two bag-of-words vectors."""
    if not words1 or not words2:
        return 0.0
    counter1 = Counter(words1)
    counter2 = Counter(words2)
    intersection = set(counter1.keys()) & set(counter2.keys())
    if not intersection:
        return 0.0
    dot_product = sum(counter1[w] * counter2[w] for w in intersection)
    norm1 = math.sqrt(sum(c ** 2 for c in counter1.values()))
    norm2 = math.sqrt(sum(c ** 2 for c in counter2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)

def textrank_summarize(text, num_summary_sentences=3, num_key_points=5, top_keywords_count=10):
    """
    Genuine TextRank Algorithm (Mihalcea & Tarau, EMNLP 2004 / IEEE ICCCA 2020).
    Builds a complete sentence similarity graph and computes PageRank convergence scores.
    """
    sentences = split_into_sentences(text)
    total_words = len(text.split())

    if len(sentences) <= num_summary_sentences:
        summary = " ".join(sentences)
        key_points = sentences
        keywords = list(Counter(clean_and_tokenize(text)).keys())[:top_keywords_count]
        return {
            "summary": summary,
            "key_points": key_points,
            "keywords": keywords,
            "stats": {
                "word_count": total_words,
                "sentence_count": len(sentences),
                "reading_time_min": max(1, round(total_words / 200, 1)),
                "compression_ratio": "100%"
            },
            "infographic_mermaid": "graph TD;\n  Topic[Main Article Topic] --> Point1[Key Information]"
        }

    # Tokenize each sentence
    tokenized_sentences = [clean_and_tokenize(s) for s in sentences]

    # Construct sentence graph
    graph = nx.Graph()
    n = len(sentences)
    for i in range(n):
        graph.add_node(i)

    for i in range(n):
        for j in range(i + 1, n):
            sim = compute_cosine_similarity(tokenized_sentences[i], tokenized_sentences[j])
            if sim > 0.05:  # Similarity threshold for edge creation
                graph.add_edge(i, j, weight=sim)

    # Compute PageRank scores on graph
    try:
        if graph.number_of_edges() > 0:
            scores = nx.pagerank(graph, alpha=0.85, max_iter=100, weight='weight')
        else:
            # Fallback to length / position weighting if graph is disconnected
            scores = {i: 1.0 / (i + 1) for i in range(n)}
    except Exception:
        scores = {i: 1.0 for i in range(n)}

    # Rank sentences by TextRank score
    ranked_indices = sorted(scores.keys(), key=lambda i: scores[i], reverse=True)

    # Select top sentences for summary and retain original chronological flow
    summary_indices = sorted(ranked_indices[:num_summary_sentences])
    summary_sentences = [sentences[idx] for idx in summary_indices]
    summary_text = " ".join(summary_sentences)

    # Key Points (Top distinct sentences formatted cleanly)
    key_point_indices = sorted(ranked_indices[:min(num_key_points, len(ranked_indices))])
    key_points = [sentences[idx] for idx in key_point_indices]

    # Keyword extraction using word frequency across the document
    all_tokens = clean_and_tokenize(text)
    word_freq = Counter(all_tokens)
    top_keywords = [word for word, count in word_freq.most_common(top_keywords_count)]

    # Dynamic Infographic / Visual Concept Network generation in Mermaid.js
    main_topic = top_keywords[0].capitalize() if top_keywords else "Article Focus"
    sec_topics = [k.capitalize() for k in top_keywords[1:5]]

    mermaid_lines = ["graph TD", f'  Root["Article Focus: {main_topic}"]:::mainNode']
    mermaid_lines.append("  classDef mainNode fill:#4f46e5,stroke:#312e81,stroke-width:2px,color:#fff,font-weight:bold,rx:8px;")
    mermaid_lines.append("  classDef subNode fill:#0284c7,stroke:#0369a1,stroke-width:1px,color:#fff,rx:6px;")
    mermaid_lines.append("  classDef detailNode fill:#10b981,stroke:#047857,stroke-width:1px,color:#fff,rx:4px;")

    for idx, topic in enumerate(sec_topics, start=1):
        mermaid_lines.append(f'  Root --> Sub{idx}["{topic}"]:::subNode')
        if idx <= len(key_points):
            clean_kp = re.sub(r'["\']', '', key_points[idx - 1])[:55] + "..."
            mermaid_lines.append(f'  Sub{idx} --> D{idx}["{clean_kp}"]:::detailNode')

    infographic_mermaid = "\n".join(mermaid_lines)
    summary_words = len(summary_text.split())
    compression = round((1.0 - (summary_words / max(1, total_words))) * 100, 1)

    return {
        "summary": summary_text,
        "key_points": key_points,
        "keywords": top_keywords,
        "stats": {
            "word_count": total_words,
            "summary_word_count": summary_words,
            "sentence_count": len(sentences),
            "reading_time_min": max(1, round(total_words / 200, 1)),
            "compression_ratio": f"{compression}% reduction"
        },
        "infographic_mermaid": infographic_mermaid,
        "algorithm_info": {
            "name": "TextRank Graph-Based Ranking Algorithm",
            "paper": "TextRank: Bringing Order into Texts",
            "authors": "Rada Mihalcea and Paul Tarau (EMNLP 2004)",
            "ieee_reference": "M. S. Joshi, K. S. Babu, and B. S. Rao, 'An Enhanced TextRank Algorithm for Automated Text Summarization,' 2020 IEEE 5th ICCCA, pp. 782-786, doi: 10.1109/ICCCA49541.2020.9250810."
        }
    }

if __name__ == '__main__':
    sample = """
    India's space agency ISRO has achieved a landmark milestone with the successful landing of the Chandrayaan-3 mission near the lunar South Pole.
    The spacecraft landed softly on August 23, making India the fourth country to achieve a soft lunar landing and the very first to touch down near the rugged south polar region.
    The mission consisted of the Vikram lander and the Pragyan rover, which deployed instruments to analyze lunar soil and sub-surface temperature gradients.
    Scientists confirmed that the rover discovered traces of sulfur, oxygen, iron, and titanium on the lunar regolith.
    Global space agencies including NASA and ESA commended the cost-effective engineering and precision navigation of ISRO.
    This achievement marks a new era in space exploration and accelerates international interest in future Artemis expeditions and lunar resource utilization.
    """
    res = textrank_summarize(sample)
    print("SUMMARY:\n", res['summary'])
    print("\nKEYWORDS:", res['keywords'])
    print("\nMERMAID:\n", res['infographic_mermaid'])
