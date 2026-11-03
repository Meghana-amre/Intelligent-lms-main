import json
import sqlite3
from database import get_db_connection, init_db

# -------------------------------------------------------------
# HIGH SCHOOL QUESTION BANK (Covering 8 Subjects)
# -------------------------------------------------------------
HIGH_SCHOOL_QUESTIONS = [
    # BIOLOGY
    {
        "category": "highschool", "subject": "Biology", "topic": "Human Circulatory System",
        "question": "Which chamber of the human heart receives oxygenated blood directly from the lungs via pulmonary veins?",
        "option_a": "Right Atrium", "option_b": "Left Atrium", "option_c": "Right Ventricle", "option_d": "Left Ventricle",
        "correct_answer": "B",
        "explanation": "The left atrium receives oxygen-rich blood from the lungs through the four pulmonary veins before pumping it to the left ventricle.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Cell Biology",
        "question": "Which cell organelle is famously known as the 'Powerhouse of the Cell' because it produces ATP?",
        "option_a": "Ribosome", "option_b": "Endoplasmic Reticulum", "option_c": "Mitochondria", "option_d": "Golgi Apparatus",
        "correct_answer": "C",
        "explanation": "Mitochondria synthesize adenosine triphosphate (ATP) through cellular respiration, supplying energy for cellular activities.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Plant Physiology",
        "question": "What is the green pigment responsible for absorbing sunlight during photosynthesis in plant leaves?",
        "option_a": "Carotenoid", "option_b": "Chlorophyll", "option_c": "Anthocyanin", "option_d": "Xanthophyll",
        "correct_answer": "B",
        "explanation": "Chlorophyll located inside chloroplasts absorbs red and blue light waves while reflecting green light.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Human Nervous System",
        "question": "Which part of the human brain controls involuntary life-support functions such as breathing and heartbeat?",
        "option_a": "Cerebrum", "option_b": "Cerebellum", "option_c": "Medulla Oblongata", "option_d": "Hypothalamus",
        "correct_answer": "C",
        "explanation": "The medulla oblongata, located in the lower brainstem, governs autonomic reflexes like cardiac rhythm and respiration.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Genetics",
        "question": "Who is universally recognized as the 'Father of Modern Genetics' for his pea plant experiments?",
        "option_a": "Gregor Mendel", "option_b": "Charles Darwin", "option_c": "Louis Pasteur", "option_d": "Robert Hooke",
        "correct_answer": "A",
        "explanation": "Gregor Mendel discovered the fundamental laws of biological inheritance through systematic pea plant breeding trials.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Digestive System",
        "question": "Which enzyme present in human saliva begins the chemical digestion of dietary starch into maltose?",
        "option_a": "Pepsin", "option_b": "Salivary Amylase (Ptyalin)", "option_c": "Lipase", "option_d": "Trypsin",
        "correct_answer": "B",
        "explanation": "Salivary amylase breaks down complex starch polysaccharides into simpler disaccharides like maltose.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Circulatory System",
        "question": "What component of human blood is primarily tasked with clotting to prevent excessive hemorrhage?",
        "option_a": "Erythrocytes (RBCs)", "option_b": "Leukocytes (WBCs)", "option_c": "Platelets (Thrombocytes)", "option_d": "Blood Plasma",
        "correct_answer": "C",
        "explanation": "Platelets aggregate at vascular injury sites and initiate the biochemical cascade leading to fibrin clot formation.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Excretory System",
        "question": "What is the structural and functional microscopic filtration unit of the mammalian kidney?",
        "option_a": "Neuron", "option_b": "Nephron", "option_c": "Alveolus", "option_d": "Villus",
        "correct_answer": "B",
        "explanation": "Nephrons filter blood, selectively reabsorb nutrients and water, and produce urine in the kidneys.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Ecology",
        "question": "Organisms that manufacture their own organic nutrients from inorganic substances via photosynthesis are called:",
        "option_a": "Heterotrophs", "option_b": "Autotrophs", "option_c": "Decomposers", "option_d": "Detritivores",
        "correct_answer": "B",
        "explanation": "Autotrophs (producers like green plants and cyanobacteria) synthesize organic compounds from CO2 and water using sunlight.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Biology", "topic": "Endocrine System",
        "question": "Which endocrine hormone, secreted by the pancreas, regulates glucose uptake and reduces blood sugar levels?",
        "option_a": "Glucagon", "option_b": "Adrenaline", "option_c": "Insulin", "option_d": "Thyroxine",
        "correct_answer": "C",
        "explanation": "Beta cells of pancreatic islets secrete insulin, facilitating glucose absorption into skeletal muscle and liver cells.",
        "difficulty": "Easy"
    },

    # SCIENCE (PHYSICS & CHEMISTRY)
    {
        "category": "highschool", "subject": "Science", "topic": "Physics - Mechanics",
        "question": "According to Newton's Second Law of Motion, force is defined mathematically as:",
        "option_a": "Mass divided by Acceleration", "option_b": "Mass multiplied by Acceleration", "option_c": "Velocity multiplied by Time", "option_d": "Work done per unit Time",
        "correct_answer": "B",
        "explanation": "Newton's Second Law states F = m * a (Force equals mass times acceleration).",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Chemistry - Acids & Bases",
        "question": "What is the pH value of pure neutral distilled water at 25 degrees Celsius?",
        "option_a": "0", "option_b": "7", "option_c": "14", "option_d": "5.5",
        "correct_answer": "B",
        "explanation": "On the pH scale, values below 7 are acidic, above 7 are basic, and exactly 7 represents neutrality.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Physics - Optics",
        "question": "The bending of a beam of light as it transitions from one optical medium into another of different density is called:",
        "option_a": "Reflection", "option_b": "Refraction", "option_c": "Dispersion", "option_d": "Diffraction",
        "correct_answer": "B",
        "explanation": "Refraction is the alteration of a wave's propagation speed and direction across an interface between two media.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Chemistry - Atomic Structure",
        "question": "Which subatomic particle possesses a negative electrostatic charge and orbits the atomic nucleus?",
        "option_a": "Proton", "option_b": "Neutron", "option_c": "Electron", "option_d": "Positron",
        "correct_answer": "C",
        "explanation": "Electrons are negatively charged particles that occupy atomic orbitals surrounding the positively charged nucleus.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Physics - Thermodynamics",
        "question": "The phase transition where a solid directly converts into a vapor without passing through the liquid phase is called:",
        "option_a": "Evaporation", "option_b": "Condensation", "option_c": "Sublimation", "option_d": "Solidification",
        "correct_answer": "C",
        "explanation": "Sublimation occurs when substances like dry ice (solid CO2) or camphor convert directly from solid to gas.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Physics - Electricity",
        "question": "Ohm's Law states that current (I) passing through a conductor between two points is proportional to:",
        "option_a": "Voltage (V)", "option_b": "Resistance squared", "option_c": "Magnetic field", "option_d": "Power (P)",
        "correct_answer": "A",
        "explanation": "Ohm's Law gives V = I * R, meaning current I is directly proportional to potential difference V across a constant resistor.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Chemistry - Elements",
        "question": "What is the chemical symbol for the precious metal Gold on the Periodic Table?",
        "option_a": "Ag", "option_b": "Au", "option_c": "Fe", "option_d": "Gd",
        "correct_answer": "B",
        "explanation": "Gold has the chemical symbol Au, derived from the Latin word 'Aurum' which means shining dawn.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Physics - Gravitation",
        "question": "What is the standard acceleration due to Earth's gravity (g) near sea level?",
        "option_a": "8.3 m/s²", "option_b": "9.8 m/s²", "option_c": "12.2 m/s²", "option_d": "6.67 m/s²",
        "correct_answer": "B",
        "explanation": "Standard acceleration due to Earth's gravity is approximately 9.80665 m/s² (commonly rounded to 9.8 m/s²).",
        "difficulty": "Easy"
    },

    # MATHEMATICS
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Algebra",
        "question": "Solve the linear equation for x: 3x - 7 = 14",
        "option_a": "x = 5", "option_b": "x = 7", "option_c": "x = 9", "option_d": "x = 6",
        "correct_answer": "B",
        "explanation": "3x = 14 + 7 = 21; therefore, x = 21 / 3 = 7.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Geometry",
        "question": "What is the sum of the interior angles of any planar triangle?",
        "option_a": "90 degrees", "option_b": "180 degrees", "option_c": "270 degrees", "option_d": "360 degrees",
        "correct_answer": "B",
        "explanation": "In Euclidean planar geometry, the three interior angles of every triangle invariably sum to 180 degrees.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Number Theory",
        "question": "What is the smallest prime number?",
        "option_a": "0", "option_b": "1", "option_c": "2", "option_d": "3",
        "correct_answer": "C",
        "explanation": "2 is the smallest prime number and the only even prime number in mathematics.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Trigonometry",
        "question": "In a right-angled triangle, the ratio of the side opposite to an acute angle to the hypotenuse is defined as:",
        "option_a": "Cosine", "option_b": "Sine", "option_c": "Tangent", "option_d": "Secant",
        "correct_answer": "B",
        "explanation": "By definition, Sine(theta) = Opposite Side / Hypotenuse.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Mensuration",
        "question": "What is the formula for calculating the area of a circle with radius r?",
        "option_a": "2 * π * r", "option_b": "π * r²", "option_c": "4/3 * π * r³", "option_d": "2 * π * r²",
        "correct_answer": "B",
        "explanation": "The planar area enclosed by a circle is π * r², while its circumference is 2 * π * r.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Arithmetic Progressions",
        "question": "Identify the next term in the arithmetic sequence: 4, 11, 18, 25, ...",
        "option_a": "31", "option_b": "32", "option_c": "34", "option_d": "35",
        "correct_answer": "B",
        "explanation": "The common difference d is (11 - 4) = 7. Thus, the next term is 25 + 7 = 32.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Probability",
        "question": "What is the probability of rolling an even number on a fair, standard six-sided die?",
        "option_a": "1/6", "option_b": "1/3", "option_c": "1/2", "option_d": "2/3",
        "correct_answer": "C",
        "explanation": "The even outcomes are {2, 4, 6} out of 6 total possibilities {1,2,3,4,5,6}. P = 3/6 = 1/2.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Quadratic Equations",
        "question": "What is the value of the discriminant (b² - 4ac) for the quadratic equation x² - 6x + 9 = 0?",
        "option_a": "-9", "option_b": "0", "option_c": "18", "option_d": "36",
        "correct_answer": "B",
        "explanation": "Here a=1, b=-6, c=9. Discriminant = (-6)² - 4(1)(9) = 36 - 36 = 0 (indicating real and equal roots).",
        "difficulty": "Medium"
    },

    # HISTORY
    {
        "category": "highschool", "subject": "History", "topic": "Indian Freedom Struggle",
        "question": "In which year did India attain independence from British colonial rule?",
        "option_a": "1942", "option_b": "1945", "option_c": "1947", "option_d": "1950",
        "correct_answer": "C",
        "explanation": "India officially gained sovereign independence on August 15, 1947.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "History", "topic": "Indian History",
        "question": "Who was the first female Prime Minister of sovereign India?",
        "option_a": "Sarojini Naidu", "option_b": "Indira Gandhi", "option_c": "Pratibha Patil", "option_d": "Sucheta Kripalani",
        "correct_answer": "B",
        "explanation": "Indira Gandhi served as India's prime minister from 1966 to 1977 and again from 1980 until 1984.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "History", "topic": "World History",
        "question": "The historic storming of the Bastille prison in 1789 triggered which epochal revolution?",
        "option_a": "American Revolution", "option_b": "French Revolution", "option_c": "Russian Revolution", "option_d": "Industrial Revolution",
        "correct_answer": "B",
        "explanation": "On July 14, 1789, Parisian revolutionaries stormed the Bastille fortress, inaugurating the French Revolution.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "History", "topic": "Ancient Civilizations",
        "question": "The Great Bath, an architectural wonder of ancient urban sanitation, was discovered at which Harappan site?",
        "option_a": "Lothal", "option_b": "Kalibangan", "option_c": "Mohenjo-daro", "option_d": "Dholavira",
        "correct_answer": "C",
        "explanation": "The Great Bath was excavated at Mohenjo-daro in Sindh, demonstrating sophisticated urban water management.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "History", "topic": "Mughal Empire",
        "question": "Which Mughal Emperor constructed the Taj Mahal in Agra as a memorial for his wife Mumtaz Mahal?",
        "option_a": "Akbar", "option_b": "Babur", "option_c": "Shah Jahan", "option_d": "Jahangir",
        "correct_answer": "C",
        "explanation": "Emperor Shah Jahan commissioned the white marble mausoleum Taj Mahal in 1632.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "History", "topic": "Modern History",
        "question": "The historic Dandi Salt March was launched by Mahatma Gandhi in which year?",
        "option_a": "1920", "option_b": "1930", "option_c": "1942", "option_d": "1919",
        "correct_answer": "B",
        "explanation": "Mahatma Gandhi embarked on the Dandi Salt March from Sabarmati Ashram in March 1930 as part of the Civil Disobedience Movement.",
        "difficulty": "Easy"
    },

    # GEOGRAPHY
    {
        "category": "highschool", "subject": "Geography", "topic": "Physical Geography",
        "question": "What is the highest mountain peak in the world above sea level?",
        "option_a": "Mount K2", "option_b": "Mount Kangchenjunga", "option_c": "Mount Everest", "option_d": "Mount Kilimanjaro",
        "correct_answer": "C",
        "explanation": "Mount Everest in the Himalayas stands at 8,848.86 meters above sea level.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Geography", "topic": "Hydrology",
        "question": "Which is the longest river in the world by continuous channel length?",
        "option_a": "Amazon River", "option_b": "Nile River", "option_c": "Yangtze River", "option_d": "Mississippi River",
        "correct_answer": "B",
        "explanation": "The Nile River in northeastern Africa flows approximately 6,650 kilometers.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Geography", "topic": "Atmospheric Science",
        "question": "Which layer of Earth's atmosphere contains the crucial ozone layer that shields against ultraviolet rays?",
        "option_a": "Troposphere", "option_b": "Stratosphere", "option_c": "Mesosphere", "option_d": "Thermosphere",
        "correct_answer": "B",
        "explanation": "The stratosphere houses the ozone layer (O3), absorbing harmful solar ultraviolet radiation.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Geography", "topic": "Indian Geography",
        "question": "Which Indian state has the longest mainland maritime coastline?",
        "option_a": "Maharashtra", "option_b": "Tamil Nadu", "option_c": "Gujarat", "option_d": "Andhra Pradesh",
        "correct_answer": "C",
        "explanation": "Gujarat boasts the longest coastline in India, extending over approximately 1,600 km.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Geography", "topic": "World Geography",
        "question": "The imaginary 0-degree line of latitude encircling the center of the Earth is called the:",
        "option_a": "Prime Meridian", "option_b": "Tropic of Cancer", "option_c": "Equator", "option_d": "International Date Line",
        "correct_answer": "C",
        "explanation": "The Equator divides Earth into Northern and Southern Hemispheres at latitude 0 degrees.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Geography", "topic": "Geomorphology",
        "question": "Which is the largest hot desert on Earth?",
        "option_a": "Gobi Desert", "option_b": "Thar Desert", "option_c": "Sahara Desert", "option_d": "Kalahari Desert",
        "correct_answer": "C",
        "explanation": "The Sahara Desert in North Africa spans over 9 million square kilometers, making it the largest hot desert.",
        "difficulty": "Easy"
    },

    # SOCIAL SCIENCE (CIVICS & ECONOMICS)
    {
        "category": "highschool", "subject": "Social Science", "topic": "Indian Polity",
        "question": "Who presided as the Chairman of the Drafting Committee of the Indian Constitution?",
        "option_a": "Dr. Rajendra Prasad", "option_b": "Dr. B. R. Ambedkar", "option_c": "Jawaharlal Nehru", "option_d": "Sardar Patel",
        "correct_answer": "B",
        "explanation": "Dr. Bhimrao Ramji Ambedkar served as the Chairman of the Constitution Drafting Committee.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Social Science", "topic": "Civics",
        "question": "What is the minimum voting age for an Indian citizen under the 61st Constitutional Amendment?",
        "option_a": "16 years", "option_b": "18 years", "option_c": "21 years", "option_d": "25 years",
        "correct_answer": "B",
        "explanation": "The 61st Amendment Act of 1988 lowered the universal adult suffrage age from 21 to 18 years.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Social Science", "topic": "Economics",
        "question": "The economic sector that encompasses farming, forestry, fishing, and animal husbandry is termed the:",
        "option_a": "Primary Sector", "option_b": "Secondary Sector", "option_c": "Tertiary Sector", "option_d": "Quaternary Sector",
        "correct_answer": "A",
        "explanation": "The primary sector involves direct extraction and harvesting of natural resources.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Social Science", "topic": "Indian Polity",
        "question": "How many fundamental rights are currently guaranteed to Indian citizens under Part III of the Constitution?",
        "option_a": "5", "option_b": "6", "option_c": "7", "option_d": "8",
        "correct_answer": "B",
        "explanation": "There are 6 fundamental rights (Right to Equality, Freedom, Against Exploitation, Freedom of Religion, Cultural/Educational, and Constitutional Remedies).",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Social Science", "topic": "Economics",
        "question": "Which premier institution serves as the central monetary authority and currency issuing bank in India?",
        "option_a": "State Bank of India (SBI)", "option_b": "Reserve Bank of India (RBI)", "option_c": "NITI Aayog", "option_d": "Ministry of Finance",
        "correct_answer": "B",
        "explanation": "The Reserve Bank of India (RBI), established in 1935, manages monetary policy and currency issuance.",
        "difficulty": "Easy"
    },

    # ENGLISH
    {
        "category": "highschool", "subject": "English", "topic": "Grammar - Parts of Speech",
        "question": "Identify the adverb in the following sentence: 'The talented musician played the violin exceptionally well.'",
        "option_a": "Talented", "option_b": "Musician", "option_c": "Exceptionally", "option_d": "Violin",
        "correct_answer": "C",
        "explanation": "'Exceptionally' is an adverb of degree modifying the adverb 'well' (which in turn modifies the verb 'played').",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "English", "topic": "Vocabulary - Antonyms",
        "question": "Select the word that is most nearly OPPOSITE in meaning to 'METICULOUS':",
        "option_a": "Careless", "option_b": "Thorough", "option_c": "Accurate", "option_d": "Diligent",
        "correct_answer": "A",
        "explanation": "'Meticulous' means showing great attention to detail; its direct antonym is 'careless' or 'sloppy'.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "English", "topic": "Grammar - Active & Passive Voice",
        "question": "What is the passive voice form of: 'Shakespeare wrote Hamlet'?",
        "option_a": "Hamlet was written by Shakespeare.", "option_b": "Hamlet is being written by Shakespeare.", "option_c": "Hamlet had been written by Shakespeare.", "option_d": "Hamlet wrote Shakespeare.",
        "correct_answer": "A",
        "explanation": "In passive voice for simple past, 'object + was/were + past participle + by subject' gives: 'Hamlet was written by Shakespeare.'",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "English", "topic": "Idioms & Phrases",
        "question": "What does the idiom 'Piece of cake' signify?",
        "option_a": "A birthday celebration", "option_b": "A very easy task", "option_c": "A difficult puzzle", "option_d": "A sweet dessert",
        "correct_answer": "B",
        "explanation": "The colloquial idiom 'a piece of cake' refers to an action or assignment that is straightforward to accomplish.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "English", "topic": "Literary Devices",
        "question": "Which literary device involves giving human traits or emotions to non-human objects, as in 'The wind whispered through the trees'?",
        "option_a": "Metaphor", "option_b": "Hyperbole", "option_c": "Personification", "option_d": "Oxymoron",
        "correct_answer": "C",
        "explanation": "Personification attributes human qualities, feelings, or actions to inanimate objects or abstractions.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "English", "topic": "Spelling & Vocabulary",
        "question": "Choose the correctly spelled English word:",
        "option_a": "Accomodation", "option_b": "Accommodation", "option_c": "Acommodation", "option_d": "Accomadation",
        "correct_answer": "B",
        "explanation": "'Accommodation' has two 'c's and two 'm's.",
        "difficulty": "Medium"
    },

    # GENERAL KNOWLEDGE
    {
        "category": "highschool", "subject": "General Knowledge", "topic": "Science & Space",
        "question": "Which planet in our solar system is nicknamed the 'Red Planet' due to abundant iron oxide on its surface?",
        "option_a": "Venus", "option_b": "Mars", "option_c": "Jupiter", "option_d": "Mercury",
        "correct_answer": "B",
        "explanation": "Mars appears reddish because ferric oxide (rust) is prevalent in its surface regolith.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "General Knowledge", "topic": "Current & National Affairs",
        "question": "Which Indian city is proudly known as the 'Silicon Valley of India' for its leading IT export industry?",
        "option_a": "Hyderabad", "option_b": "Bengaluru", "option_c": "Pune", "option_d": "Chennai",
        "correct_answer": "B",
        "explanation": "Bengaluru (Bangalore), Karnataka is the premier information technology hub and software capital of India.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "General Knowledge", "topic": "Inventions & Discoveries",
        "question": "Who is credited with inventing the World Wide Web (WWW) in 1989 at CERN?",
        "option_a": "Bill Gates", "option_b": "Steve Jobs", "option_c": "Sir Tim Berners-Lee", "option_d": "Alan Turing",
        "correct_answer": "C",
        "explanation": "British computer scientist Sir Tim Berners-Lee invented the World Wide Web in 1989 while working at CERN.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "General Knowledge", "topic": "Awards & Honors",
        "question": "Who was the first Indian citizen to be awarded the prestigious Nobel Prize (for Literature in 1913)?",
        "option_a": "Rabindranath Tagore", "option_b": "C. V. Raman", "option_c": "Mother Teresa", "option_d": "Amartya Sen",
        "correct_answer": "A",
        "explanation": "Rabindranath Tagore received the 1913 Nobel Prize in Literature for his profound poetry collection 'Gitanjali'.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "General Knowledge", "topic": "Environment",
        "question": "On which calendar date is 'World Environment Day' celebrated globally each year?",
        "option_a": "April 22", "option_b": "June 5", "option_c": "September 16", "option_d": "December 1",
        "correct_answer": "B",
        "explanation": "World Environment Day is observed internationally on June 5 to foster ecological awareness and protection.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "General Knowledge", "topic": "Sports",
        "question": "In cricket, what is the maximum number of runs that can be scored off a single legal delivery without overthrows?",
        "option_a": "4", "option_b": "6", "option_c": "5", "option_d": "8",
        "correct_answer": "B",
        "explanation": "A batsman striking the ball completely over the boundary rope on the full scores 6 runs.",
        "difficulty": "Easy"
    }
]

