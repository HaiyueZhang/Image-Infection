import uuid

def generate_token():
    return str(uuid.uuid4())

# Example usage
token = generate_token()
print("Generated token:", token)
