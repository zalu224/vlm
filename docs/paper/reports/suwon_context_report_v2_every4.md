# Paired comparison: `suwon_naive` (A) vs `suwon_context` (B)

Judged file: `judged_v2_every4.jsonl`.
Frames judged: A = 74, B = 74, paired = 73.
B better on 51 frames, worse on 15, tied on 7.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 1.603 | 1.216 | -0.387 |
| actionability | 2.63 | 3.027 | 0.397 |
| spatial accuracy | 2.151 | 1.838 | -0.313 |
| conciseness | 2.493 | 3.878 | 1.385 |
| hallucination | 2.507 | 3.973 | 1.466 |
| **overall** | **2.277** | **2.786** | **0.509** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.928 | 4.149 |
| p90 latency (s) | 6.2 | 4.284 |
| mean words / instruction | 65.351 | 8.014 |
| conciseness, computed (1–5) | 1.23 | 5.0 |
| unique instructions / frames | 0.986 | 0.257 |
| share of most common instruction | 0.027 | 0.351 |

Most common A: "The person wearing the camera should continue walking forward, following the flow of the crowd. They should be mindful of their surroundings and the people around them to avoid any potential obstacles. If they feel the need to stop or turn, they should do so cautiously and ensure they are in a safe position before proceeding."  
Most common B: "Two steps ahead, there's a person. Move forward."

## Largest improvements (B over A)

**Frame 000164** (Δ +3.60)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: truck (right, far); car (centre, far).
- A: The image you've provided shows a signboard with various businesses and their contact information, including restaurants and other establishments. Given that you are a blind person walking and using a camera, here are the steps you can follow:

1. **Identify the Signboard**: Use your camera to take a close-up photo of the signboard. Focus on the text and logos to identify the businesses listed.

2
- B: The truck is far ahead and clear. Move forward.

**Frame 000260** (Δ +2.60)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: person (centre, far).
- A: The image shows a narrow alleyway with a sign on the right side that appears to be in Korean. The sign has a red circle with a line through it, which typically indicates a prohibition or warning. The text on the sign seems to be related to a specific area or rule, possibly related to smoking or a similar activity, as there is a cigarette symbol inside the red circle. Given the context
- B: The path is clear ahead. Move forward.

**Frame 000268** (Δ +2.40)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); person (centre, far); person (centre, far); person (centre, far).
- A: The person wearing the camera should continue walking forward, as the path appears clear and there are no immediate obstacles. The camera is capturing the environment, so the person can rely on the visual information provided by the camera to navigate safely. If the person encounters any changes in the environment, such as a change in the sidewalk, a crosswalk, or a street, they should pause and listen for any sounds
- B: The path is clear ahead. Move forward.

**Frame 000084** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: trash can (right, far).
- A: The image you've provided appears to be taken from a camera worn by a blind person who is walking through a market. Here are some steps you can take next:

1. **Identify the Surroundings**: Use your surroundings to orient yourself. Notice the sounds of the market, such as the rustling of food packaging and the chatter of people. This can help you locate the entrance or exit of
- B: Two steps ahead, there's a trash can. Move forward.

**Frame 000168** (Δ +1.80)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: truck (right, mid); car (centre, far).
- A: The image you've provided shows a street scene with various signs, including some that appear to be for businesses or services. Since you are a blind person walking, here are some steps you can follow:

1. **Identify Your Surroundings**: Use your white cane or guide dog to scan the area. The cane should help you detect any obstacles or changes in the terrain, such as steps or uneven
- B: The truck is partly blocked ahead. Move forward.

**Frame 000288** (Δ +1.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); person (left, far); person (centre, far); person (left, far).
- A: The image shows a shopping mall with various stores and clothing racks. Here are some suggestions for what you might do next:

1. **Continue Walking**: Keep walking in the direction you are currently going. The path appears to be clear and there are no immediate obstacles.

2. **Listen for Sounds**: Continue listening for any sounds that might indicate the presence of people, objects, or obstacles. This can
- B: The path is clear ahead. Move forward.

**Frame 000072** (Δ +1.60)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (centre, mid); person (centre, mid); car (left, far).
- A: The person should continue walking forward, following the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they can proceed at a steady pace. If they encounter any changes in the sidewalk, such as a change in the surface or a curb, they should be prepared to adjust their walking path accordingly.
- B: Two steps ahead, there's a person. Move forward.