# Expanding High School with additional questions to guarantee 60+ questions in pool
MORE_HS_QUESTIONS = [
    {
        "category": "highschool", "subject": "Biology", "topic": "Microbiology",
        "question": "Which disease among the following is caused by a virus rather than a bacterium?",
        "option_a": "Tuberculosis", "option_b": "Influenza (Flu)", "option_c": "Cholera", "option_d": "Typhoid",
        "correct_answer": "B",
        "explanation": "Influenza is caused by influenza viruses, whereas Tuberculosis, Cholera, and Typhoid are bacterial infections.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Science", "topic": "Physics - Sound",
        "question": "What property of a sound wave determines its perceived pitch?",
        "option_a": "Amplitude", "option_b": "Frequency", "option_c": "Velocity", "option_d": "Wavelength",
        "correct_answer": "B",
        "explanation": "Pitch depends directly upon the frequency of sound oscillations; higher frequency yields higher pitch.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "Mathematics", "topic": "Statistics",
        "question": "What is the median of the following dataset: 3, 7, 8, 12, 14, 19, 21?",
        "option_a": "8", "option_b": "12", "option_c": "14", "option_d": "10",
        "correct_answer": "B",
        "explanation": "With 7 ordered numbers, the middle (4th) element is 12, which represents the median.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "History", "topic": "World History",
        "question": "World War II concluded in which year following the surrender of Axis forces?",
        "option_a": "1939", "option_b": "1941", "option_c": "1945", "option_d": "1950",
        "correct_answer": "C",
        "explanation": "World War II concluded in 1945 with the capitulation of Germany in May and Japan in September.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Geography", "topic": "Oceanography",
        "question": "Which ocean is the deepest and largest in surface area on Earth?",
        "option_a": "Atlantic Ocean", "option_b": "Indian Ocean", "option_c": "Pacific Ocean", "option_d": "Arctic Ocean",
        "correct_answer": "C",
        "explanation": "The Pacific Ocean covers over 165 million square kilometers and houses the deepest trench (Mariana Trench).",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "Social Science", "topic": "Economics",
        "question": "The total monetary value of all finished goods and services produced within a country's domestic borders in a year is known as:",
        "option_a": "Gross Domestic Product (GDP)", "option_b": "Net National Income", "option_c": "Per Capita Income", "option_d": "Fiscal Deficit",
        "correct_answer": "A",
        "explanation": "Gross Domestic Product (GDP) quantifies the domestic market value of all final products and services.",
        "difficulty": "Medium"
    },
    {
        "category": "highschool", "subject": "English", "topic": "Vocabulary - Synonyms",
        "question": "What is the closest synonym for the word 'CANDID'?",
        "option_a": "Deceitful", "option_b": "Frank and Outspoken", "option_c": "Hesitant", "option_d": "Complex",
        "correct_answer": "B",
        "explanation": "'Candid' denotes frank, honest, and unreserved straightforwardness.",
        "difficulty": "Easy"
    },
    {
        "category": "highschool", "subject": "General Knowledge", "topic": "Geography & World Capitals",
        "question": "What is the capital city of Japan?",
        "option_a": "Kyoto", "option_b": "Osaka", "option_c": "Tokyo", "option_d": "Hiroshima",
        "correct_answer": "C",
        "explanation": "Tokyo is the capital and most populous metropolitan prefecture of Japan.",
        "difficulty": "Easy"
    }
]

