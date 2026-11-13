"""Curated role-specific foundational topics and difficulty-calibrated fallback questions."""

from dataclasses import dataclass

from app.modules.interview.calibration import Difficulty, ExperienceLevel
from app.modules.interview.deduplication import is_duplicate_or_paraphrase


@dataclass(frozen=True)
class CuratedQuestion:
    topic: str
    difficulty: Difficulty
    question_type: str  # "conceptual" | "applied" | "gap_probe"
    question_text: str


ROLE_ALIASES: dict[str, str] = {
    "software engineer": "software engineer",
    "swe": "software engineer",
    "software developer": "software engineer",
    "backend developer": "backend developer",
    "backend engineer": "backend developer",
    "python developer": "python developer",
    "python engineer": "python developer",
    "data scientist": "data scientist",
    "machine learning engineer": "machine learning engineer",
    "ml engineer": "machine learning engineer",
    "ai engineer": "ai engineer",
    "genai engineer": "ai engineer",
    "ai / genai engineer": "ai engineer",
}


ROLE_FUNDAMENTAL_TOPICS: dict[str, list[str]] = {
    "software engineer": [
        "Arrays & Linked Lists",
        "Time Complexity",
        "Stacks & Queues",
        "Object-Oriented Programming",
        "Hash Maps",
        "SQL vs NoSQL",
        "REST APIs",
        "Testing & Debugging",
    ],
    "backend developer": [
        "REST APIs",
        "HTTP Methods & Status Codes",
        "Authentication & Authorization",
        "Database Indexing",
        "SQL Joins",
        "Middleware",
        "JWT Authentication",
        "Caching Basics",
    ],
    "python developer": [
        "Lists vs Tuples",
        "Python Dictionaries",
        "Decorators",
        "Generators",
        "Identity vs Equality",
        "Exception Handling",
        "Global Interpreter Lock (GIL)",
        "Virtual Environments & Testing",
    ],
    "data scientist": [
        "Supervised vs Unsupervised Learning",
        "Overfitting & Underfitting",
        "Bias-Variance Tradeoff",
        "Classification Metrics",
        "Cross-Validation",
        "Handling Missing Values",
        "Classification vs Regression",
        "Feature Engineering",
    ],
    "machine learning engineer": [
        "Supervised vs Unsupervised Learning",
        "Overfitting & Regularization",
        "Model Evaluation Metrics",
        "Cross-Validation",
        "Feature Preprocessing",
        "Model Serving & APIs",
        "Data Leakage",
        "Python for ML",
    ],
    "ai engineer": [
        "Embeddings",
        "Retrieval-Augmented Generation (RAG)",
        "Text Chunking",
        "Vector Databases",
        "Transformers & Attention",
        "Prompt Engineering",
        "LLM Evaluation & Hallucinations",
        "API Integration",
    ],
}


