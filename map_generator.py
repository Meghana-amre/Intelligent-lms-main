import re

def sanitize_label(text, max_chars=40):
    """Sanitizes text for Mermaid node labels by removing special characters and trimming length."""
    text = re.sub(r'[\(\)\[\]\{\}\"\';:<>]', '', text).strip()
    if len(text) > max_chars:
        return text[:max_chars].strip() + "..."
    return text

def detect_theory_type(text):
    """
    Analyzes theory content using NLP pattern markers to classify structure:
    1. 'process' -> Step-by-step Flowchart
    2. 'hierarchy' -> Hierarchical Taxonomy Concept Map
    3. 'relational' -> Cause-and-Effect Relationship Graph
    4. 'mindmap' -> Multi-branching Mind Map
    """
    text_lower = text.lower()

    process_keywords = [
        "step", "first", "second", "then", "after", "finally", "next", "subsequently",
        "phase", "stage", "process", "cycle", "procedure", "leads to", "produces", "converts"
    ]
    hierarchy_keywords = [
        "types of", "classified into", "categories", "categorized", "branches", "levels",
        "subtypes", "consists of", "divided into", "hierarchy", "taxonomy", "classes", "forms of"
    ]
    relational_keywords = [
        "causes", "results in", "affects", "influences", "depends on", "interacts with",
        "impacts", "triggers", "connects to", "relationship", "due to", "stimulates"
    ]

    process_score = sum(1 for kw in process_keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
    hierarchy_score = sum(1 for kw in hierarchy_keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))
    relational_score = sum(1 for kw in relational_keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_lower))

    # Also check if text has numbered items like "1.", "2.", "Step 1"
    if re.search(r'(?:step\s*\d|\b\d+\.|\bstage\s*\d)', text_lower):
        process_score += 3

    scores = {
        'process': process_score,
        'hierarchy': hierarchy_score,
        'relational': relational_score,
        'mindmap': 1 # Baseline default
    }

    best_type = max(scores, key=scores.get)
    # If all low or tied with baseline, select mindmap
    if scores[best_type] <= 1:
        best_type = 'mindmap'

    return best_type