# -------------------------------------------------------------
# PUC & DEGREE TECHNICAL ASSESSMENT (100+ Computer Science Questions)
# Covering: Arrays, Strings, Linked Lists, Stacks, Queues, Searching,
# Sorting, Trees, Graphs, OOPS, Java, Python, C++, Networks, OS, DBMS, ML, AI
# -------------------------------------------------------------
PUC_DEGREE_QUESTIONS = [
    # 1. ARRAYS
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Arrays",
        "question": "What is the worst-case time complexity to access an element by its index in a standard contiguous array?",
        "option_a": "O(1)", "option_b": "O(n)", "option_c": "O(log n)", "option_d": "O(n²)",
        "correct_answer": "A",
        "explanation": "Arrays provide direct memory addressing via base_address + (index * element_size), executing in O(1) constant time.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Arrays",
        "question": "What is the worst-case time complexity of inserting an element at the beginning (index 0) of an array with n elements?",
        "option_a": "O(1)", "option_b": "O(log n)", "option_c": "O(n)", "option_d": "O(n log n)",
        "correct_answer": "C",
        "explanation": "Inserting at index 0 requires shifting all existing n elements one position to the right, incurring O(n) operations.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Arrays",
        "question": "Kadane's algorithm is widely celebrated for solving which classic array problem in O(n) linear time?",
        "option_a": "Longest Increasing Subsequence", "option_b": "Maximum Subarray Sum", "option_c": "Matrix Multiplication", "option_d": "Finding Array Duplicates",
        "correct_answer": "B",
        "explanation": "Kadane's algorithm computes the maximum contiguous subarray sum in a 1D array in optimal O(n) time and O(1) auxiliary space.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Arrays",
        "question": "In a 2D array matrix of size M x N stored in Row-Major order, the memory address of element A[i][j] with base address B and element size S is:",
        "option_a": "B + (i * N + j) * S", "option_b": "B + (j * M + i) * S", "option_c": "B + (i + j) * S", "option_d": "B + (i * M + j) * S",
        "correct_answer": "A",
        "explanation": "Row-major storage lays out elements row by row; thus skipping i full rows of length N yields offset (i * N + j) * S.",
        "difficulty": "Medium"
    },

    # 2. STRINGS
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Strings",
        "question": "Which string searching algorithm precomputes a 'Prefix Function' (π table) to avoid redundant character comparisons in O(n + m) time?",
        "option_a": "Rabin-Karp", "option_b": "Knuth-Morris-Pratt (KMP)", "option_c": "Boyer-Moore", "option_d": "Aho-Corasick",
        "correct_answer": "B",
        "explanation": "The KMP algorithm constructs a longest proper prefix which is also suffix (LPS) array, achieving linear O(N + M) search.",
        "difficulty": "Hard"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Strings",
        "question": "In Java and Python, strings are designed to be:",
        "option_a": "Mutable", "option_b": "Immutable", "option_c": "Volatile", "option_d": "Dynamic Pointers",
        "correct_answer": "B",
        "explanation": "String objects in Java and Python cannot be modified once instantiated. Modifications yield new string allocations.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Strings",
        "question": "The Rabin-Karp pattern matching algorithm relies on which underlying computer science mechanism?",
        "option_a": "Dynamic Programming", "option_b": "Rolling Hash Function", "option_c": "Trie Traversal", "option_d": "Greedy Choice",
        "correct_answer": "B",
        "explanation": "Rabin-Karp calculates rolling hashes for successive substrings to test pattern matches efficiently.",
        "difficulty": "Medium"
    },

    # 3. LINKED LISTS
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Linked Lists",
        "question": "Floyd's Cycle-Finding Algorithm (Tortoise and Hare) detects loops in a singly linked list using two pointers that advance by:",
        "option_a": "1 node and 2 nodes per step", "option_b": "1 node and 3 nodes per step", "option_c": "2 nodes and 4 nodes per step", "option_d": "Same speed",
        "correct_answer": "A",
        "explanation": "The slow pointer advances by 1 step while the fast pointer moves 2 steps; if a cycle exists, they must inevitably collide.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Linked Lists",
        "question": "What is the time complexity to insert a new node immediately after a given pointer node in a singly linked list?",
        "option_a": "O(1)", "option_b": "O(n)", "option_c": "O(log n)", "option_d": "O(n log n)",
        "correct_answer": "A",
        "explanation": "When the direct reference to the predecessor node is already known, updating pointers takes O(1) constant time.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Linked Lists",
        "question": "In a Doubly Linked List, each node maintains pointers to:",
        "option_a": "Only next node", "option_b": "Both next and previous nodes", "option_c": "Only previous node and head", "option_d": "All ancestor nodes",
        "correct_answer": "B",
        "explanation": "Doubly linked list nodes store pointers to both their successor (`next`) and predecessor (`prev`) nodes.",
        "difficulty": "Easy"
    },

    # 4. STACKS
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Stacks",
        "question": "Which fundamental principle governs the addition and removal of items in a Stack data structure?",
        "option_a": "First In First Out (FIFO)", "option_b": "Last In First Out (LIFO)", "option_c": "Highest Priority First", "option_d": "Shortest Job First",
        "correct_answer": "B",
        "explanation": "Stacks operate strictly on a LIFO (Last In First Out) basis, where elements are pushed and popped from the top.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Stacks",
        "question": "Which algorithm commonly employs a Stack to convert infix arithmetic expressions into postfix (Reverse Polish) notation?",
        "option_a": "Dijkstra's Shunting-yard algorithm", "option_b": "Prim's algorithm", "option_c": "Kruskal's algorithm", "option_d": "Bellman-Ford",
        "correct_answer": "A",
        "explanation": "Edsger Dijkstra's Shunting-yard algorithm parses mathematical operators onto an operator stack according to precedence.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Stacks",
        "question": "What condition occurs when attempting to POP an element from an already empty stack?",
        "option_a": "Stack Overflow", "option_b": "Stack Underflow", "option_c": "Segmentation Fault", "option_d": "Memory Leak",
        "correct_answer": "B",
        "explanation": "Attempting to delete or pop from an empty collection triggers an underflow error condition.",
        "difficulty": "Easy"
    },

    # 5. QUEUES
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Queues",
        "question": "Which underlying discipline governs the arrival and processing of items in a standard Queue?",
        "option_a": "LIFO", "option_b": "FIFO", "option_c": "Random Order", "option_d": "Stack discipline",
        "correct_answer": "B",
        "explanation": "Queues enforce First In First Out (FIFO) semantics: enqueued at the rear, dequeued from the front.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Queues",
        "question": "In a circular queue of capacity N implemented via an array, what index formula advances the rear pointer after enqueueing?",
        "option_a": "rear = (rear + 1) % N", "option_b": "rear = rear + 1", "option_c": "rear = (rear - 1) % N", "option_d": "rear = (rear * 2) % N",
        "correct_answer": "A",
        "explanation": "Modulo arithmetic `(rear + 1) % N` allows the index to wrap seamlessly around to index 0 when reaching capacity.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Queues",
        "question": "Which specialized queue permits insertion and deletion at both ends (front and rear)?",
        "option_a": "Priority Queue", "option_b": "Deque (Double-Ended Queue)", "option_c": "Blocking Queue", "option_d": "Monotonic Stack",
        "correct_answer": "B",
        "explanation": "A Deque (Double-Ended Queue) allows push/pop operations at both the front and rear boundaries.",
        "difficulty": "Easy"
    },

    # 6. SEARCHING
    {
        "category": "puc_degree", "subject": "Algorithms", "topic": "Searching",
        "question": "Binary Search operates efficiently on an array with time complexity O(log n), under which mandatory prerequisite?",
        "option_a": "Array must be dynamically sized", "option_b": "Array elements must be sorted", "option_c": "Array must contain only positive integers", "option_d": "Array must be a linked list",
        "correct_answer": "B",
        "explanation": "Binary search divides search intervals in half, requiring monotonically sorted order to determine target direction.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Algorithms", "topic": "Searching",
        "question": "What is the worst-case number of comparisons required by Linear Search on an array containing n items?",
        "option_a": "1", "option_b": "log₂ n", "option_c": "n", "option_d": "n²",
        "correct_answer": "C",
        "explanation": "In the worst case (target item is at the final position or absent), linear search must examine all n elements.",
        "difficulty": "Easy"
    },

    # 7. SORTING
    {
        "category": "puc_degree", "subject": "Algorithms", "topic": "Sorting",
        "question": "What is the worst-case time complexity of QuickSort when bad pivots (e.g. consistently smallest/largest elements) are selected?",
        "option_a": "O(n log n)", "option_b": "O(n)", "option_c": "O(n²)", "option_d": "O(log n)",
        "correct_answer": "C",
        "explanation": "When partitioning generates unbalanced subproblems of sizes 0 and n-1, QuickSort degenerates into O(n²) quadratic time.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Algorithms", "topic": "Sorting",
        "question": "Which sorting algorithm is guaranteed to execute in O(n log n) time across Best, Average, and Worst cases, while maintaining stability?",
        "option_a": "HeapSort", "option_b": "MergeSort", "option_c": "QuickSort", "option_d": "SelectionSort",
        "correct_answer": "B",
        "explanation": "MergeSort divides arrays into halves and merges in linear time, guaranteeing O(n log n) in all cases and preserving relative order (stable).",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Algorithms", "topic": "Sorting",
        "question": "Counting Sort can achieve O(n + k) linear time performance because it:",
        "option_a": "Is a comparison-based sort", "option_b": "Is a non-comparison sort operating on key frequencies within range k", "option_c": "Uses binary search trees", "option_d": "Performs random swaps",
        "correct_answer": "B",
        "explanation": "Counting sort does not compare elements directly; it tallies occurrence frequencies over an integer range k.",
        "difficulty": "Medium"
    },

    # 8. TREES
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Trees",
        "question": "What is the maximum number of nodes in a binary tree of height h (where height of root node alone is 0)?",
        "option_a": "2^(h+1) - 1", "option_b": "2^h", "option_c": "2^(h-1)", "option_d": "2 * h + 1",
        "correct_answer": "A",
        "explanation": "Summing 2^0 + 2^1 + ... + 2^h yields the geometric series sum 2^(h+1) - 1.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Trees",
        "question": "Which binary tree traversal visits nodes in non-decreasing sorted order for any valid Binary Search Tree (BST)?",
        "option_a": "Pre-order Traversal", "option_b": "In-order Traversal", "option_c": "Post-order Traversal", "option_d": "Level-order Traversal",
        "correct_answer": "B",
        "explanation": "In-order traversal visits Left Subtree -> Root -> Right Subtree, which yields monotonically sorted keys in a BST.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Trees",
        "question": "In an AVL self-balancing binary search tree, what is the allowable balance factor range for every node?",
        "option_a": "{-1, 0, 1}", "option_b": "{-2, 0, 2}", "option_c": "{0, 1}", "option_d": "Any integer",
        "correct_answer": "A",
        "explanation": "The AVL property mandates that height(left) - height(right) must remain strictly within {-1, 0, +1}.",
        "difficulty": "Medium"
    },

    # 9. GRAPHS
    {
        "category": "puc_degree", "subject": "Data Structures", "topic": "Graphs",
        "question": "Which graph traversal algorithm utilizes a Queue to discover vertices level-by-level, finding the shortest path in unweighted graphs?",
        "option_a": "Depth First Search (DFS)", "option_b": "Breadth First Search (BFS)", "option_c": "Topological Sort", "option_d": "Floyd-Warshall",
        "correct_answer": "B",
        "explanation": "BFS expands outward level-by-level using a FIFO queue, guaranteeing shortest hop paths in unweighted graphs.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Algorithms", "topic": "Graphs",
        "question": "Dijkstra's Single Source Shortest Path algorithm fails to compute correct distances in graphs containing:",
        "option_a": "Dense edges", "option_b": "Directed cycles", "option_c": "Negative weight edges", "option_d": "Multiple connected components",
        "correct_answer": "C",
        "explanation": "Dijkstra's greedy assumption assumes path costs only increase monotonically; negative edges break this invariant (Bellman-Ford is needed).",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Algorithms", "topic": "Graphs",
        "question": "Kruskal's algorithm finds a Minimum Spanning Tree (MST) in a connected weighted graph by utilizing which disjoint-set data structure?",
        "option_a": "Union-Find (Disjoint Set Union)", "option_b": "Segment Tree", "option_c": "Fibonacci Heap", "option_d": "Suffix Automaton",
        "correct_answer": "A",
        "explanation": "Kruskal's sorts edges by weight and uses Union-Find with path compression to prevent cycle formation.",
        "difficulty": "Medium"
    },

    # 10. OOPS (OBJECT ORIENTED PROGRAMMING)
    {
        "category": "puc_degree", "subject": "OOPS", "topic": "Object Oriented Concepts",
        "question": "Which core OOP principle restricts direct access to internal object components while bundling data and methods together?",
        "option_a": "Inheritance", "option_b": "Encapsulation", "option_c": "Polymorphism", "option_d": "Dynamic Binding",
        "correct_answer": "B",
        "explanation": "Encapsulation conceals object state details (data hiding) behind well-defined public interface accessors.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "OOPS", "topic": "Polymorphism",
        "question": "Method Overriding in object-oriented programming represents which type of polymorphism?",
        "option_a": "Compile-time (Static) Polymorphism", "option_b": "Run-time (Dynamic) Polymorphism", "option_c": "Ad-hoc Polymorphism", "option_d": "Template Polymorphism",
        "correct_answer": "B",
        "explanation": "Overridden methods are resolved dynamically at runtime based on the actual instantiating object type via virtual method tables.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "OOPS", "topic": "Constructors",
        "question": "Can an abstract class in Java or C++ have a constructor?",
        "option_a": "No, abstract classes never possess constructors", "option_b": "Yes, to initialize member fields when a subclass is instantiated", "option_c": "Only if declared private", "option_d": "Only if declared static",
        "correct_answer": "B",
        "explanation": "Abstract classes have constructors called via `super()` by derived subclass constructors during instantiation.",
        "difficulty": "Medium"
    },

    # 11. JAVA
    {
        "category": "puc_degree", "subject": "Java", "topic": "Java Architecture",
        "question": "Java achieves platform independence ('Write Once, Run Anywhere') by compiling source code (.java) into:",
        "option_a": "Assembly code", "option_b": "Native machine binaries", "option_c": "Bytecode (.class) executed by the JVM", "option_d": "JavaScript",
        "correct_answer": "C",
        "explanation": "The `javac` compiler produces intermediate bytecode, which any Java Virtual Machine (JVM) interprets or JIT-compiles on that OS.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Java", "topic": "Memory Management",
        "question": "In the Java Memory Model, where are dynamic object instances created with the 'new' keyword stored?",
        "option_a": "Call Stack", "option_b": "Heap Memory", "option_c": "Register Set", "option_d": "Native Method Stack",
        "correct_answer": "B",
        "explanation": "All Java objects reside in shared Heap memory, managed by the automatic Garbage Collector.",
        "difficulty": "Easy"
    },

    # 12. PYTHON
    {
        "category": "puc_degree", "subject": "Python", "topic": "Python Internals",
        "question": "What is the Global Interpreter Lock (GIL) in CPython?",
        "option_a": "A security mechanism against SQL injection", "option_b": "A mutex that prevents multiple native threads from executing Python bytecodes simultaneously", "option_c": "A database connection lock", "option_d": "A compiler optimization tool",
        "correct_answer": "B",
        "explanation": "CPython's GIL is a mutex guarding Python object references, restricting thread execution in the interpreter to one thread at a time.",
        "difficulty": "Hard"
    },
    {
        "category": "puc_degree", "subject": "Python", "topic": "Data Types",
        "question": "Which built-in Python data structure is ordered, indexed, and completely mutable?",
        "option_a": "tuple", "option_b": "list", "option_c": "set", "option_d": "frozenset",
        "correct_answer": "B",
        "explanation": "Python lists are mutable sequences; tuples are immutable; sets are unordered collections.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Python", "topic": "Generators",
        "question": "Which Python keyword transforms a standard function into a generator iterator that produces values on-demand?",
        "option_a": "return", "option_b": "yield", "option_c": "emit", "option_d": "async",
        "correct_answer": "B",
        "explanation": "`yield` pauses function execution and emits a value, saving local execution state for subsequent calls.",
        "difficulty": "Medium"
    },

    # 13. C++
    {
        "category": "puc_degree", "subject": "C++", "topic": "Pointers & Memory",
        "question": "In modern C++ (C++11 and onwards), which smart pointer guarantees exclusive, single ownership of a dynamically allocated heap object?",
        "option_a": "std::shared_ptr", "option_b": "std::unique_ptr", "option_c": "std::weak_ptr", "option_d": "std::auto_ptr",
        "correct_answer": "B",
        "explanation": "`std::unique_ptr` manages a unique resource pointer that cannot be copied, only moved, automatically deleting it upon destruction.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "C++", "topic": "Virtual Functions",
        "question": "What happens when a base class destructor is NOT declared 'virtual' and a derived object is deleted through a base class pointer?",
        "option_a": "Derived class destructor is never invoked, causing a memory leak", "option_b": "Compilation error occurs immediately", "option_c": "Code executes normally", "option_d": "Segmentation fault at compile time",
        "correct_answer": "A",
        "explanation": "Without a virtual destructor, `delete basePtr` invokes only the base class destructor, leaking derived class allocated resources.",
        "difficulty": "Hard"
    },

    # 14. COMPUTER NETWORKS
    {
        "category": "puc_degree", "subject": "Computer Networks", "topic": "OSI Model",
        "question": "At which layer of the 7-layer OSI reference model do IP routing and packet forwarding take place?",
        "option_a": "Data Link Layer (Layer 2)", "option_b": "Network Layer (Layer 3)", "option_c": "Transport Layer (Layer 4)", "option_d": "Session Layer (Layer 5)",
        "correct_answer": "B",
        "explanation": "The Network Layer (Layer 3) handles logical network addressing (IPv4/IPv6) and inter-network routing.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Computer Networks", "topic": "Transport Protocols",
        "question": "Which key difference distinguishes TCP from UDP at the Transport layer?",
        "option_a": "TCP is connection-oriented, reliable, and guarantees in-order delivery; UDP is connectionless and faster", "option_b": "UDP guarantees packet delivery while TCP does not", "option_c": "TCP runs only on optical fiber", "option_d": "UDP uses 3-way handshakes",
        "correct_answer": "A",
        "explanation": "TCP establishes stateful connections with flow control and acknowledgments; UDP is a lightweight, best-effort datagram protocol.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Computer Networks", "topic": "Routing Protocols",
        "question": "The Address Resolution Protocol (ARP) is used on local networks to resolve:",
        "option_a": "IP address to MAC address", "option_b": "Domain Name to IP address", "option_c": "MAC address to Port number", "option_d": "Public IP to Private IP",
        "correct_answer": "A",
        "explanation": "ARP broadcasts queries to resolve a 32-bit IPv4 logical address into a 48-bit physical MAC hardware address.",
        "difficulty": "Medium"
    },

    # 15. OPERATING SYSTEMS
    {
        "category": "puc_degree", "subject": "Operating Systems", "topic": "Deadlocks",
        "question": "Which of the following is NOT one of the four Coffman conditions necessary for a Deadlock to occur?",
        "option_a": "Mutual Exclusion", "option_b": "Hold and Wait", "option_c": "No Preemption", "option_d": "Strict Resource Preemption",
        "correct_answer": "D",
        "explanation": "The 4 Coffman conditions are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Preemption breaks deadlock.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Operating Systems", "topic": "CPU Scheduling",
        "question": "Which CPU scheduling algorithm is non-preemptive and notoriously suffers from the 'Convoy Effect'?",
        "option_a": "First-Come, First-Served (FCFS)", "option_b": "Round Robin (RR)", "option_c": "Shortest Remaining Time First (SRTF)", "option_d": "Priority Scheduling",
        "correct_answer": "A",
        "explanation": "Under FCFS, long CPU-burst processes hold the CPU, forcing all subsequent shorter I/O-bound jobs to wait (Convoy Effect).",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Operating Systems", "topic": "Virtual Memory",
        "question": "Belady's Anomaly demonstrates that increasing the number of allocated page frames can paradoxically increase page faults in which algorithm?",
        "option_a": "Optimal Page Replacement", "option_b": "Least Recently Used (LRU)", "option_c": "First-In, First-Out (FIFO)", "option_d": "Clock Algorithm",
        "correct_answer": "C",
        "explanation": "FIFO page replacement exhibits Belady's Anomaly because it is not a stack algorithm.",
        "difficulty": "Hard"
    },

    # 16. DBMS (DATABASE MANAGEMENT SYSTEMS)
    {
        "category": "puc_degree", "subject": "DBMS", "topic": "ACID Properties",
        "question": "In relational database transactions, which ACID property guarantees that either all operations succeed or all changes are rolled back completely?",
        "option_a": "Atomicity", "option_b": "Consistency", "option_c": "Isolation", "option_d": "Durability",
        "correct_answer": "A",
        "explanation": "Atomicity ensures the 'all-or-nothing' execution of transactional database statements.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "DBMS", "topic": "Normalization",
        "question": "A database relation is in Third Normal Form (3NF) if it is already in 2NF and has no:",
        "option_a": "Partial functional dependencies", "option_b": "Transitive functional dependencies", "option_c": "Multivalued dependencies", "option_d": "Join dependencies",
        "correct_answer": "B",
        "explanation": "3NF requires that no non-prime attribute is transitively dependent on any candidate key.",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "DBMS", "topic": "Indexing",
        "question": "Why are B+ Trees predominantly preferred over standard binary search trees for disk-based database indexes?",
        "option_a": "They have smaller nodes than binary trees", "option_b": "High branching factor reduces tree depth and disk I/O, and sequential leaf links speed up range queries", "option_c": "They occupy zero disk space", "option_d": "They eliminate locking",
        "correct_answer": "B",
        "explanation": "B+ Trees have huge fan-outs minimizing disk block seeks, and linked leaf nodes provide fast range scans.",
        "difficulty": "Hard"
    },

    # 17. MACHINE LEARNING & AI
    {
        "category": "puc_degree", "subject": "Machine Learning", "topic": "Classification & Regression",
        "question": "What is the primary difference between Supervised Learning and Unsupervised Learning?",
        "option_a": "Supervised uses labeled training datasets; unsupervised infers latent patterns from unlabeled data", "option_b": "Supervised uses neural networks while unsupervised does not", "option_c": "Unsupervised is only for classification", "option_d": "Supervised never needs loss functions",
        "correct_answer": "A",
        "explanation": "Supervised algorithms learn mappings from labeled input-output pairs (X -> Y); unsupervised finds intrinsic structures in unannotated X.",
        "difficulty": "Easy"
    },
    {
        "category": "puc_degree", "subject": "Machine Learning", "topic": "Model Evaluation",
        "question": "In classification metrics, what does the term 'Precision' measure?",
        "option_a": "TP / (TP + FP)", "option_b": "TP / (TP + FN)", "option_c": "(TP + TN) / Total", "option_d": "2 * (Precision * Recall) / (Precision + Recall)",
        "correct_answer": "A",
        "explanation": "Precision evaluates how many of the positively predicted instances were truly positive: True Positives / (True Positives + False Positives).",
        "difficulty": "Medium"
    },
    {
        "category": "puc_degree", "subject": "Artificial Intelligence", "topic": "Search Algorithms",
        "question": "The A* heuristic search algorithm evaluates nodes using f(n) = g(n) + h(n). What must be true of heuristic h(n) to guarantee optimal solutions?",
        "option_a": "h(n) must be monotonic and admissible (never overestimate true cost to goal)", "option_b": "h(n) must always be zero", "option_c": "h(n) must overestimate cost", "option_d": "h(n) must equal g(n)",
        "correct_answer": "A",
        "explanation": "Admissibility ensures A* never rules out optimal paths by overestimating remaining distance to goal.",
        "difficulty": "Hard"
    },
    {
        "category": "puc_degree", "subject": "Machine Learning", "topic": "Decision Trees",
        "question": "Which metric measuring impurity or disorder is minimized when splitting nodes in the ID3 / CART decision tree algorithm?",
        "option_a": "Entropy / Gini Impurity", "option_b": "Euclidean Distance", "option_c": "Mahalanobis Distance", "option_d": "Cosine Similarity",
        "correct_answer": "A",
        "explanation": "Decision trees choose attribute splits maximizing Information Gain (reducing Shannon Entropy or Gini Impurity).",
        "difficulty": "Medium"
    }
]

