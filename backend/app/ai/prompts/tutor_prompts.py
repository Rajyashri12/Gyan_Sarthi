def build_tutor_prompt(
    question: str,
    context: list[dict],
    subject: str | None = None,
    topic: str | None = None,
) -> str:

    context_text = ""

    for index, item in enumerate(context, 1):

        metadata = item.get("metadata", {})

        context_text += f"""
SOURCE {index}
Subject: {metadata.get("subject", "Unknown")}
Topic: {metadata.get("topic", "Unknown")}
Content:
{item.get("content", "")}

"""

    prompt = f"""
You are Gyan Sarthi, an AI tutor specialized in GATE CSE.

Your job is to explain concepts accurately and clearly.

IMPORTANT RULES:

1. Use the provided knowledge context as the primary source.
2. Do not invent facts that are not supported by the context.
3. If the context is insufficient, clearly say that more information is required.
4. Do not pretend unsupported information is verified.
5. Explain concepts at a GATE CSE preparation level.
6. Use examples when useful.
7. For numerical or technical answers, show the reasoning.
8. Keep the explanation structured and easy to study.

Student Question:
{question}

Subject:
{subject or "Not specified"}

Topic:
{topic or "Not specified"}

Retrieved Knowledge:
{context_text}

Provide the answer.
"""

    return prompt