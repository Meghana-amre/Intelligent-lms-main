"""Deterministic local generators for expanding the LMS question bank."""

import hashlib
import random

DSA_APTITUDE_TOPICS = (
    'Arrays',
    'Strings',
    'Linked Lists',
    'Stacks',
    'Queues',
    'Hash Maps',
    'Searching',
    'Sorting',
    'Trees',
    'Graphs',
)


def _shuffle_options(options, answer, seed_text):
    correct_index = ord(answer.upper()) - ord('A')
    indexed_options = list(enumerate(str(option) for option in options))
    seed = int.from_bytes(hashlib.sha256(seed_text.encode('utf-8')).digest(), 'big')
    random.Random(seed).shuffle(indexed_options)
    shuffled_options = [option for _, option in indexed_options]
    shuffled_answer = chr(ord('A') + next(
        index for index, (original_index, _) in enumerate(indexed_options)
        if original_index == correct_index
    ))
    return shuffled_options, shuffled_answer


def _question(category, subject, topic, text, options, answer, explanation, difficulty='Medium', exam=None):
    shuffled_options, shuffled_answer = _shuffle_options(options, answer, text)
    return {
        'category': category,
        'subject': subject,
        'exam': exam,
        'topic': topic,
        'question': text,
        'option_a': shuffled_options[0],
        'option_b': shuffled_options[1],
        'option_c': shuffled_options[2],
        'option_d': shuffled_options[3],
        'correct_answer': shuffled_answer,
        'explanation': explanation,
        'difficulty': difficulty,
    }


def _numeric_options(answer):
    distractors = []
    for value in (answer + 2, answer - 1, answer + 5, answer * 2, answer + 1):
        if value != answer and value not in distractors:
            distractors.append(value)
        if len(distractors) == 3:
            break
    return [answer, *distractors]