# Adding 50+ programmatic variations to guarantee an expansive question bank
def populate_additional_questions():
    """Generates additional high quality questions to ensure 100+ unique questions per test."""
    more_technical = []
    
    # Extra Array & Linked List questions
    more_technical.append({
        "category": "puc_degree", "subject": "Data Structures", "topic": "Arrays",
        "question": "What is the time complexity to find the median of an unsorted array of n elements using the Quickselect algorithm in the average case?",
        "option_a": "O(n)", "option_b": "O(n log n)", "option_c": "O(n²)", "option_d": "O(log n)",
        "correct_answer": "A",
        "explanation": "Quickselect discards half the search space on each partition, yielding average time n + n/2 + n/4 + ... = O(n).",
        "difficulty": "Medium"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "Data Structures", "topic": "Linked Lists",
        "question": "To reverse a singly linked list iteratively in-place, how many pointer variables are required?",
        "option_a": "1", "option_b": "3 (prev, curr, next)", "option_c": "n pointers", "option_d": "Cannot be reversed in-place",
        "correct_answer": "B",
        "explanation": "Three pointers (`prev`, `curr`, and `next`) track the reversing chain without allocating secondary nodes.",
        "difficulty": "Easy"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "Algorithms", "topic": "Dynamic Programming",
        "question": "What are the two foundational characteristics a computational problem must possess to be solvable via Dynamic Programming?",
        "option_a": "Greedy choice and linearity", "option_b": "Optimal substructure and overlapping subproblems", "option_c": "Heuristic evaluation and admissibility", "option_d": "Divide and conquer with independent subproblems",
        "correct_answer": "B",
        "explanation": "Dynamic Programming optimizes problems with overlapping subproblems (memoization/tabulation) and optimal substructure.",
        "difficulty": "Medium"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "Algorithms", "topic": "Graph Algorithms",
        "question": "Which algorithm computes All-Pairs Shortest Paths in an edge-weighted directed graph in O(V³) time?",
        "option_a": "Bellman-Ford", "option_b": "Floyd-Warshall", "option_c": "Dijkstra", "option_d": "Tarjan's strongly connected components",
        "correct_answer": "B",
        "explanation": "Floyd-Warshall uses a dynamic programming triple-loop to compute shortest paths between all pairs of vertices in O(V³).",
        "difficulty": "Hard"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "OOPS", "topic": "Design Principles",
        "question": "In the SOLID design principles for object-oriented software, what does the 'L' stand for?",
        "option_a": "Linear Inheritance Principle", "option_b": "Liskov Substitution Principle", "option_c": "Logical Cohesion Principle", "option_d": "Lazy Loading Principle",
        "correct_answer": "B",
        "explanation": "Liskov Substitution Principle states that subtypes must be substitutable for their base types without altering correctness.",
        "difficulty": "Medium"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "Operating Systems", "topic": "Synchronization",
        "question": "What synchronization primitive is an integer variable accessed exclusively through atomic wait() [P] and signal() [V] operations?",
        "option_a": "Semaphore", "option_b": "Spinlock", "option_c": "Pipe", "option_d": "Socket",
        "correct_answer": "A",
        "explanation": "Dijkstra introduced the Semaphore, whose atomic wait() decrements and signal() increments the shared resource count.",
        "difficulty": "Medium"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "Computer Networks", "topic": "Network Security",
        "question": "Which cryptographic protocol operates over TCP port 443 to provide encrypted HTTP internet communication?",
        "option_a": "FTP", "option_b": "TLS / SSL (HTTPS)", "option_c": "SNMP", "option_d": "Telnet",
        "correct_answer": "B",
        "explanation": "Transport Layer Security (TLS) encrypts web data between client browsers and servers over port 443.",
        "difficulty": "Easy"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "DBMS", "topic": "SQL",
        "question": "In SQL, which clause is specifically used to filter groups created by the GROUP BY statement?",
        "option_a": "WHERE", "option_b": "HAVING", "option_c": "ORDER BY", "option_d": "LIMIT",
        "correct_answer": "B",
        "explanation": "`HAVING` filters aggregate groups, whereas `WHERE` filters individual rows prior to grouping.",
        "difficulty": "Easy"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "Machine Learning", "topic": "Regularization",
        "question": "Which regularization technique adds the absolute sum of coefficient weights (L1 penalty) to the loss function, encouraging parameter sparsity?",
        "option_a": "Ridge Regularization (L2)", "option_b": "Lasso Regularization (L1)", "option_c": "Dropout", "option_d": "Batch Normalization",
        "correct_answer": "B",
        "explanation": "Lasso (Least Absolute Shrinkage and Selection Operator) penalizes sum(|w|), driving irrelevant weights exactly to zero.",
        "difficulty": "Medium"
    })
    more_technical.append({
        "category": "puc_degree", "subject": "Data Structures", "topic": "Hashing",
        "question": "When two distinct keys produce the identical hash index in a hash table, this event is termed a:",
        "option_a": "Hash Overflow", "option_b": "Hash Collision", "option_c": "Hash Underflow", "option_d": "Deadlock",
        "correct_answer": "B",
        "explanation": "A hash collision occurs when hash(k1) == hash(k2). It is resolved via chaining or open addressing.",
        "difficulty": "Easy"
    })

    return more_technical

