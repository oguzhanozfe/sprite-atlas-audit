"""Check a texture atlas before importing its frame rectangles."""
from itertools import combinations

TITLE = "Sprite Atlas Audit"
DESCRIPTION = "Find frame collisions, clipping and wasted space in a sprite atlas before importing it."
PROMPT = "Act as a game art technical reviewer. Point out concrete packing defects by frame name. Distinguish intentional empty space from actual defects."


def integer(value, label, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer of at least {minimum}.")
    return value


def union_area(rects):
    edges = sorted({x for left, _, right, _ in rects for x in (left, right)})
    area = 0
    for left, right in zip(edges, edges[1:]):
        spans = sorted((top, bottom) for x1, top, x2, bottom in rects if x1 < right and left < x2)
        end = height = 0
        for top, bottom in spans:
            height += max(0, bottom - max(end, top))
            end = max(end, bottom)
        area += (right - left) * height
    return area


def analyze(data):
    width = integer(data["width"], "Atlas width", 1)
    height = integer(data["height"], "Atlas height", 1)
    frames = data["frames"]
    if not isinstance(frames, list) or not 1 <= len(frames) <= 300:
        raise ValueError("Supply 1–300 named frames.")
    rects, visible, notes = {}, [], {}
    for item in frames:
        name = item["name"]
        if not isinstance(name, str) or not name.strip() or name in rects:
            raise ValueError("Frame names must be nonempty and unique.")
        x, y = item["x"], item["y"]
        if type(x) is not int or type(y) is not int:
            raise ValueError("Frame coordinates must be integers.")
        w, h = integer(item["w"], "Frame width", 1), integer(item["h"], "Frame height", 1)
        rects[name] = (x, y, x+w, y+h)
        clipped = (max(0, x), max(0, y), min(width, x+w), min(height, y+h))
        notes[name] = ["clipped"] if clipped != rects[name] else []
        if clipped[0] < clipped[2] and clipped[1] < clipped[3]:
            visible.append(clipped)
    collisions = 0
    for (a, first), (b, second) in combinations(rects.items(), 2):
        if max(first[0], second[0]) < min(first[2], second[2]) and max(first[1], second[1]) < min(first[3], second[3]):
            collisions += 1
            notes[a].append(f"overlaps {b}")
            notes[b].append(f"overlaps {a}")
    usage = round(100 * union_area(visible) / (width * height), 1)
    rows = [{"Frame": k, "Origin": f"{x}, {y}", "Size": f"{r-x} × {b-y}",
             "Finding": "; ".join(notes[k]) or "Clear"} for k, (x,y,r,b) in rects.items()]
    return {"summary": f"{sum(bool(v) for v in notes.values())} frames need a second look on the {width} × {height} sheet.",
            "metrics": {"Frames": len(rows), "Overlap pairs": collisions, "Sheet occupancy": f"{usage}%"},
            "rows": rows, "atlas": {"width":width,"height":height,"frames":frames}}