def generate_visual_map(theory_text):
    """
    Transforms arbitrary theory content into an optimized visual diagram.
    Adapts layout dynamically based on linguistic analysis.
    """
    cleaned = theory_text.strip()
    if not cleaned:
        return {
            "layout_type": "Empty",
            "diagram_code": "graph TD;\n  Empty[Please enter theory text to generate a map]"
        }

    layout_type = detect_theory_type(cleaned)
    lines = [line.strip() for line in cleaned.split('\n') if len(line.strip()) > 3]

    # Split into sentences or clauses
    raw_sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 10]

    # Extract central topic from first line or first sentence
    first_chunk = lines[0] if lines else sentences[0]
    topic_match = re.search(r'^#*\s*(?:the\s+)?([a-zA-Z0-9\s]{3,35})(?:is|are|:|--|\n|\.)', first_chunk, re.IGNORECASE)
    if topic_match:
        main_topic = sanitize_label(topic_match.group(1).title(), max_chars=30)
    else:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', first_chunk)
        main_topic = sanitize_label(" ".join(words[:3]).title(), max_chars=30) if words else "Core Concept"

    if layout_type == 'process':
        # PROCESS FLOWCHART (graph TD with sequential blocks)
        mermaid = ["graph TD", "  %% Process Flowchart Layout"]
        mermaid.append("  classDef startNode fill:#4338ca,stroke:#312e81,stroke-width:2px,color:#fff,font-weight:bold,rx:8px;")
        mermaid.append("  classDef stepNode fill:#0284c7,stroke:#0369a1,stroke-width:1px,color:#fff,rx:6px;")
        mermaid.append("  classDef endNode fill:#059669,stroke:#047857,stroke-width:2px,color:#fff,font-weight:bold,rx:8px;")

        # Extract steps from numbered lines or sequential sentences
        steps = []
        for line in lines:
            if re.match(r'^(?:\d+\.|step\s*\d|stage\s*\d|phase\s*\d|[-*])', line, re.IGNORECASE):
                cleaned_line = re.sub(r'^(?:\d+\.|step\s*\d:?|stage\s*\d:?|phase\s*\d:?|[-*])\s*', '', line, flags=re.IGNORECASE)
                steps.append(sanitize_label(cleaned_line, max_chars=45))

        if not steps:
            for s in sentences[:6]:
                steps.append(sanitize_label(s, max_chars=45))

        mermaid.append(f'  Start["Start: {main_topic}"]:::startNode')
        prev_node = "Start"

        for idx, step in enumerate(steps, start=1):
            curr_node = f"Step{idx}"
            mermaid.append(f'  {curr_node}["Step {idx}: {step}"]:::stepNode')
            mermaid.append(f'  {prev_node} --> {curr_node}')
            prev_node = curr_node

        mermaid.append(f'  End["Completed: {main_topic}"]:::endNode')
        mermaid.append(f'  {prev_node} --> End')

        return {
            "layout_type": "Step-by-Step Process Flowchart",
            "detected_pattern": "Sequential & Procedural Transitions",
            "diagram_code": "\n".join(mermaid)
        }

    elif layout_type == 'hierarchy':
        # HIERARCHICAL CONCEPT MAP (graph TD with multi-level category trees)
        mermaid = ["graph TD", "  %% Hierarchical Concept Map Layout"]
        mermaid.append("  classDef rootNode fill:#7c3aed,stroke:#5b21b6,stroke-width:2px,color:#fff,font-weight:bold,rx:10px;")
        mermaid.append("  classDef catNode fill:#2563eb,stroke:#1d4ed8,stroke-width:1px,color:#fff,rx:6px;")
        mermaid.append("  classDef subNode fill:#0d9488,stroke:#0f766e,stroke-width:1px,color:#fff,rx:4px;")

        mermaid.append(f'  Root["{main_topic}"]:::rootNode')

        # Find category bullet points or classification clauses
        categories = []
        for line in lines[1:]:
            if re.match(r'^(?:[-*•]|\d+\.)', line):
                item = re.sub(r'^(?:[-*•]|\d+\.)\s*', '', line)
                categories.append(item)

        if not categories:
            categories = sentences[1:6] if len(sentences) > 1 else ["Component A", "Component B", "Component C"]

        for idx, cat in enumerate(categories[:5], start=1):
            parts = cat.split(':')
            if len(parts) > 1:
                cat_title = sanitize_label(parts[0], max_chars=25)
                cat_desc = sanitize_label(parts[1], max_chars=35)
                mermaid.append(f'  Cat{idx}["{cat_title}"]:::catNode')
                mermaid.append(f'  Root --> Cat{idx}')
                mermaid.append(f'  Detail{idx}["{cat_desc}"]:::subNode')
                mermaid.append(f'  Cat{idx} --> Detail{idx}')
            else:
                cat_title = sanitize_label(cat, max_chars=35)
                mermaid.append(f'  Cat{idx}["{cat_title}"]:::catNode')
                mermaid.append(f'  Root --> Cat{idx}')

        return {
            "layout_type": "Hierarchical Concept Map",
            "detected_pattern": "Taxonomy, Classifications & Categorical Subdivisions",
            "diagram_code": "\n".join(mermaid)
        }

    elif layout_type == 'relational':
        # RELATIONSHIP CONCEPT MAP (graph LR with directional relational labels)
        mermaid = ["graph LR", "  %% Relational Concept Map"]
        mermaid.append("  classDef entityNode fill:#db2777,stroke:#9d174d,stroke-width:2px,color:#fff,font-weight:bold,rx:8px;")
        mermaid.append("  classDef targetNode fill:#4f46e5,stroke:#3730a3,stroke-width:1px,color:#fff,rx:6px;")

        mermaid.append(f'  Core["{main_topic}"]:::entityNode')

        rel_sentences = sentences[:5]
        for idx, s in enumerate(rel_sentences, start=1):
            short_s = sanitize_label(s, max_chars=40)
            relation_label = "influences"
            for kw in ["causes", "leads to", "produces", "affects", "depends on"]:
                if kw in s.lower():
                    relation_label = kw
                    break
            mermaid.append(f'  Node{idx}["{short_s}"]:::targetNode')
            mermaid.append(f'  Core -- "{relation_label}" --> Node{idx}')

        return {
            "layout_type": "Relationship Concept Graph",
            "detected_pattern": "Cause-and-Effect & Conceptual Interactions",
            "diagram_code": "\n".join(mermaid)
        }

    else:
        # BRANCHING MIND MAP (Native Mermaid mindmap syntax)
        mermaid = ["mindmap", f'  root(({main_topic}))']

        branches = []
        for line in lines[1:]:
            branch_text = re.sub(r'^(?:[-*•]|\d+\.)\s*', '', line)
            if not branch_text:
                continue

            parts = branch_text.split(':', 1)
            branch_name = sanitize_label(parts[0], max_chars=35)
            branch_detail = sanitize_label(parts[1], max_chars=45) if len(parts) > 1 else None
            branches.append((branch_name, branch_detail))

        if not branches:
            branches = [(sanitize_label(s, max_chars=35), None) for s in sentences[1:6]]

        for branch_name, branch_detail in branches[:6]:
            if branch_name:
                mermaid.append(f'    {branch_name}')
            if branch_name and branch_detail:
                mermaid.append(f'      {branch_detail}')

        return {
            "layout_type": "Branching Mind Map",
            "detected_pattern": "Multifaceted Conceptual Association",
            "diagram_code": "\n".join(mermaid)
        }

if __name__ == '__main__':
    theory1 = """
    Water Cycle Process:
    Step 1: Evaporation of water from oceans due to solar heat.
    Step 2: Condensation of water vapor into clouds in the upper atmosphere.
    Step 3: Precipitation returns water to the ground as rain or snow.
    Step 4: Collection of runoff into rivers and groundwater reservoirs.
    """
    res1 = generate_visual_map(theory1)
    print("THEORY 1 (Process):", res1['layout_type'])
    print(res1['diagram_code'])
    print("-" * 50)

    theory2 = """
    Types of Machine Learning:
    - Supervised Learning: Algorithms trained on labeled datasets.
    - Unsupervised Learning: Discovering hidden patterns in unlabeled data.
    - Reinforcement Learning: Agents learning through rewards and penalties.
    """
    res2 = generate_visual_map(theory2)
    print("THEORY 2 (Hierarchy):", res2['layout_type'])
    print(res2['diagram_code'])
