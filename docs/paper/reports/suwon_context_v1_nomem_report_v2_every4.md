# Paired comparison: `suwon_naive` (A) vs `suwon_context_v1_nomem` (B)

Judged file: `judged_v2_every4.jsonl`.
Frames judged: A = 74, B = 74, paired = 73.
B better on 49 frames, worse on 22, tied on 2.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 1.603 | 1.514 | -0.089 |
| actionability | 2.63 | 2.986 | 0.356 |
| spatial accuracy | 2.151 | 2.216 | 0.065 |
| conciseness | 2.493 | 3.676 | 1.183 |
| hallucination | 2.507 | 3.973 | 1.466 |
| **overall** | **2.277** | **2.873** | **0.596** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.928 | 4.178 |
| p90 latency (s) | 6.2 | 4.575 |
| mean words / instruction | 65.351 | 8.432 |
| conciseness, computed (1–5) | 1.23 | 4.784 |
| unique instructions / frames | 0.986 | 0.797 |
| share of most common instruction | 0.027 | 0.081 |

Most common A: "The person wearing the camera should continue walking forward, following the flow of the crowd. They should be mindful of their surroundings and the people around them to avoid any potential obstacles. If they feel the need to stop or turn, they should do so cautiously and ensure they are in a safe position before proceeding."  
Most common B: "Two steps ahead, there's a person. Move forward."

## Largest improvements (B over A)

**Frame 000236** (Δ +2.60)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (centre, far).
- A: As a blind person walking, you can proceed by following these steps:

1. **Listen for Sounds**: Continue to listen for any sounds that might indicate the presence of obstacles or people. The sounds of footsteps, doors, or other environmental noises can guide you.

2. **Feel for Obstacles**: Use your white cane to feel for any obstacles or changes in the ground. The cane can help you
- B: The person is ahead and to the right. Move forward.

**Frame 000260** (Δ +2.60)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: person (centre, far).
- A: The image shows a narrow alleyway with a sign on the right side that appears to be in Korean. The sign has a red circle with a line through it, which typically indicates a prohibition or warning. The text on the sign seems to be related to a specific area or rule, possibly related to smoking or a similar activity, as there is a cigarette symbol inside the red circle. Given the context
- B: The path ahead is clear. Walk forward.

**Frame 000288** (Δ +2.60)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); person (left, far); person (centre, far); person (left, far).
- A: The image shows a shopping mall with various stores and clothing racks. Here are some suggestions for what you might do next:

1. **Continue Walking**: Keep walking in the direction you are currently going. The path appears to be clear and there are no immediate obstacles.

2. **Listen for Sounds**: Continue listening for any sounds that might indicate the presence of people, objects, or obstacles. This can
- B: Two steps ahead, there's a person. Move slowly.

**Frame 000188** (Δ +2.40)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: person (centre, near); car (left, near); car (centre, mid); trash can (right, mid).
- A: The person should continue walking forward, as the path appears clear and there are no immediate obstacles. The street is relatively narrow, so it's important to stay aware of the surroundings and any pedestrians or vehicles that might be approaching. If there are any signs or markings on the ground, they should be mindful of them to ensure safe navigation.
- B: A person is near directly ahead. Walk carefully.

**Frame 000116** (Δ +2.20)
- cues: Free space: left=clear, centre=clear, right=partly blocked. Obstacles: person (left, far); person (left, far); person (centre, far); person (centre, far).
- A: The image shows a bustling street market with various stalls and shops. Here are some suggestions for navigating the area:

1. **Listen for Sounds**: Pay attention to the sounds around you. The rustling of fruits and vegetables, the chatter of people, and the occasional motorbike or car passing by can help you orient yourself and gauge the distance to different stalls.

2. **Use Your Cane**:
- B: Two steps ahead, keep left.

**Frame 000144** (Δ +2.20)
- cues: Free space: left=clear, centre=clear, right=partly blocked. Obstacles: bicycle (left, mid); motorcycle (centre, mid); motorcycle (centre, mid); motorcycle (centre, mid).
- A: The image you provided shows a street scene with various shops, signs, and vehicles. To navigate safely, here are some steps you can follow:

1. **Listen for Sounds**: Pay attention to the sounds around you. The sounds of vehicles, people, and the environment can provide clues about the layout and any potential hazards.

2. **Use Your Cane**: Use your white cane to scan the
- B: There's a motorcycle a bit closer ahead you. Keep walking forward steadily.

