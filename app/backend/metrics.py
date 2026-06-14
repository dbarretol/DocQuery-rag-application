from prometheus_client import Counter, Histogram

# Latency metrics
RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_latency_seconds",
    "Time spent in retrieval",
    ["status"]
)
GENERATION_LATENCY = Histogram(
    "rag_generation_latency_seconds",
    "Time spent in generation",
    ["model", "status"]
)

# Token/Cost metrics
TOKEN_USAGE = Counter(
    "rag_token_usage_total",
    "Total tokens used",
    ["model", "type"] # type: input, output
)
