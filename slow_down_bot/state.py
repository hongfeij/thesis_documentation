import json

def save_state(bot_instance, filepath="state.json"):
    states = []
    try:
        with open(filepath, "r") as f:
            states = json.load(f)
    except FileNotFoundError:
        pass

    new_entry = {
        "id": len(states) + 1,
        "last_user_input": bot_instance.last_user_input,
        "hallucination_rate": bot_instance.hallucination_rate
    }

    states.append(new_entry)

    with open(filepath, "w") as f:
        json.dump(states, f, indent=4)

# def load_state(bot, filepath="state.json"):
#     try:
#         with open(filepath, "r") as f:
#             states = json.load(f)
#             # Check if states is a list and not empty
#             if isinstance(states, list) and states:
#                 last_state = states[-1]
#                 if isinstance(last_state, dict):
#                     bot.last_user_input = last_state.get(
#                         "last_user_input", "")
#                     bot.hallucination_rate = last_state.get(
#                         "hallucination_rate", 0)
#                 else:
#                     bot.reset_state()
#             else:
#                 bot.reset_state()
#     except (FileNotFoundError, json.JSONDecodeError):
#         bot.reset_state()

# def reset_state(bot):
#     bot.last_user_input = ""
#     bot.hallucination_rate = 0