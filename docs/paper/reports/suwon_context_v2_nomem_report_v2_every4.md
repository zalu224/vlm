# Paired comparison: `suwon_naive` (A) vs `suwon_context_v2_nomem` (B)

Judged file: `judged_v2_every4.jsonl`.
Frames judged: A = 74, B = 74, paired = 73.
B better on 58 frames, worse on 11, tied on 4.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 1.603 | 2.405 | 0.802 |
| actionability | 2.63 | 3.527 | 0.897 |
| spatial accuracy | 2.151 | 2.973 | 0.822 |
| conciseness | 2.493 | 3.838 | 1.345 |
| hallucination | 2.507 | 4.027 | 1.52 |
| **overall** | **2.277** | **3.354** | **1.077** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.928 | 4.658 |
| p90 latency (s) | 6.2 | 4.788 |
| mean words / instruction | 65.351 | 8.568 |
| conciseness, computed (1–5) | 1.23 | 4.865 |
| unique instructions / frames | 0.986 | 0.689 |
| share of most common instruction | 0.027 | 0.081 |

Most common A: "The person wearing the camera should continue walking forward, following the flow of the crowd. They should be mindful of their surroundings and the people around them to avoid any potential obstacles. If they feel the need to stop or turn, they should do so cautiously and ensure they are in a safe position before proceeding."  
Most common B: "STOP. There's a person directly ahead."

## Largest improvements (B over A)

**Frame 000092** (Δ +3.40)
- cues: Free space: left=partly blocked, centre=blocked, right=clear. Obstacles: person (left, far); person (right, far); person (right, far).
- A: The image you've provided appears to be taken from a camera worn by a blind person who is walking. To navigate and interact with the environment, here are some steps you can follow:

1. **Identify the Surroundings**: Use your white cane or guide dog to scan the area. The image shows a market stall with a sign in Korean. The stall appears to be selling various types of eggs
- B: STOP. There's a person directly ahead.

**Frame 000168** (Δ +3.40)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: truck (right, mid); car (centre, far).
- A: The image you've provided shows a street scene with various signs, including some that appear to be for businesses or services. Since you are a blind person walking, here are some steps you can follow:

1. **Identify Your Surroundings**: Use your white cane or guide dog to scan the area. The cane should help you detect any obstacles or changes in the terrain, such as steps or uneven
- B: STOP. There's a truck close ahead.

**Frame 000288** (Δ +3.40)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); person (left, far); person (centre, far); person (left, far).
- A: The image shows a shopping mall with various stores and clothing racks. Here are some suggestions for what you might do next:

1. **Continue Walking**: Keep walking in the direction you are currently going. The path appears to be clear and there are no immediate obstacles.

2. **Listen for Sounds**: Continue listening for any sounds that might indicate the presence of people, objects, or obstacles. This can
- B: Continue. There's a person far ahead on the left.