CURATED_QUESTION_BANK: dict[str, list[CuratedQuestion]] = {
    "software engineer": [
        CuratedQuestion("Arrays & Linked Lists", "easy", "conceptual", "What is the difference between an array and a linked list, and when would you choose one over the other?"),
        CuratedQuestion("Time Complexity", "easy", "conceptual", "How do you explain Big-O time complexity, and what is the difference between O(1), O(log n), and O(n)?"),
        CuratedQuestion("Stacks & Queues", "easy", "conceptual", "What is the difference between a stack and a queue, and can you give a real example where each is used?"),
        CuratedQuestion("Object-Oriented Programming", "easy", "conceptual", "Can you explain the four pillars of object-oriented programming with a simple example?"),
        CuratedQuestion("Hash Maps", "medium", "conceptual", "How does a hash map work under the hood, and what happens when two keys hash to the same bucket?"),
        CuratedQuestion("SQL vs NoSQL", "medium", "conceptual", "What is the main difference between SQL and NoSQL databases, and how do you decide which to use for a project?"),
        CuratedQuestion("REST APIs", "medium", "applied", "What makes an API RESTful, and how do you design clean endpoints for creating and fetching resources?"),
        CuratedQuestion("Testing & Debugging", "hard", "applied", "How do you diagnose and fix a bug that happens intermittently in production but is hard to reproduce locally?"),
    ],
    "backend developer": [
        CuratedQuestion("REST APIs", "easy", "conceptual", "What is a REST API, and how do HTTP requests and responses communicate between a client and server?"),
        CuratedQuestion("HTTP Methods & Status Codes", "easy", "conceptual", "Explain the difference between GET, POST, PUT, PATCH, and DELETE, along with common HTTP status codes like 200, 201, 400, 401, and 404."),
        CuratedQuestion("Authentication & Authorization", "easy", "conceptual", "What is the difference between authentication and authorization in a backend application?"),
        CuratedQuestion("SQL Joins", "easy", "conceptual", "What is the difference between an INNER JOIN and a LEFT JOIN in SQL?"),
        CuratedQuestion("Middleware", "medium", "applied", "What is middleware in a web framework, and what kinds of tasks are best handled in middleware?"),
        CuratedQuestion("Database Indexing", "medium", "applied", "What is a database index, how does it speed up queries, and what is the trade-off of adding too many indexes?"),
        CuratedQuestion("REST APIs", "medium", "applied", "How would you implement pagination in a REST API that returns a large list of records?"),
        CuratedQuestion("JWT Authentication", "medium", "applied", "How does JWT authentication work from user login to verifying a protected API request?"),
        CuratedQuestion("Caching Basics", "hard", "applied", "When would you add a cache like Redis in front of a database, and how do you handle stale cached data?"),
        CuratedQuestion("API Reliability", "hard", "applied", "How would you prevent duplicate payment processing if a client retries the same request?"),
    ],
    "python developer": [
        CuratedQuestion("Lists vs Tuples", "easy", "conceptual", "What is the difference between a list and a tuple in Python, and when would you use each?"),
        CuratedQuestion("Identity vs Equality", "easy", "conceptual", "In Python, what is the difference between `is` and `==`?"),
        CuratedQuestion("Python Dictionaries", "easy", "conceptual", "How do Python dictionaries work, and why are key lookups fast on average?"),
        CuratedQuestion("Exception Handling", "easy", "applied", "How does try/except/else/finally work in Python, and why should you avoid bare `except:` blocks?"),
        CuratedQuestion("Decorators", "medium", "applied", "What is a Python decorator, and can you describe a practical use case for writing one?"),
        CuratedQuestion("Generators", "medium", "conceptual", "When would you use a generator in Python instead of returning a list?"),
        CuratedQuestion("Global Interpreter Lock (GIL)", "medium", "conceptual", "What is the Global Interpreter Lock (GIL) in CPython, and how does it affect CPU-bound vs I/O-bound tasks?"),
        CuratedQuestion("Memory Efficiency", "hard", "applied", "How would you process a large file efficiently in Python without loading the entire file into memory?"),
        CuratedQuestion("Virtual Environments & Testing", "hard", "applied", "How do you structure and test a Python service using fixtures and mocks so external API calls don't slow down your test suite?"),
    ],
    "data scientist": [
        CuratedQuestion("Supervised vs Unsupervised Learning", "easy", "conceptual", "What is the difference between supervised and unsupervised learning, with an example of each?"),
        CuratedQuestion("Classification vs Regression", "easy", "conceptual", "What is the difference between classification and regression problems, and what algorithms are commonly used for each?"),
        CuratedQuestion("Overfitting & Underfitting", "easy", "conceptual", "What are overfitting and underfitting, and how can you tell when a model is overfitting?"),
        CuratedQuestion("Handling Missing Values", "easy", "applied", "How do you decide how to handle missing values in a tabular dataset before training a model?"),
        CuratedQuestion("Classification Metrics", "medium", "conceptual", "Explain precision, recall, and F1 score. When is accuracy misleading on its own?"),
        CuratedQuestion("Cross-Validation", "medium", "applied", "Why do we use k-fold cross-validation instead of a single train/test split?"),
        CuratedQuestion("Bias-Variance Tradeoff", "medium", "conceptual", "What is the bias-variance tradeoff in machine learning?"),
        CuratedQuestion("Feature Engineering", "hard", "applied", "How do you prevent data leakage when scaling features or encoding categories during cross-validation?"),
    ],
    "machine learning engineer": [
        CuratedQuestion("Supervised vs Unsupervised Learning", "easy", "conceptual", "What is the difference between supervised and unsupervised learning, and how do you choose between them?"),
        CuratedQuestion("Overfitting & Regularization", "easy", "conceptual", "What causes overfitting in a machine learning model, and what are common ways to reduce it?"),
        CuratedQuestion("Model Evaluation Metrics", "easy", "conceptual", "How do you evaluate a classification model when the classes are imbalanced?"),
        CuratedQuestion("Feature Preprocessing", "easy", "applied", "Why is feature scaling important for some ML algorithms, and which algorithms are sensitive to it?"),
        CuratedQuestion("Cross-Validation", "medium", "applied", "How does k-fold cross-validation work, and when would you use stratified k-fold?"),
        CuratedQuestion("Data Leakage", "medium", "applied", "What is data leakage in machine learning pipelines, and how do you prevent it?"),
        CuratedQuestion("Model Serving & APIs", "medium", "applied", "How would you deploy a trained machine learning model as an API so another application can use it?"),
        CuratedQuestion("Model Monitoring", "hard", "applied", "If your model performs well on training data but poorly on production data, how would you investigate the issue?"),
        CuratedQuestion("Model Serving & APIs", "hard", "applied", "What metrics and checks would you monitor after deploying an ML model to detect performance degradation in production?"),
    ],
    "ai engineer": [
        CuratedQuestion("Embeddings", "easy", "conceptual", "What are text embeddings, and how are they used to measure semantic similarity?"),
        CuratedQuestion("Retrieval-Augmented Generation (RAG)", "easy", "conceptual", "What is Retrieval-Augmented Generation (RAG), and why is it useful compared to prompting an LLM alone?"),
        CuratedQuestion("Prompt Engineering", "easy", "applied", "What practical techniques do you use to make LLM outputs more reliable and structured?"),
        CuratedQuestion("Vector Databases", "easy", "conceptual", "What is a vector database, and how does it differ from a traditional relational database?"),
        CuratedQuestion("Text Chunking", "medium", "applied", "What is chunking in a RAG pipeline, and how does chunk size affect retrieval quality?"),
        CuratedQuestion("Transformers & Attention", "medium", "conceptual", "What is the purpose of the attention mechanism in transformers, and why is it useful?"),
        CuratedQuestion("LLM Evaluation & Hallucinations", "medium", "applied", "How do you reduce hallucinations and verify that an LLM answer is grounded in retrieved context?"),
        CuratedQuestion("LLM Evaluation & Hallucinations", "hard", "applied", "How would you design an evaluation test set to measure whether changes to your RAG retriever or prompt actually improved answer quality?"),
    ],
}

