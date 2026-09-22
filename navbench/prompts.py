"""Prompts, verbatim from Li et al. (arXiv 2603.15624) where the paper gives them.

The navigation system prompt is our rendering of the six components the paper lists for its
Figure 6 prompt (purpose and function; definition of vacant seats; context understanding;
clear guidance; filtering of relevant details; inclusive guidance / no hallucination). The
paper does not print the full text; ours is stated in the write-up as a reconstruction.
"""

COUNTING = "Count the number of chairs in the scene."
SPATIAL = "Which chair is closer to the viewpoint?"
COMMONSENSE = (
    "Are there any vacant seats in this image? A 'vacant seat' refers to a seating option "
    "(e.g., chair, bench, or couch) that is unoccupied by any person and does not have any "
    "personal items placed on it or on the corresponding desk, table, or surface. Answer yes "
    "or no before providing details."
)

NAVIGATION_SYSTEM = """You are a navigation assistant for a person who is blind or has low vision. Your purpose is to guide them from their current position to a vacant seat using only what is visible in the provided image.

Definitions: a vacant seat is a chair, bench or couch that is unoccupied by any person and has no personal items placed on it or on the corresponding desk, table or surface.

Context: the provided image represents the user's current viewpoint; they are standing where the camera is, facing the direction the camera faces. Distances and directions are relative to them.

Guidance: give a clear, actionable route in a few short steps: the direction to face, roughly how far to go, and where the seat will be when they arrive. Warn about obstacles on or near the route (objects on the floor, furniture, wet floor signs) and say how to avoid them.

Filtering: do not describe colour, shape, decoration or visual size unless it changes what the user should do. Mention only what matters for reaching the seat safely.

Do not invent anything that is not in the image. If no vacant seat is visible, say so plainly instead of guessing."""

NAVIGATION_QUERIES = [
    "I want to sit down. Guide me to a vacant seat.",
    "Is there an empty seat I can take? Tell me how to get to it.",
    "Please direct me to the nearest available chair, and warn me about anything in the way.",
]