def seed_all_questions():
    """Populates SQLite questions table with verified High School & Technical question banks."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing questions to prevent duplicates upon re-seeding
    cursor.execute('DELETE FROM questions')
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="questions"')

    all_hs = list(HIGH_SCHOOL_QUESTIONS) + list(MORE_HS_QUESTIONS)
    all_puc = list(PUC_DEGREE_QUESTIONS) + populate_additional_questions()

    # Expand High School to guarantee 70+ unique questions across 8 subjects
    extra_hs_data = [
        ("Biology", "Cell Division", "What type of cell division reduces chromosome numbers by half to generate gametes?", "Mitosis", "Meiosis", "Binary Fission", "Budding", "B", "Meiosis produces haploid sex cells (gametes) with half the parental chromosomes.", "Easy"),
        ("Biology", "Nutrition", "Which vitamin deficiency is primarily responsible for causing Scurvy in humans?", "Vitamin A", "Vitamin B12", "Vitamin C", "Vitamin D", "C", "Ascorbic acid (Vitamin C) deficiency causes scurvy, leading to bleeding gums.", "Easy"),
        ("Biology", "Photosynthesis", "What is the primary gaseous byproduct released by plants during the light reactions of photosynthesis?", "Carbon Dioxide", "Nitrogen", "Oxygen", "Methane", "C", "Photolysis of water molecules during photosynthesis releases diatomic Oxygen (O2).", "Easy"),
        ("Biology", "Human Skeleton", "Which is the longest, strongest, and heaviest bone in the adult human body?", "Tibia", "Fibula", "Femur (Thigh bone)", "Humerus", "C", "The Femur (thigh bone) is the longest and strongest structural bone in humans.", "Easy"),
        ("Science", "Chemistry - Bonding", "The chemical bond formed through the mutual sharing of valence electron pairs is termed a:", "Ionic Bond", "Covalent Bond", "Hydrogen Bond", "Metallic Bond", "B", "Covalent bonding involves electrostatic attraction from shared electron pairs between non-metals.", "Easy"),
        ("Science", "Physics - Energy", "What is the SI unit of Work and Energy?", "Newton", "Pascal", "Joule", "Watt", "C", "One Joule (J) equals one Newton-meter of work performed.", "Easy"),
        ("Science", "Chemistry - Gases", "Which gas constitutes roughly 78 percent of Earth's atmosphere by volume?", "Oxygen", "Carbon Dioxide", "Nitrogen", "Argon", "C", "Molecular Nitrogen (N2) makes up approximately 78% of dry atmospheric air.", "Easy"),
        ("Science", "Physics - Nuclear", "Nuclear fission in commercial nuclear power reactors predominantly uses which isotope as fissile fuel?", "Uranium-235", "Uranium-238", "Carbon-14", "Thorium-230", "A", "U-235 easily undergoes induced fission upon capturing thermal neutrons.", "Medium"),
        ("Mathematics", "Geometry", "What is the perimeter of a rectangle with length 15 cm and width 8 cm?", "23 cm", "46 cm", "120 cm", "60 cm", "B", "Perimeter = 2 * (length + width) = 2 * (15 + 8) = 2 * 23 = 46 cm.", "Easy"),
        ("Mathematics", "Exponents", "What is the value of 2 to the power of 8 (2^8)?", "128", "256", "512", "1024", "B", "2^8 = 256.", "Easy"),
        ("Mathematics", "Percentages", "If an item costing Rs. 500 is sold with a 20% discount, what is its selling price?", "Rs. 380", "Rs. 400", "Rs. 420", "Rs. 450", "B", "Discount = 20% of 500 = 100. Selling price = 500 - 100 = Rs. 400.", "Easy"),
        ("Mathematics", "Coordinate Geometry", "What is the slope of a horizontal straight line parallel to the x-axis?", "0", "1", "Undefined", "-1", "A", "Horizontal lines have delta y = 0, hence slope m = 0.", "Easy"),
        ("History", "Ancient India", "Emperor Ashoka embraced Buddhism following the devastating bloodshed of which famous war?", "Battle of Panipat", "Kalinga War", "Battle of Plassey", "Battle of Buxar", "B", "The Kalinga War (261 BCE) inspired Ashoka to adopt Dhamma and renounce armed conquest.", "Easy"),
        ("History", "Indian Renaissance", "Who founded the Brahmo Samaj in 1828 to promote social reform and abolish Sati?", "Swami Vivekananda", "Raja Ram Mohan Roy", "Ishwar Chandra Vidyasagar", "Dayananda Saraswati", "B", "Raja Ram Mohan Roy founded Brahmo Samaj and pioneered modern Indian social reform.", "Medium"),
        ("History", "Indian National Movement", "The historic slogan 'Swaraj is my birthright and I shall have it' was declared by:", "Bal Gangadhar Tilak", "Lala Lajpat Rai", "Bipin Chandra Pal", "Subhas Chandra Bose", "A", "Bal Gangadhar Tilak proclaimed this famous nationalist rallying cry.", "Easy"),
        ("Geography", "Indian Rivers", "Which river is also venerated as the 'Dakshin Ganga' (Ganges of the South)?", "Godavari", "Krishna", "Kaveri", "Mahanadi", "A", "Godavari is referred to as Dakshin Ganga due to its scale and spiritual significance.", "Medium"),
        ("Geography", "Solar System", "Which planet rotates on its side with an axial tilt of nearly 98 degrees?", "Neptune", "Uranus", "Saturn", "Jupiter", "B", "Uranus has an extreme axial tilt of ~97.8 degrees, essentially rotating on its side.", "Medium"),
        ("Geography", "Cartography", "What is a line on a map joining places of equal atmospheric pressure called?", "Isobar", "Isotherm", "Isohyet", "Contour", "A", "Isobars connect geographical locations sharing identical barometric pressure.", "Medium"),
        ("Social Science", "Civics", "What is the tenure of a member elected to the Rajya Sabha (Upper House of Indian Parliament)?", "4 years", "5 years", "6 years", "Permanent", "C", "Rajya Sabha members serve a 6-year term, with one-third retiring every two years.", "Medium"),
        ("Social Science", "Economics", "What does 'Inflation' describe in macroeconomic terms?", "A sustained decrease in prices", "A general and continuous rise in price levels over time", "Increase in currency value", "Growth of unemployment", "B", "Inflation is a progressive decline in purchasing power reflected by persistent price increases.", "Easy"),
        ("English", "Grammar - Conjunctions", "Complete the sentence: 'She worked hard, ______ she failed to secure the top rank.'", "because", "yet", "since", "so", "B", "'Yet' correctly introduces an adversative or contrasting subordinate clause.", "Easy"),
        ("English", "Vocabulary - Idioms", "What is the meaning of 'To burn the midnight oil'?", "To waste electricity", "To work or study late into the night", "To start a fire", "To cause an argument", "B", "It idioms working or studying diligently into late hours.", "Easy"),
        ("General Knowledge", "Space Missions", "What was the name of India's historic moon landing mission that landed Chandrayaan-3 near the lunar South Pole in 2023?", "Mangalyaan", "Chandrayaan-3", "Aditya-L1", "Gaganyaan", "B", "ISRO's Chandrayaan-3 successfully touched down on August 23, 2023.", "Easy"),
        ("General Knowledge", "National Symbols", "What is the national aquatic animal of India?", "Ganges River Dolphin", "Blue Whale", "Olive Ridley Turtle", "Gharial", "A", "The endangered Ganges River Dolphin (Platanista gangetica) is India's national aquatic animal.", "Easy"),
        ("English", "Grammar", "Choose the correct preposition: 'The student was congratulated ______ his stellar academic performance.'", "at", "for", "on", "about", "C", "The standard idiom is 'congratulated on' an achievement.", "Easy"),
        ("Biology", "Genetics", "How many pairs of chromosomes are present in a normal diploid human somatic cell?", "21 pairs", "22 pairs", "23 pairs", "24 pairs", "C", "Human body cells have 23 pairs (46 total) of chromosomes.", "Easy"),
        ("Science", "Chemistry", "What is the common chemical name of baking soda?", "Sodium Carbonate", "Sodium Hydrogen Carbonate (Bicarbonate)", "Calcium Carbonate", "Sodium Hydroxide", "B", "Baking soda is Sodium Bicarbonate (NaHCO3).", "Easy"),
        ("Mathematics", "Geometry", "What is the measure of each interior angle in a regular hexagon?", "108 degrees", "120 degrees", "135 degrees", "140 degrees", "B", "(6 - 2) * 180 / 6 = 720 / 6 = 120 degrees.", "Medium")
    ]
    for subj, top, q, a, b, c, d, corr, exp, diff in extra_hs_data:
        all_hs.append({
            "category": "highschool", "subject": subj, "topic": top,
            "question": q, "option_a": a, "option_b": b, "option_c": c, "option_d": d,
            "correct_answer": corr, "explanation": exp, "difficulty": diff
        })

    # Expand PUC & Degree to guarantee 115+ unique CS questions
    extra_cs_data = [
        ("Data Structures", "Arrays", "In dynamic arrays (like Python list or C++ std::vector), what is the amortized time complexity of append / push_back?", "O(1)", "O(n)", "O(log n)", "O(n²)", "A", "Dynamic arrays double capacity geometrically, yielding O(1) amortized append time.", "Medium"),
        ("Data Structures", "Arrays", "What is the prefix sum array used for in array algorithmic optimizations?", "Finding array maximum", "Range sum queries in O(1) time", "Sorting array in O(n)", "Reversing array", "B", "Prefix sums allow answering sum(L to R) in O(1) by prefix[R] - prefix[L-1].", "Medium"),
        ("Data Structures", "Strings", "What is the minimum edit distance algorithm (Levenshtein Distance) classified under?", "Greedy Approach", "Dynamic Programming", "Divide and Conquer", "Backtracking", "B", "Levenshtein distance builds an (M+1) x (N+1) DP matrix to find minimum insertions, deletions, and substitutions.", "Hard"),
        ("Data Structures", "Strings", "Which data structure is most optimal for implementing auto-complete and dictionary prefix lookups?", "Hash Map", "Trie (Prefix Tree)", "Min Heap", "Binary Search Tree", "B", "Trie nodes represent characters, allowing O(L) prefix lookups where L is key length.", "Medium"),
        ("Data Structures", "Linked Lists", "What is a major memory disadvantage of linked lists compared to contiguous arrays?", "Cannot store integers", "Extra memory overhead for pointer storage per node and cache misses", "Fixed maximum capacity", "Slow insertion at head", "B", "Linked lists store 4/8 byte pointers per element and have poor CPU cache spatial locality.", "Medium"),
        ("Data Structures", "Linked Lists", "How do you find the middle element of a singly linked list in a single pass?", "Count all elements first", "Use two pointers: slow moving 1 step and fast moving 2 steps", "Use a hash set", "Convert list to an array", "B", "When fast reaches the end, slow pointer will point exactly at the middle node.", "Easy"),
        ("Data Structures", "Linked Lists", "In a circular singly linked list, the 'next' pointer of the last node points to:", "NULL", "Head node", "Previous node", "Itself", "B", "The tail node connects back to the head node, forming an unbroken loop.", "Easy"),
        ("Data Structures", "Stacks", "What is the auxiliary space complexity of validating balanced parentheses using a stack for a string of length n?", "O(1)", "O(n)", "O(log n)", "O(n²)", "B", "In the worst case of all open brackets '(((((', the stack stores up to n characters.", "Easy"),
        ("Data Structures", "Stacks", "Which data structure is intrinsically utilized by runtime environments to support function call recursion?", "Call Stack", "Heap Queue", "Circular Buffer", "Hash Table", "A", "The system Call Stack pushes activation stack frames containing return addresses and local variables.", "Easy"),
        ("Data Structures", "Queues", "Which queue variant always serves the element with the highest/lowest priority key first?", "FIFO Queue", "Priority Queue", "Deque", "Ring Buffer", "B", "Priority Queues (typically backed by binary heaps) retrieve extreme elements in O(1) / O(log n).", "Easy"),
        ("Data Structures", "Queues", "How can a queue be implemented using two stacks (Stack1 and Stack2)?", "Enqueues push to Stack1; dequeues pop from Stack2 (transferring when Stack2 is empty)", "Push to both stacks simultaneously", "Cannot be implemented with stacks", "Use stacks as arrays", "A", "Transferring elements between two LIFO stacks reverses order, simulating FIFO semantics.", "Medium"),
        ("Algorithms", "Searching", "Interpolation Search achieves average time complexity O(log(log n)) on sorted arrays when elements are:", "Unsorted", "Uniformly distributed", "Exponentially distributed", "Strings", "B", "Interpolation search estimates target probe position assuming uniform numerical distribution.", "Hard"),
        ("Algorithms", "Searching", "What is the time complexity of Exponential Search on a sorted array of size n?", "O(n)", "O(log n)", "O(1)", "O(n²)", "B", "Exponential search finds range bounds in O(log i) and runs binary search in O(log i), giving O(log n).", "Medium"),
        ("Algorithms", "Sorting", "Which in-place sorting algorithm has the best average-case performance with smallest constant factors on random data?", "Bubble Sort", "QuickSort", "Selection Sort", "Insertion Sort", "B", "QuickSort has excellent cache locality and minimal swap overhead in practical implementations.", "Medium"),
        ("Algorithms", "Sorting", "What is the minimum theoretical lower bound on comparisons for any comparison-based sorting algorithm on n items?", "O(n)", "O(n log n)", "O(n²)", "O(log n)", "B", "Decision tree depth log2(n!) = Omega(n log n) sets the mathematical lower bound for comparison sorts.", "Hard"),
        ("Algorithms", "Sorting", "Which sorting algorithm is commonly adopted by Python (Timsort) and Java for reference objects?", "QuickSort", "Timsort (Hybrid of MergeSort & InsertionSort)", "HeapSort", "RadixSort", "B", "Timsort exploits natural contiguous ordered runs in real-world data with high efficiency.", "Medium"),
        ("Data Structures", "Trees", "In a Max-Heap binary tree with n elements, where is the maximum key located?", "Leaf node", "Root node", "Middle node", "Anywhere", "B", "The Max-Heap property requires parent >= children, locating the global maximum at root in O(1).", "Easy"),
        ("Data Structures", "Trees", "What is the time complexity to insert an element into a Binary Heap of n elements?", "O(1)", "O(log n)", "O(n)", "O(n log n)", "B", "Insertion appends at the bottom leaf and 'heapifies up' through tree height, requiring O(log n).", "Medium"),
        ("Data Structures", "Trees", "In a Red-Black self-balancing BST, what color is the root node guaranteed to be?", "Red", "Black", "Either Red or Black", "Yellow", "B", "Property 2 of Red-Black Trees strictly requires the root node to be Black.", "Medium"),
        ("Data Structures", "Trees", "What is the diameter (longest path between any two nodes) of a binary tree?", "Height of root", "Max path between two leaf nodes passing through or below an ancestor", "Total node count", "Number of leaf nodes", "B", "Tree diameter is the maximum path distance between any two leaves, calculated via DFS.", "Medium"),
        ("Data Structures", "Graphs", "In an Adjacency Matrix representation of a graph with V vertices, what is the space complexity?", "O(V + E)", "O(V²)", "O(E²)", "O(V log V)", "B", "A V x V 2D matrix allocates V² cells regardless of edge density.", "Easy"),
        ("Algorithms", "Graphs", "Topological Sorting can only be performed on which category of graphs?", "Undirected Graphs with cycles", "Directed Acyclic Graphs (DAG)", "Complete Graphs", "Bipartite Graphs", "B", "Topological order establishes linear dependency orders, requiring DAGs without directed cycles.", "Medium"),
        ("Algorithms", "Graphs", "Which algorithm detects strongly connected components (SCCs) in a directed graph using two DFS traversals?", "Kosaraju's Algorithm", "Dijkstra's Algorithm", "Prim's Algorithm", "Kruskal's Algorithm", "A", "Kosaraju's algorithm performs DFS on original graph and reversed transpose graph to identify SCCs.", "Hard"),
        ("Algorithms", "Graphs", "What is the time complexity of Breadth First Search (BFS) using an Adjacency List with V vertices and E edges?", "O(V * E)", "O(V + E)", "O(V²)", "O(E log V)", "B", "BFS visits every vertex once (V) and traverses each incident edge once (E), yielding O(V + E).", "Easy"),
        ("OOPS", "Concepts", "What is the primary objective of 'Data Abstraction' in Object-Oriented Software?", "Hiding complex internal implementation details and exposing only essential interface", "Inheriting fields from parent", "Overloading constructors", "Storing code in databases", "A", "Abstraction simplifies systems by separating interface definitions from low-level implementation.", "Easy"),
        ("OOPS", "Inheritance", "When a class inherits from two or more direct parent classes simultaneously, this is termed:", "Single Inheritance", "Multiple Inheritance", "Multilevel Inheritance", "Hierarchical Inheritance", "B", "Multiple inheritance allows a derived class to combine attributes of several base classes.", "Easy"),
        ("OOPS", "Polymorphism", "Function Overloading is an example of:", "Compile-time (Static) Polymorphism", "Run-time Polymorphism", "Dynamic Dispatch", "Virtual Binding", "A", "Function overloading resolves function signatures at compile time based on parameter types.", "Easy"),
        ("OOPS", "Design", "What is the 'Diamond Problem' associated with in object-oriented programming?", "Polymorphism speed", "Ambiguity in multiple inheritance when two parent classes inherit from a common ancestor", "Memory leak in destructors", "Private variable access", "B", "Ambiguity arises when calling a method from a grandparent class inherited through multiple paths.", "Medium"),
        ("Java", "Collections", "Which Java Collection Framework class implements a resizable dynamic array?", "LinkedList", "ArrayList", "HashSet", "TreeMap", "B", "ArrayList wraps a dynamic array that grows automatically as elements are added.", "Easy"),
        ("Java", "Concurrency", "Which Java keyword ensures that only one thread can execute a block of code at a time on an object monitor?", "volatile", "synchronized", "transient", "final", "B", "The `synchronized` keyword acquires intrinsic object locks, preventing concurrent data race conditions.", "Medium"),
        ("Python", "Decorators", "In Python, what is a 'Decorator'?", "A GUI design tool", "A function that takes another function as argument and extends its behavior without modifying it", "A class destructor", "A package manager", "B", "Decorators wrap callable functions to inject orthogonal cross-cutting logic using @syntax.", "Medium"),
        ("Python", "Memory", "How does Python handle memory management and unused object cleanup?", "Manual malloc and free", "Reference counting combined with a cyclic garbage collector", "RAII only", "No garbage collection", "B", "CPython relies on reference counts, with a generational cyclic GC detecting unreferenced loops.", "Hard"),
        ("C++", "Templates", "What is the C++ mechanism that enables writing generic, type-independent functions and classes?", "Macros", "Templates", "Pointers", "Namespaces", "B", "C++ templates perform compile-time code generation for parameterized types.", "Easy"),
        ("C++", "Memory", "In C++, what is the rule of RAII (Resource Acquisition Is Initialization)?", "Resource lifetime is bound to the lifespan of an object on stack", "Never allocate on heap", "Always use void pointers", "Initialize all variables to zero", "A", "RAII guarantees resource deallocation inside destructors when objects leave scope.", "Medium"),
        ("Computer Networks", "Protocols", "Which protocol dynamically allocates IP addresses and subnet masks to client host machines on a local network?", "DNS", "DHCP", "SMTP", "SNMP", "B", "Dynamic Host Configuration Protocol (DHCP) assigns network configuration parameters automatically.", "Easy"),
        ("Computer Networks", "DNS", "What is the primary role of the Domain Name System (DNS)?", "Encrypting passwords", "Translating human-readable domain names (like google.com) into IP addresses", "Allocating bandwidth", "Filtering malware", "B", "DNS functions as the internet's phonebook, mapping domain names to IP addresses.", "Easy"),
        ("Computer Networks", "TCP/IP", "What three packets constitute the TCP Three-Way Handshake connection establishment?", "SYN -> SYN-ACK -> ACK", "ACK -> SYN -> FIN", "HELLO -> READY -> ACK", "RST -> SYN -> ACK", "A", "The client sends SYN; server replies with SYN-ACK; client confirms with ACK.", "Medium"),
        ("Computer Networks", "Subnetting", "What is the default subnet mask for a standard Class C IPv4 network address?", "255.0.0.0", "255.255.0.0", "255.255.255.0", "255.255.255.255", "C", "Class C addresses allocate 24 bits to the network ID (255.255.255.0).", "Easy"),
        ("Operating Systems", "Processes", "What data structure does the OS kernel maintain to store process state, PID, program counter, and registers?", "Process Control Block (PCB)", "File Allocation Table", "Page Table", "Segment Map", "A", "The PCB holds metadata required to suspend, schedule, and resume process execution.", "Easy"),
        ("Operating Systems", "Thrashing", "What is 'Thrashing' in an operating system with virtual memory?", "Excessive CPU context switching", "A state where the CPU spends significantly more time swapping pages in/out of disk than executing instructions", "Disk corruption", "Network collision", "B", "Thrashing happens when the total working set exceeds available physical RAM frames.", "Medium"),
        ("Operating Systems", "Memory", "What is the purpose of the Translation Lookaside Buffer (TLB) in modern CPU memory management?", "Cache virtual-to-physical address translations to accelerate memory access", "Store disk buffers", "Handle interrupt requests", "Manage register files", "A", "The TLB is a high-speed associative hardware cache for page table mappings.", "Hard"),
        ("Operating Systems", "File Systems", "What is an 'inode' in Unix-like file systems?", "A file compression method", "A data structure storing file metadata (permissions, ownership, file size, block pointers) except filename", "A root directory", "A disk partition", "B", "An inode contains attributes and disk block locations for a filesystem object.", "Medium"),
        ("DBMS", "Keys", "What is a 'Candidate Key' in relational database design?", "A key with duplicate values", "A minimal superkey capable of uniquely identifying every tuple in a relation", "A foreign key", "A secondary index", "B", "Candidate keys uniquely identify rows without redundant attributes.", "Easy"),
        ("DBMS", "Transactions", "In database transaction isolation levels, what is a 'Dirty Read'?", "Reading committed data", "Reading data written by an uncommitted concurrent transaction that might later be rolled back", "Reading deleted tables", "Reading from backup files", "B", "A dirty read occurs under Read Uncommitted isolation when inspecting uncommitted modifications.", "Medium"),
        ("DBMS", "Transactions", "Which database transaction isolation level prevents dirty reads, non-repeatable reads, and phantom reads completely?", "Read Committed", "Repeatable Read", "Serializable", "Snapshot", "C", "Serializable is the highest isolation level, executing transactions as if strictly sequential.", "Hard"),
        ("DBMS", "SQL", "Which SQL command is a Data Definition Language (DDL) command that deletes all rows in a table instantly and cannot be rolled back?", "DELETE", "TRUNCATE", "DROP", "ALTER", "B", "TRUNCATE deallocates data pages directly without logging row-level deletes, making it fast and DDL.", "Medium"),
        ("Machine Learning", "Overfitting", "Which of the following techniques is used to prevent Overfitting in machine learning models?", "Cross-validation and Regularization (L1/L2)", "Increasing model complexity unnecessarily", "Removing validation datasets", "Training on noisy data indefinitely", "A", "Cross-validation, early stopping, pruning, and regularization prevent models from memorizing noise.", "Easy"),
        ("Machine Learning", "Algorithms", "Support Vector Machines (SVM) find an optimal hyperplane that maximizes what metric between distinct classes?", "Entropy", "Margin (distance between hyperplane and nearest support vectors)", "Gini Impurity", "Covariance", "B", "SVM finds the maximum-margin hyperplane separating classes in feature space.", "Medium"),
        ("Machine Learning", "Clustering", "What distance metric is most commonly computed in standard K-Means clustering to assign data points to centroids?", "Hamming Distance", "Euclidean Distance", "Jaccard Index", "Cosine Similarity", "B", "Standard K-Means minimizes the sum of squared Euclidean distances to cluster centroids.", "Easy"),
        ("Artificial Intelligence", "Concepts", "What is the Minimax algorithm widely utilized for in artificial intelligence?", "Shortest path routing", "Adversarial game playing (like Chess or Tic-Tac-Toe) with two players", "Clustering documents", "Language translation", "B", "Minimax searches game trees, maximizing the player's gain while minimizing opponent potential.", "Medium"),
        ("Data Structures", "Hash Tables", "In Open Addressing for hash collision resolution, Quadratic Probing computes probe intervals using which polynomial function?", "Linear i", "Quadratic c1*i + c2*i²", "Exponential 2^i", "Random constant", "B", "Quadratic probing uses hash(k, i) = (hash'(k) + c1*i + c2*i²) mod m to eliminate primary clustering.", "Medium"),
        ("Data Structures", "Trees", "In a B-Tree of order m, what is the maximum number of children any internal node can possess?", "m", "m - 1", "2 * m", "m / 2", "A", "By definition, an order m B-Tree node has at most m children and at most m-1 keys.", "Medium"),
        ("Algorithms", "Greedy", "Huffman Coding constructs optimal prefix-free binary codes for data compression using which data structure?", "Queue", "Min-Priority Queue (Min-Heap)", "Stack", "Adjacency Matrix", "B", "Huffman combines lowest frequency tree roots by repeatedly popping from a Min-Heap.", "Medium"),
        ("Algorithms", "Recursion", "What is the master theorem condition that solves recurrence T(n) = 2T(n/2) + O(n)?", "Case 1: O(n)", "Case 2: O(n log n)", "Case 3: O(n²)", "Does not apply", "B", "Since log_b(a) = log_2(2) = 1 and f(n) = Theta(n^1), Case 2 applies yielding O(n log n).", "Hard"),
        ("OOPS", "Coupling & Cohesion", "In software architecture, what represents desirable software module design?", "High Coupling and Low Cohesion", "Low Coupling and High Cohesion", "High Coupling and High Cohesion", "Low Coupling and Low Cohesion", "B", "High cohesion ensures focused responsibilities; low coupling minimizes inter-module dependencies.", "Easy"),
        ("Java", "Garbage Collection", "Which method can be invoked to suggest that the Java Virtual Machine run the garbage collector?", "Runtime.getRuntime().gc() or System.gc()", "delete()", "free()", "dispose()", "A", "`System.gc()` suggests execution of garbage collection, though execution is non-guaranteed.", "Medium"),
        ("Python", "Comprehensions", "What does the expression `[x**2 for x in range(5) if x % 2 == 0]` evaluate to in Python?", "[0, 4, 16]", "[1, 9]", "[0, 1, 4, 9, 16]", "[4, 16]", "A", "Even numbers in range(5) are 0, 2, 4. Their squares are 0, 4, 16.", "Easy"),
        ("C++", "STL", "Which container in the C++ Standard Template Library is implemented internally as a Red-Black Tree?", "std::vector", "std::set and std::map", "std::unordered_map", "std::deque", "B", "Associative ordered containers `std::set` and `std::map` use self-balancing Red-Black trees.", "Medium"),
        ("Computer Networks", "HTTP", "What is the HTTP status code representing '404'?", "OK", "Bad Request", "Unauthorized", "Not Found", "D", "HTTP 404 indicates the requested resource could not be found on the server.", "Easy"),
        ("Operating Systems", "Inter-Process Communication", "Which IPC mechanism provides shared memory that allows two processes to communicate at memory hardware speed?", "Pipes", "Message Queues", "Shared Memory Segments", "RPC", "C", "Shared memory maps identical physical RAM pages into address spaces of multiple processes.", "Medium"),
        ("DBMS", "Concurrency", "Two-Phase Locking (2PL) protocol ensures which property for concurrent database schedules?", "Atomicity", "Conflict Serializability", "Deadlock Freedom", "Fault Tolerance", "B", "2PL (Growing phase followed by Shrinking phase) mathematically guarantees conflict serializability.", "Hard"),
        ("Machine Learning", "Metrics", "What does the Area Under the Receiver Operating Characteristic Curve (AUC-ROC) measure?", "Regression error", "Model discrimination capability across all classification thresholds", "Clustering inertia", "Feature importance", "B", "AUC-ROC quantifies true positive rate vs false positive rate trade-offs across decision thresholds.", "Medium"),
        ("Artificial Intelligence", "Knowledge Representation", "In First-Order Logic, what does the existential quantifier (∃) express?", "'For all instances'", "'There exists at least one instance'", "'No instance exists'", "'It is false'", "B", "The existential quantifier ∃ states that a predicate holds true for at least one entity in the domain.", "Easy"),
        ("Algorithms", "Complexity", "What class of problems can be verified in polynomial time by a deterministic Turing machine?", "P", "NP", "NP-Hard", "EXPTIME", "B", "NP (Nondeterministic Polynomial time) denotes decision problems verifiable in polynomial time.", "Hard"),
        ("Data Structures", "Strings", "What is the longest palindromic substring time complexity achieved by Manacher's Algorithm?", "O(n²)", "O(n)", "O(n log n)", "O(n³)", "B", "Manacher's algorithm exploits mirror symmetry to find the longest palindrome in optimal O(n) time.", "Hard")
    ]

    for subj, top, q, a, b, c, d, corr, exp, diff in extra_cs_data:
        all_puc.append({
            "category": "puc_degree", "subject": subj, "topic": top,
            "question": q, "option_a": a, "option_b": b, "option_c": c, "option_d": d,
            "correct_answer": corr, "explanation": exp, "difficulty": diff
        })

    total_inserted = 0
    for q in all_hs:
        cursor.execute('''
            INSERT INTO questions (category, subject, topic, question, option_a, option_b, option_c, option_d,
                                  correct_answer, explanation, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (q['category'], q['subject'], q['topic'], q['question'], q['option_a'], q['option_b'],
              q['option_c'], q['option_d'], q['correct_answer'], q['explanation'], q['difficulty']))
        total_inserted += 1

    for q in all_puc:
        cursor.execute('''
            INSERT INTO questions (category, subject, topic, question, option_a, option_b, option_c, option_d,
                                  correct_answer, explanation, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (q['category'], q['subject'], q['topic'], q['question'], q['option_a'], q['option_b'],
              q['option_c'], q['option_d'], q['correct_answer'], q['explanation'], q['difficulty']))
        total_inserted += 1

    conn.commit()
    conn.close()
    print(f"Successfully seeded database with {total_inserted} distinct questions.")
    print(f"High School pool: {len(all_hs)} questions (Target: >= 50).")
    print(f"PUC & Degree pool: {len(all_puc)} questions (Target: >= 100).")

if __name__ == '__main__':
    seed_all_questions()

