def get_recent_chat(messages,limit=4):
    history=[]
    for message in messages[-limit:]:  # -limit gets last four mesaages
        role=message['role']
        content=message['content']
        history.append(
            f"{role}:{content}"
        )
    return "\n".join(history)  # join will merge and becomes conversation memory