**Frame 000084** (Δ +3.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: trash can (right, far).
- A: The image you've provided appears to be taken from a camera worn by a blind person who is walking through a market. Here are some steps you can take next:

1. **Identify the Surroundings**: Use your surroundings to orient yourself. Notice the sounds of the market, such as the rustling of food packaging and the chatter of people. This can help you locate the entrance or exit of
- B: The centre is partly blocked. Slow down and keep to the left.

**Frame 000116** (Δ +3.20)
- cues: Free space: left=clear, centre=clear, right=partly blocked. Obstacles: person (left, far); person (left, far); person (centre, far); person (centre, far).
- A: The image shows a bustling street market with various stalls and shops. Here are some suggestions for navigating the area:

1. **Listen for Sounds**: Pay attention to the sounds around you. The rustling of fruits and vegetables, the chatter of people, and the occasional motorbike or car passing by can help you orient yourself and gauge the distance to different stalls.

2. **Use Your Cane**:
- B: Continue. There's a person far ahead on the left.

**Frame 000132** (Δ +3.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: truck (left, mid); person (centre, far); person (centre, far); car (centre, far).
- A: The image shows a street scene with a white truck, a few pedestrians, and a motorcycle parked on the side. The street appears to be in an urban area with shops and signs. Here are some steps you can take:

1. **Look for Obstacles**: Be aware of any obstacles such as parked vehicles, pedestrians, or other moving objects. The motorcycle and the truck are visible, so be
- B: The truck is close ahead. Slow down and keep to the right.

**Frame 000184** (Δ +3.00)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: car (left, near); person (centre, mid); car (centre, far); car (centre, far).
- A: The image you've provided shows a street scene with buildings, shops, and parked cars. Since you are walking and the image is from a camera worn by a blind person, here are some steps you can follow:

1. **Listen for Sounds**: Pay attention to the sounds around you. Listen for the movement of vehicles, people, and any other environmental sounds that can help you navigate the area.
- B: Continue. There's a person ahead and a car on the left.

**Frame 000228** (Δ +3.00)
- cues: Free space: left=blocked, centre=blocked, right=blocked. Obstacles: person (centre, near); person (left, near); person (centre, far); person (centre, far).
- A: The person wearing the camera should continue walking forward. The camera is capturing the environment ahead, so they can navigate based on the visual information provided. If they encounter any obstacles or changes in the environment, they can adjust their path accordingly. The camera will help them stay aware of their surroundings and avoid any potential hazards.
- B: STOP. There's a person directly ahead.

**Frame 000016** (Δ +2.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (right, mid); person (right, mid); person (centre, far).
- A: The person wearing the camera should continue walking forward, as the path appears clear and there are no immediate obstacles. The person should be aware of the tactile guide lines on the ground, which are designed to help guide visually impaired individuals. If the person encounters any changes in the path, such as a change in the tactile guide lines or a sudden obstacle, they should stop and assess the situation. If the
- B: Continue walking. There's a person ahead and to the right.

**Frame 000024** (Δ +2.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (right, far); person (centre, far); person (left, far).
- A: The person wearing the camera should continue walking forward, following the tactile paving on the ground. The tactile paving guides the person in the direction they should go. If the tactile paving leads them to a crosswalk, they should cross the street at the designated crosswalk. If they reach a stop sign or a traffic light, they should stop and wait for the signal to change before proceeding. If they encounter
- B: Continue walking. There's a person ahead and to the right.

## Largest regressions (B under A)

**Frame 000264** (Δ -2.60)
- cues: Free space: left=blocked, centre=clear, right=clear. Obstacles: person (centre, far); person (centre, far); person (centre, far).
- A: The image shows a narrow alleyway with a sign that appears to be in Korean. The alleyway leads to a brighter area where people are walking. Here are some steps you can take:

1. **Stay on the Path**: Continue walking straight ahead, following the path that leads out of the alleyway.
2. **Listen for Sounds**: Use your hearing to identify any obstacles or people ahead.
- B: Continue. There's a person far ahead.

**Frame 000248** (Δ -2.00)
- cues: Free space: left=blocked, centre=clear, right=blocked. Obstacles: none detected.
- A: The person should continue walking forward, as the alley appears to be clear ahead. There are no visible obstacles or hazards in the immediate path. The person can maintain their current pace and direction. If they encounter any obstacles or changes in the environment, they should be prepared to adjust their path accordingly.
- B: Continue. There's a person bending down a few steps ahead.

**Frame 000212** (Δ -1.20)
- cues: Free space: left=partly blocked, centre=clear, right=partly blocked. Obstacles: person (right, mid); person (left, mid); person (left, mid); person (right, far).
- A: The person wearing the camera should look for the pedestrian crossing signal, which is currently red, indicating that it is not safe to cross the street. Once the signal changes to green, they should cross the street at the designated crosswalk. It's important to stay on the sidewalk and avoid crossing in the middle of the street. If there are no crosswalks, they should look for a safe spot
- B: Continue walking. There's a person ahead on your right.

**Frame 000096** (Δ -1.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: none detected.
- A: The image you've provided shows the exterior of a butcher shop. To navigate safely, here are some steps you can follow:

1. **Listen for Sounds**: Use your hearing to identify the location of the shop. Listen for the sounds of people inside, the clinking of meat, or the hum of the shop's equipment.

2. **Use Your Cane**: If you haven't already,
- B: Continue. There's a person far ahead on the right.

**Frame 000156** (Δ -1.00)
- cues: Free space: left=blocked, centre=clear, right=clear. Obstacles: car (centre, far); car (centre, far); car (centre, far).
- A: The image shows a street scene with a gas station on the right and a signboard on the left displaying contact information for various countries. The street appears to be relatively quiet with a few parked cars and a person walking in the distance. Here are some suggestions for the next steps:

1. **Cross the Street**: If you need to cross the street, ensure there are no oncoming vehicles. Look
- B: Continue. There's a car far ahead.