GENERIC_QUESTIONS: list[CuratedQuestion] = [
    CuratedQuestion("Core Programming", "easy", "conceptual", "What is the difference between a list/array and a hash map (dictionary), and when do you use each?"),
    CuratedQuestion("SQL & Databases", "easy", "conceptual", "What is the difference between a primary key and a foreign key in a relational database?"),
    CuratedQuestion("APIs & Web", "easy", "conceptual", "What happens when a client sends an HTTP request to a backend API endpoint?"),
    CuratedQuestion("Testing & Debugging", "medium", "applied", "How do you approach writing unit tests for a function that depends on an external service or database?"),
    CuratedQuestion("Version Control & Collaboration", "medium", "applied", "How do you structure commits and pull requests when working on a feature with a team?"),
    CuratedQuestion("Performance & Reliability", "hard", "applied", "If an endpoint in your application becomes slow under load, what steps would you take to identify the bottleneck?"),
]


def canonical_role(target_role: str | None) -> str:
    cleaned = str(target_role or "").strip().lower()
    if cleaned in ROLE_ALIASES:
        return ROLE_ALIASES[cleaned]
    for alias, canonical in ROLE_ALIASES.items():
        if alias in cleaned:
            return canonical
    return "software engineer"


def get_role_fundamental_topics(target_role: str | None) -> list[str]:
    role = canonical_role(target_role)
    return list(ROLE_FUNDAMENTAL_TOPICS.get(role, ROLE_FUNDAMENTAL_TOPICS["software engineer"]))