**Frame 000136** (Δ +1.40)
- cues: Free space: left=blocked, centre=blocked, right=clear. Obstacles: none detected.
- A: The image you provided appears to be taken from a camera mounted on a blind person, as it captures the scene from a first-person perspective. Here are the steps you should take next:

1. **Assess the Surroundings**: Look around to identify any obstacles, such as parked cars, pedestrians, or uneven surfaces. The sidewalk appears to be clear, but be cautious of any hidden hazards like po
- B: The car is directly ahead. Move forward.

**Frame 000140** (Δ +1.40)
- cues: Free space: left=clear, centre=clear, right=partly blocked. Obstacles: shopping cart (right, near); truck (left, far); bicycle (left, far); car (centre, far).
- A: The image you provided shows a street scene with various shops, signs, and vehicles. Here are some steps you can follow to navigate safely:

1. **Listen for Sounds**: Pay attention to the sounds around you. The sounds of vehicles, people, and ambient noise can help you gauge your surroundings and identify potential hazards.

2. **Use Your Cane**: If you are using a white cane,
- B: The truck is directly ahead. Move forward.

**Frame 000184** (Δ +1.40)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: car (left, near); person (centre, mid); car (centre, far); car (centre, far).
- A: The image you've provided shows a street scene with buildings, shops, and parked cars. Since you are walking and the image is from a camera worn by a blind person, here are some steps you can follow:

1. **Listen for Sounds**: Pay attention to the sounds around you. Listen for the movement of vehicles, people, and any other environmental sounds that can help you navigate the area.
- B: The car on your left is partly blocked. Move forward.

## Largest regressions (B under A)

**Frame 000000** (Δ -1.60)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (right, mid); person (centre, far); person (left, far).
- A: The person wearing the camera should proceed cautiously, as there is a person standing in the middle of the walkway. The individual should stop and wait for the person in the traditional attire to move out of the way. Once the person in the traditional attire has moved, the blind person can continue walking. It's important to be patient and respectful of others in public spaces.
- B: Two steps ahead, there's a person. Move forward.

**Frame 000064** (Δ -1.60)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (centre, far); person (centre, far); person (centre, far); person (centre, far).
- A: Based on the image, it appears you are walking on a sidewalk in an urban area. Here are some steps you can follow to continue your walk safely:

1. **Stay on the Sidewalk**: Continue walking on the sidewalk. The yellow tactile paving on the sidewalk should guide you in the right direction.

2. **Be Aware of Your Surroundings**: Keep your ears open for any sounds that
- B: Two steps ahead, there's a person. Move forward.

**Frame 000068** (Δ -1.60)
- cues: Free space: left=blocked, centre=partly blocked, right=partly blocked. Obstacles: bus (centre, far); person (centre, far); person (centre, far); person (centre, far).
- A: The person should continue walking forward, following the tactile paving on the sidewalk. The tactile paving will guide them in the direction they need to go. If they encounter any obstacles, such as the bus or pedestrians, they should stop and assess the situation before proceeding. If they need to cross the street, they should use the crosswalk and ensure that it is safe to do so.
- B: Two steps ahead, there's a person. Move forward.

**Frame 000004** (Δ -1.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, far); person (right, far); person (centre, far); person (right, far).
- A: The person wearing the camera should continue walking forward, as the path appears clear and there are no immediate obstacles. The person should be cautious of the yellow tactile paving on the ground, which indicates a change in the surface or a potential hazard. The person should also be aware of the pedestrians around, as there are people walking in the area. If the person encounters any obstacles or feels the need to stop
- B: Two steps ahead, there's a person. Move forward.

**Frame 000212** (Δ -1.40)
- cues: Free space: left=partly blocked, centre=clear, right=partly blocked. Obstacles: person (right, mid); person (left, mid); person (left, mid); person (right, far).
- A: The person wearing the camera should look for the pedestrian crossing signal, which is currently red, indicating that it is not safe to cross the street. Once the signal changes to green, they should cross the street at the designated crosswalk. It's important to stay on the sidewalk and avoid crossing in the middle of the street. If there are no crosswalks, they should look for a safe spot
- B: The person on your right is near. Move forward.
