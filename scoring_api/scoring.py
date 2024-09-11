import hashlib

from store import Store


def get_cache_key(first_name, last_name, phone, birthday) -> str:
    key_parts = (
        first_name or "",
        last_name or "",
        birthday or "",
        str(phone) if phone else "",
    )
    encoded_key_parts = "".join(key_parts).encode('utf-8')
    return "uid:" + hashlib.md5(encoded_key_parts).hexdigest()


def get_score(store: Store, phone=None, email=None, birthday=None, gender=None, first_name=None, last_name=None):
    primary_key = get_cache_key(first_name, last_name, phone, birthday)
    if cached_data := store.cache_get(primary_key=primary_key):
        return cached_data[0][1]

    score = 0
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5

    store.cache_set((primary_key, score))
    return score


def get_interests(store: Store, client_id: int) -> list[str]:
    if cached_data := store.cache_get(f"cid:{client_id}"):
        return cached_data[0][1]
    return []