**Frame 000252** (Δ +2.20)
- cues: Free space: left=partly blocked, centre=clear, right=blocked. Obstacles: none detected.
- A: The camera you are using is designed to assist visually impaired individuals by providing audio feedback about their surroundings. Based on the image, it appears you are walking through a narrow alleyway. Here are the next steps:

1. **Listen for Sounds**: Use the audio feedback from the camera to identify any obstacles, such as walls, doors, or other people. The camera should be able to detect the distance
- B: The path is clear ahead. Continue straight.

**Frame 000024** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (right, far); person (centre, far); person (left, far).
- A: The person wearing the camera should continue walking forward, following the tactile paving on the ground. The tactile paving guides the person in the direction they should go. If the tactile paving leads them to a crosswalk, they should cross the street at the designated crosswalk. If they reach a stop sign or a traffic light, they should stop and wait for the signal to change before proceeding. If they encounter
- B: Two steps ahead, there's a person. Move slowly.

**Frame 000220** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=blocked, right=blocked. Obstacles: person (right, near); person (centre, near); person (left, mid); person (left, mid).
- A: The person wearing the camera should continue walking forward, following the flow of the crowd. They should be mindful of their surroundings and the people around them to avoid any potential obstacles. If they feel the need to stop or turn, they should do so cautiously and ensure they are in a safe position before proceeding.
- B: The path ahead is blocked. Move to the left.

**Frame 000112** (Δ +1.80)
- cues: Free space: left=partly blocked, centre=clear, right=partly blocked. Obstacles: person (centre, mid); bicycle (centre, mid); person (left, far); motorcycle (left, far).
- A: The image shows a street scene with a person riding a bicycle and a market on the right side. Here are some suggestions for the next steps:

1. **Cross the Street**: If you need to cross the street, look for a crosswalk or a safe spot to cross. Ensure there are no oncoming vehicles and that it is safe to cross.

2. **Observe the Market**: If
- B: A cyclist and motorcycle ahead of you. Keep walking forward steadily.

## Largest regressions (B under A)

**Frame 000000** (Δ -1.60)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (right, mid); person (centre, far); person (left, far).
- A: The person wearing the camera should proceed cautiously, as there is a person standing in the middle of the walkway. The individual should stop and wait for the person in the traditional attire to move out of the way. Once the person in the traditional attire has moved, the blind person can continue walking. It's important to be patient and respectful of others in public spaces.
- B: Two steps ahead, there's a person. Move forward.

**Frame 000284** (Δ -1.60)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (centre, far); person (right, far); person (centre, far); person (centre, far).
- A: Based on the image, it appears to be a shopping mall with various stores and people walking around. Here are some suggestions for what you might do next:

1. **Look for a Restroom**: If you need to use the restroom, look for a sign that says "화장실" (washroom) or "화장실" (restroom) and follow the direction indicated.

2
- B: Two steps ahead, there's a person. Move forward.

**Frame 000004** (Δ -1.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, far); person (right, far); person (centre, far); person (right, far).
- A: The person wearing the camera should continue walking forward, as the path appears clear and there are no immediate obstacles. The person should be cautious of the yellow tactile paving on the ground, which indicates a change in the surface or a potential hazard. The person should also be aware of the pedestrians around, as there are people walking in the area. If the person encounters any obstacles or feels the need to stop
- B: Two steps ahead, there's a person. Move forward.

**Frame 000100** (Δ -1.40)
- cues: Free space: left=clear, centre=partly blocked, right=blocked. Obstacles: motorcycle (centre, mid); person (left, far); person (left, far); person (left, far).
- A: The image shows a street scene with a small shop and a parked motorbike. Here are some steps you can take next:

1. **Listen for Sounds**: Use your hearing to identify any sounds that might indicate the presence of people, vehicles, or other environmental cues. This can help you navigate safely.

2. **Observe the Surroundings**: Look for any visible signs or markings that might indicate
- B: The action splits ahead
Ahead
<tool_call>
 addCriterion>()

**Frame 000076** (Δ -1.20)
- cues: Free space: left=blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, mid); bus (centre, far); car (left, far); car (left, far).
- A: The person should continue walking forward, following the sidewalk. They can use the tactile paving on the ground to guide their path. The tactile paving is a series of raised dots that indicate the edge of the sidewalk and can help the person navigate safely. If they encounter any obstacles, they should be cautious and adjust their path accordingly.
- B: A cyclist is approaching aheadft of and slightly right of you. Keep walking forward steadily.
