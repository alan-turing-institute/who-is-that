from flask import Request


def get_context(selected_text: str, request: Request) -> tuple[str, str]:
    selected_text_start = int(request.form["selected_text_start"])
    concatenated_text = request.form["concatenated_text"]
    # Use the start position to slice the concatenated text
    summary = concatenated_text[: selected_text_start + len(selected_text)]
    print(
        f"Summarising up to: {selected_text} using {len(summary)} characters.",
        flush=True,
    )
    return summary, concatenated_text
