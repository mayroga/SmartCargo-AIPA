def generate_advisor_message(validation_result: dict) -> str:
    """
    Explica de manera educativa cada semáforo/documento.
    No reemplaza operador aéreo.
    """
    messages = []
    for doc in validation_result.get("documents", []):
        if doc["status"] == "🟢":
            messages.append(f"{doc['doc_type']} está correcto y cumple normas operativas.")
        elif doc["status"] == "🔴":
            messages.append(f"{doc['doc_type']} tiene error: {doc['observation']}. Revisar antes de enviar.")
        else:
            messages.append(f"{doc['doc_type']} requiere atención: {doc['observation']}")

    for motivo in validation_result.get("motivos", []):
        messages.append(f"Motivo: {motivo}")

    return "\n".join(messages)
