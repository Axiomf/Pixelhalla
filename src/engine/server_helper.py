import uuid
import pickle

generated_ids = set()

def generate_unique_client_id():
    """Generate a random 8-character ID and ensure it is unique among active_client_ids."""
    while True:
        client_id = str(uuid.uuid4())[:8]
        if client_id not in generated_ids:
            generated_ids.add(client_id)
            # Removed heavy logging to prevent slowdown
            # print(f"Generated unique client_id: {client_id}")
            return client_id

def broadcast(server_package, list_of_IDs, all_clients):
    """Send a package to all connected clients in a group."""
    for client_id in list_of_IDs:
        send_to_client(server_package, client_id, all_clients)

def send_to_client(server_package, client_id, all_clients):
    """Send a package to a specific client identified by client_id."""
    target = None
    for client in all_clients:
        if client.client_id == client_id:
            target = client
            break
    
    if target is None:
        # print(f"Client {client_id} not found in all_clients")
        return
    try:
        target.conn.sendall(pickle.dumps(server_package))
        # Removed frequent logging to reduce overhead
        # print(f"Sent to client {client_id}: {server_package}")
    except Exception as e:
        print(f"Error sending to client {client_id}: {e}")

def serialize_fighters(group):
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y),  # modified: only x and y coordinates
            "state": getattr(sprite, "state", "idle"),
            "id": getattr(sprite, "fighter_id", "id not given"),
            "is_doing": getattr(sprite, "is_doing", "is_doing not given"),  # cycle animations info
            "facing_right": getattr(sprite, "facing_right", True),
            "health": getattr(sprite, "health", 100),
            "max_health": getattr(sprite, "max_health", 100),
        })
    return serialized
def serialize_projectiles(group):
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y),  # modified: only x and y coordinates
            "id": getattr(sprite, "fighter_id", "id not given")
        })
    return serialized
def serialize_power_ups(group):
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y)  # modified: only x and y coordinates
        })
    return serialized
def serialize_platforms(group):
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y)  # modified: only x and y coordinates
        })
    return serialized