def _exam_candidates(category, subject):
    questions = []

    if subject == 'CET':
        for value in range(2, 92):
            speed = value + 3
            distance = speed * (value + 1)
            questions.append(_question(
                category, 'Physics', 'Motion',
                f'A vehicle travels {distance} km in {value + 1} hours. What is its average speed?',
                _numeric_options(speed), 'A',
                f'Average speed = distance / time = {distance} / {value + 1} = {speed} km/h.',
                exam=subject,
            ))

            amount = value
            molar_mass = value + 4
            sample_mass = amount * molar_mass
            questions.append(_question(
                category, 'Chemistry', 'Mole Concept',
                f'How many grams are present in {amount} mol of a compound whose molar mass is {molar_mass} g/mol?',
                _numeric_options(sample_mass), 'A',
                f'Mass = amount × molar mass = {amount} × {molar_mass} = {sample_mass} g.',
                exam=subject,
            ))

            x_value = value + 2
            questions.append(_question(
                category, 'Mathematics', 'Algebra',
                f'Solve 2x + {x_value} = {3 * x_value} for x.',
                _numeric_options(x_value), 'A',
                f'Subtracting {x_value} leaves 2x = {2 * x_value}; therefore x = {x_value}.',
                exam=subject,
            ))

    elif subject == 'JEE':
        concepts = [
            ('Electrostatics', 'What is the net electric field inside a conductor in electrostatic equilibrium?', ('Zero', 'Uniform and non-zero', 'Infinite', 'Equal to the surface field'), 'A', 'Free charges rearrange until the electric field inside the conductor is zero.'),
            ('Mechanics', 'For a projectile launched and landing at the same height, when is its vertical velocity zero?', ('At the highest point', 'At launch only', 'Immediately before landing', 'Throughout the flight'), 'A', 'The vertical component of velocity is zero momentarily at the trajectory’s highest point.'),
            ('Organic Chemistry', 'Which reagent is commonly used to distinguish an aldehyde from a ketone by oxidation?', ('Tollens’ reagent', 'Sodium chloride solution', 'Bromine water only', 'Dilute sodium hydroxide'), 'A', 'Aldehydes reduce Tollens’ reagent to give a silver mirror; ordinary ketones do not.'),
            ('Chemical Bonding', 'What is the molecular geometry of methane, CH₄?', ('Tetrahedral', 'Trigonal planar', 'Linear', 'Bent'), 'A', 'Four bonding pairs around carbon arrange tetrahedrally to minimize repulsion.'),
            ('Calculus', 'What is the derivative of sin(x) with respect to x?', ('cos(x)', '−cos(x)', 'sin(x)', '−sin(x)'), 'A', 'The derivative of sin(x) is cos(x).'),
            ('Complex Numbers', 'What is the modulus of 3 + 4i?', ('5', '7', '1', '25'), 'A', 'The modulus is √(3² + 4²) = 5.'),
            ('Thermodynamics', 'In an isothermal process for an ideal gas, which quantity remains constant?', ('Temperature', 'Pressure', 'Volume', 'Internal energy for every gas'), 'A', 'Isothermal means the temperature is held constant.'),
            ('Chemical Equilibrium', 'For a catalyst-assisted reversible reaction at equilibrium, what changes?', ('The rate of reaching equilibrium, not its position', 'The equilibrium constant', 'The final product ratio', 'The reaction enthalpy'), 'A', 'A catalyst speeds both directions and does not change the equilibrium constant or position.'),
        ]
        questions.extend(
            _question(
                category,
                'Physics' if topic in {'Electrostatics', 'Mechanics', 'Thermodynamics'} else
                'Chemistry' if topic in {'Organic Chemistry', 'Chemical Bonding', 'Chemical Equilibrium'} else
                'Mathematics',
                topic, text, options, answer, explanation, 'Medium', exam=subject
            )
            for topic, text, options, answer, explanation in concepts
        )

        for value in range(2, 92):
            initial_speed = value + 2
            acceleration = value
            time = value + 1
            final_speed = initial_speed + acceleration * time
            questions.append(_question(
                category, 'Physics', 'Kinematics',
                f'A particle starts at {initial_speed} m/s and accelerates at {acceleration} m/s² for {time} s. Find its final speed.',
                _numeric_options(final_speed), 'A',
                f'Using v = u + at gives {initial_speed} + {acceleration} × {time} = {final_speed} m/s.',
                'Hard',
                exam=subject,
            ))

            amount = value
            molar_mass = value + 4
            sample_mass = amount * molar_mass
            questions.append(_question(
                category, 'Chemistry', 'Mole Concept',
                f'For a compound with molar mass {molar_mass} g/mol, calculate the mass of a {amount} mol sample.',
                _numeric_options(sample_mass), 'A',
                f'Mass = amount × molar mass = {amount} × {molar_mass} = {sample_mass} g.',
                exam=subject,
            ))

            coefficient = value + 1
            root = value + 2
            constant = coefficient * root
            questions.append(_question(
                category, 'Mathematics', 'Algebra',
                f'If {coefficient}x = {constant}, what is the value of x?',
                _numeric_options(root), 'A',
                f'Dividing both sides by {coefficient} gives x = {root}.',
                exam=subject,
            ))

    elif subject == 'DSA Aptitude':
        templates = {
            'Arrays': [
                ('What is the time complexity of reading an array value at a known index in an array of {size} values?', ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)'), 'Array indexing accesses a known position directly.'),
                ('A linear scan may inspect all {size} array values. What is its worst-case time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n²)'), 'A linear scan can visit every element once.'),
                ('Inserting at the start of an array with {size} elements requires shifting later values. What is the time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'The existing values may all need to shift one position.'),
                ('Removing the first item from an array of {size} elements requires closing the gap. What is the time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'After removal, the remaining elements may need to shift.'),
                ('A loop visits each of the {size} array elements once. What is its time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n²)'), 'One constant-time visit per element gives linear time.'),
            ],
            'Strings': [
                ('A routine scans all {size} characters of a string once to count vowels. What is its time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n²)'), 'Each character is checked once.'),
                ('A mutable character array of length {size} is reversed using two pointers. What is the time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n²)'), 'The two pointers swap each character at most once.'),
                ('A palindrome check compares characters from both ends of a string of length {size}. What is the worst-case time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n²)'), 'At most half the characters are compared, which is linear time.'),
                ('Two strings of length {size} are compared character by character. What is the worst-case time complexity?', ('O(n)', 'O(1)', 'O(log n)', 'O(n²)'), 'The comparison may examine every character.'),
                ('KMP searches a pattern of length {size} in a text of length {size} + 1. What is its time complexity?', ('O(n + m)', 'O(nm)', 'O(1)', 'O(n² log n)'), 'KMP preprocesses the pattern and scans the text in linear time.'),
            ],
            'Linked Lists': [
                ('What is the time complexity of accessing the item at position {size} in a singly linked list from its head?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'Nodes must be followed sequentially from the head.'),
                ('A pointer to the head is available. What is the time complexity of inserting a new node at the head of a linked list with {size} nodes?', ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)'), 'Only the new node link and head pointer need updating.'),
                ('What is the worst-case time complexity of searching for a value in a linked list with {size} nodes?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'The value may be in the last node or absent.'),
                ('Floyd’s cycle-detection algorithm processes a linked list of {size} nodes. What is its extra-space complexity?', ('O(1)', 'O(log n)', 'O(n)', 'O(n²)'), 'It uses two pointers and no collection proportional to the list length.'),
                ('A linked list has {size} nodes. What is the time complexity of finding its tail when starting at the head?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'Without a tail pointer, traversal continues node by node.'),
            ],
            'Stacks': [
                ('A fixed-capacity stack contains {size} items. What is the time complexity of pushing one item when space is available?', ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)'), 'A push updates the top position and stores one item.'),
                ('A stack contains {size} items. What is the time complexity of popping its top item?', ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)'), 'A pop removes the item at the top directly.'),
                ('Which access order does a stack with {size} stored items follow?', ('Last in, first out', 'First in, first out', 'Smallest in, first out', 'Random in, first out'), 'A stack removes the most recently added item first.'),
                ('Which structure is commonly used to check whether {size} opening and closing brackets are properly nested?', ('Stack', 'Queue', 'Hash map only', 'Binary search tree'), 'A stack tracks the most recent unmatched opening bracket.'),
                ('A depth-first traversal stores up to {size} pending vertices explicitly. Which structure is typically used?', ('Stack', 'Queue', 'Heap', 'Hash map'), 'Depth-first traversal uses a stack, either explicitly or through recursion.'),
            ],
            'Queues': [
                ('Which access order does a queue containing {size} items follow?', ('First in, first out', 'Last in, first out', 'Largest in, first out', 'Random in, first out'), 'A queue removes items in the order they were added.'),
                ('A linked queue with head and tail pointers contains {size} items. What is the time complexity of enqueue?', ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)'), 'The tail pointer allows the new item to be appended directly.'),
                ('A linked queue with a head pointer contains {size} items. What is the time complexity of dequeue?', ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)'), 'Dequeue advances the head pointer to the next node.'),
                ('Which structure does breadth-first search use to process vertices by distance from the source in a graph of {size} vertices?', ('Queue', 'Stack', 'Sorted array', 'Recursion only'), 'A queue processes discovered vertices in FIFO order.'),
                ('In a circular queue of capacity {size} that reserves one slot to distinguish full from empty, when is it full?', ('The next rear position equals front', 'Rear equals front in every case', 'Front is always zero', 'The queue has one item'), 'The queue is full when advancing rear would meet front.'),
            ],
            'Hash Maps': [
                ('Two different keys among {size} stored entries map to the same hash-table slot. What is this called?', ('A collision', 'A rotation', 'A traversal', 'An underflow'), 'A collision occurs when distinct keys map to the same slot.'),
                ('Under uniform hashing, what is the expected lookup time in a hash map with {size} entries?', ('O(1)', 'O(log n)', 'O(n)', 'O(n log n)'), 'With a suitable hash function, the expected number of probes is constant.'),
                ('Which method stores multiple colliding keys in a list at a hash-table slot for a map with {size} entries?', ('Separate chaining', 'Binary search', 'Tree rotation', 'Linear probing only'), 'Separate chaining keeps a collection of entries at each slot.'),
                ('A hash table has {size} stored entries and {size} slots. What is its load factor?', ('1', '0', '{size}', '0.5'), 'Load factor is entries divided by slots, so {size}/{size} equals 1.'),
                ('If all {size} keys collide in one hash-table bucket, what can worst-case lookup time become?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'A lookup may need to inspect every key in the bucket.'),
            ],
            'Searching': [
                ('What must be true of the data before standard binary search can be used on {size} values?', ('The values are sorted', 'The values are all distinct', 'The values are positive', 'The values form a tree'), 'Binary search relies on sorted order to discard half the range.'),
                ('What is the time complexity of binary search on {size} sorted values?', ('O(log n)', 'O(1)', 'O(n)', 'O(n log n)'), 'Each comparison halves the remaining search interval.'),
                ('What is the best-case time complexity of linear search on {size} values when the target is first?', ('O(1)', 'O(log n)', 'O(n)', 'O(n²)'), 'The first comparison finds the target immediately.'),
                ('What is the worst-case time complexity of linear search when looking for a value among {size} items?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'The search may inspect every item.'),
                ('After one binary-search comparison, at most what fraction of a sorted range of {size} values remains?', ('One half', 'All of it', 'One quarter', 'Two thirds'), 'Binary search discards one half of the current interval per comparison.'),
            ],
            'Sorting': [
                ('What is the worst-case time complexity of merge sort on {size} values?', ('O(n log n)', 'O(n)', 'O(n²)', 'O(log n)'), 'Merge sort splits into levels and merges all values at each level.'),
                ('What is the best-case time complexity of insertion sort on an already sorted list of {size} values?', ('O(n)', 'O(1)', 'O(log n)', 'O(n²)'), 'Each item needs only a constant check as the list is traversed once.'),
                ('What is the worst-case time complexity of bubble sort on {size} values?', ('O(n²)', 'O(n)', 'O(log n)', 'O(n log n)'), 'Repeated passes compare pairs across the list.'),
                ('Which property does stable sorting preserve when equal keys appear among {size} records?', ('Their original relative order', 'Their numeric values change', 'The list becomes reversed', 'Every key becomes unique'), 'A stable sort keeps equal-key records in their original relative order.'),
                ('What is quicksort’s worst-case time complexity when sorting {size} values with consistently unbalanced partitions?', ('O(n²)', 'O(n)', 'O(log n)', 'O(n log n)'), 'Unbalanced partitions can require a quadratic number of comparisons.'),
            ],
            'Trees': [
                ('Which traversal visits keys in sorted order in a binary search tree containing {size} keys?', ('Inorder', 'Preorder', 'Postorder', 'Level order'), 'Inorder visits left subtree, node, then right subtree.'),
                ('What is the search time complexity in a balanced binary search tree with {size} nodes?', ('O(log n)', 'O(1)', 'O(n)', 'O(n log n)'), 'A balanced tree reduces the remaining search subtree by height.'),
                ('Which data structure is typically used for level-order traversal of a tree with {size} nodes?', ('Queue', 'Stack', 'Hash map', 'Sorted array'), 'Level-order traversal processes nodes breadth first using a queue.'),
                ('A full binary tree has {size} internal nodes. How many leaves does it have?', ('{size} + 1', '{size}', '2 × {size}', '{size} − 1'), 'In a full binary tree, the number of leaves is one greater than the internal-node count.'),
                ('What is the worst-case search time in a completely skewed binary search tree with {size} nodes?', ('O(n)', 'O(1)', 'O(log n)', 'O(n log n)'), 'A skewed tree can have height proportional to its number of nodes.'),
            ],
            'Graphs': [
                ('Which traversal finds shortest paths by edge count from a source in an unweighted graph of {size} vertices?', ('Breadth-first search', 'Depth-first search', 'Inorder traversal', 'Heap sort'), 'BFS visits vertices in increasing distance from the source.'),
                ('Which traversal explores a graph of {size} vertices by following a path before backtracking?', ('Depth-first search', 'Breadth-first search', 'Binary search', 'Merge sort'), 'DFS follows a path deeply before exploring alternatives.'),
                ('In an undirected graph with {size} edges, what is the sum of all vertex degrees?', ('2 × {size}', '{size}', '{size} + 1', '{size} − 1'), 'Each undirected edge contributes one degree to each endpoint.'),
                ('What is the space complexity of an adjacency-list representation of a graph with {size} vertices and {size} edges?', ('O(V + E)', 'O(V²)', 'O(E²)', 'O(1)'), 'Adjacency lists store vertices and their incident edges.'),
                ('Which shortest-path algorithm supports negative edge weights when no reachable negative cycle exists in a graph of {size} vertices?', ('Bellman-Ford', 'Dijkstra', 'Prim', 'Kruskal'), 'Bellman-Ford supports negative edges and detects reachable negative cycles.'),
            ],
        }
        for size in range(2, 32):
            for topic in DSA_APTITUDE_TOPICS:
                for text, options, explanation in templates[topic]:
                    formatted_text = text.format(size=size)
                    formatted_options = tuple(option.format(size=size) for option in options)
                    questions.append(_question(
                        category, topic, topic, formatted_text, formatted_options, 'A',
                        explanation.format(size=size), 'Medium', exam=subject,
                    ))

    return questions


def _general_candidates(category):
    subject = 'Math' if category == 'highschool' else 'Algorithms'
    questions = []
    for value in range(2, 120):
        total = value * 4
        questions.append(_question(
            category, subject, 'Arithmetic',
            f'A library has {value} shelves with 4 books on each shelf. How many books are there?',
            _numeric_options(total), 'A',
            f'{value} × 4 = {total} books.',
            'Easy',
        ))
        difference = value * 3
        questions.append(_question(
            category, subject, 'Arithmetic',
            f'A runner completes {value * 5} laps and then runs {difference} fewer laps the next day. How many laps are run the next day?',
            _numeric_options(value * 2), 'A',
            f'{value * 5} − {difference} = {value * 2} laps.',
            'Easy',
        ))
    return questions


def generate_additional_questions(
    category,
    existing_questions,
    target_count,
    subject=None,
    required_subject_counts=None,
    required_topic_counts=None,
):
    """Generate distinct academic MCQs without adding question-index text."""
    existing_text = {
        item['question'].strip().casefold()
        for item in existing_questions
    }
    candidates = (
        _exam_candidates(category, subject)
        if category == 'puc_degree' and subject in {'CET', 'JEE', 'DSA Aptitude'}
        else _general_candidates(category)
    )
    generated = []
    target_additions = max(0, target_count - len(existing_questions))

    for question in candidates:
        key = question['question'].strip().casefold()
        if key in existing_text:
            continue
        if required_subject_counts is not None:
            subject_needed = required_subject_counts.get(question['subject'], 0)
            if subject_needed <= 0:
                continue
            required_subject_counts[question['subject']] = subject_needed - 1
        if required_topic_counts is not None:
            topic_needed = required_topic_counts.get(question['topic'], 0)
            if topic_needed <= 0:
                continue
            required_topic_counts[question['topic']] = topic_needed - 1
        existing_text.add(key)
        generated.append(question)
        if len(generated) >= target_additions:
            break

    if required_subject_counts is not None and any(required_subject_counts.values()):
        raise ValueError('Not enough unique generated questions to fill each requested subject section.')
    if required_topic_counts is not None and any(required_topic_counts.values()):
        raise ValueError('Not enough unique generated questions to fill each requested topic section.')

    return generated
