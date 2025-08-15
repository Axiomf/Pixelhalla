import uuid
import pickle

generated_ids = set()

def generate_unique_client_id():
    """Generate a random 4-character ID and ensure it is unique among active_client_ids."""
    while True:
        client_id = str(uuid.uuid4())[:4]
        if client_id not in generated_ids:
            generated_ids.add(client_id)
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

def serialize_fighters(group, usernames=None):
    """Serialize fighter sprites, including username from the provided usernames dictionary.
    Rect is sent as (x, y, width, height).
    """
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height),
            "state": getattr(sprite, "state", "idle"),
            "id": getattr(sprite, "fighter_id", "id not given"),
            "facing_right": getattr(sprite, "facing_right", True),
            "health": getattr(sprite, "health", 100),
            "max_health": getattr(sprite, "max_health", 100),
            "username": usernames.get(sprite.fighter_id, "Unknown") if usernames else "Unknown",
            "fighter_type": getattr(sprite, "fighter_type", "arcane").lower()
        })
    return serialized
def serialize_projectiles(group):
    """Serialize projectiles. Rect is (x, y, width, height)."""
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height),
            "id": getattr(sprite, "fighter_id", "id not given")
        })
    return serialized
def serialize_power_ups(group):
    """Serialize power-ups. Rect is (x, y, width, height)."""
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height),
            "type": sprite.upgrade_type
        })
    return serialized
def serialize_platforms(group):
    """Serialize platforms. Rect is (x, y, width, height)."""
    
    serialized = []
    for sprite in group.sprites():
        serialized.append({
            "rect": (sprite.rect.x, sprite.rect.y, sprite.rect.width, sprite.rect.height),
            "color": sprite.color
        })
    return serialized

# New helper to send client requests (client-side usage)
def send_request_to_server(conn, client_package):
    """Send a pickled client_package over the given socket. Returns True on success."""
    try:
        conn.sendall(pickle.dumps(client_package))
    except Exception as e:
        print(f"Error sending data: {e}")
        return False
    return True

