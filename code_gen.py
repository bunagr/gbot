import random
import json
import os
import string

# Path to your codes.json file
CODES_FILE_PATH = "codes.json"

def generate_random_code(length=8):
    """Generates a random alphanumeric code of specified length."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_reward():
    """Generates a random reward with points between 6 and 500 credits and 6 extra slots."""
    points = random.randint(6, 500)
    extra_slots = 6  # Minimum 6 extra slots
    return {"points": points, "extra_slots": extra_slots}

def load_codes():
    """Load the current codes from the JSON file."""
    if os.path.exists(CODES_FILE_PATH):
        with open(CODES_FILE_PATH, "r") as file:
            return json.load(file)
    else:
        return {"available": [], "claimed": [], "rewarded": []}

def save_codes(codes):
    """Save the updated codes to the JSON file."""
    with open(CODES_FILE_PATH, "w") as file:
        json.dump(codes, file, indent=4)

def generate_code_and_reward(num_codes=5):
    """Generates a specified number of codes and adds them to the available codes list."""
    codes = load_codes()

    for _ in range(num_codes):
        new_code = generate_random_code()
        reward = generate_reward()
        codes["available"].append({"code": new_code, "reward": reward})
    
    save_codes(codes)
    print(f"{num_codes} new codes generated and added to available codes.")

if __name__ == "__main__":
    # Number of codes you want to generate (You can modify this number as needed)
    generate_code_and_reward(1005)