def pick_curated_fallback_question(
    target_role: str | None,
    topic: str,
    difficulty: Difficulty,
    question_type: str,
    previous_questions: list[str],
    experience_level: ExperienceLevel = "fresher",
    has_resume_evidence: bool = False,
    asked_fingerprints: list[str] | None = None,
) -> CuratedQuestion:
    """Select a realistic, role- and difficulty-calibrated fallback question."""
    role = canonical_role(target_role)
    pool = list(CURATED_QUESTION_BANK.get(role, [])) + list(GENERIC_QUESTIONS)

    def _is_seen(cand_topic: str, cand_text: str) -> bool:
        dup, _ = is_duplicate_or_paraphrase(
            candidate_text=cand_text,
            candidate_topic=cand_topic,
            previous_questions=previous_questions,
            asked_fingerprints=asked_fingerprints,
        )
        return dup

    # 1. Exact or substring topic match in curated bank (preferring matching difficulty)
    topic_lower = topic.strip().lower()
    if topic_lower:
        for item in pool:
            if _is_seen(item.topic, item.question_text):
                continue
            if (
                topic_lower == item.topic.lower()
                or topic_lower in item.topic.lower()
                or topic_lower in item.question_text.lower()
            ) and item.difficulty == difficulty:
                return item

        for item in pool:
            if _is_seen(item.topic, item.question_text):
                continue
            if (
                topic_lower == item.topic.lower()
                or topic_lower in item.topic.lower()
            ):
                return CuratedQuestion(
                    topic=item.topic,
                    difficulty=difficulty,
                    question_type=item.question_type,
                    question_text=item.question_text,
                )

    # 2. Safe, natural topic-specific fallback calibrated to difficulty
    if topic_lower:
        if question_type == "gap_probe":
            text = (
                f"What are the core concepts behind {topic}, and how is it typically used in a {target_role or 'software'} project?"
                if difficulty == "easy"
                else f"How would you use {topic} in a {target_role or 'software'} application, and what common mistake would you watch out for?"
            )
        elif question_type == "applied" and has_resume_evidence:
            text = (
                f"How have you used {topic} in a project or coursework, and what did it help you accomplish?"
                if difficulty == "easy"
                else f"Walk through how you used {topic} in your work—what was one challenge you ran into and how did you solve it?"
            )
        elif difficulty == "hard":
            text = (
                f"What is a challenging edge case or reliability issue you might encounter with {topic} in production, and how would you handle it?"
            )
        else:
            text = (
                f"Can you explain what {topic} is in simple terms and give a practical example of when it is useful?"
                if difficulty == "easy"
                else f"How does {topic} work in practice, and what is one key trade-off to keep in mind?"
            )

        if not _is_seen(topic, text):
            return CuratedQuestion(
                topic=topic,
                difficulty=difficulty,
                question_type=question_type if question_type in {"conceptual", "applied", "gap_probe"} else "conceptual",
                question_text=text,
            )

    # 3. Same difficulty in role bank not yet asked (when topic fallback already asked or empty)
    for item in pool:
        if _is_seen(item.topic, item.question_text):
            continue
        if item.difficulty == difficulty:
            return item

    # 4. Any unasked question in role bank (preferring easy/medium for entry levels)
    preferred_order: tuple[Difficulty, ...] = (
        ("easy", "medium", "hard")
        if experience_level in {"internship", "fresher"}
        else ("medium", "easy", "hard")
    )
    for diff in preferred_order:
        for item in pool:
            if _is_seen(item.topic, item.question_text):
                continue
            if item.difficulty == diff:
                return item

    return CuratedQuestion(
        topic=topic or "Core Programming",
        difficulty=difficulty,
        question_type=question_type if question_type in {"conceptual", "applied", "gap_probe"} else "conceptual",
        question_text=f"Explain a core concept in {topic or 'software engineering'} and give a practical example.",
    )
