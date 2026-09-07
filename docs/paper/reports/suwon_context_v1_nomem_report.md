# Paired comparison: `suwon_naive` (A) vs `suwon_context_v1_nomem` (B)

Judged file: `judged.jsonl`.
Frames judged: A = 295, B = 295, paired = 295.
B better on 101 frames, worse on 139, tied on 55.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 2.753 | 1.997 | -0.756 |
| actionability | 3.241 | 2.624 | -0.617 |
| spatial accuracy | 2.736 | 2.169 | -0.567 |
| conciseness | 2.614 | 2.346 | -0.268 |
| hallucination | 4.519 | 3.617 | -0.902 |
| **overall** | **3.173** | **2.551** | **-0.622** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.928 | 4.179 |
| p90 latency (s) | 5.895 | 4.446 |
| mean words / instruction | 66.034 | 8.641 |
| conciseness, computed (1–5) | 1.231 | 4.837 |
| unique instructions / frames | 0.973 | 0.62 |
| share of most common instruction | 0.007 | 0.078 |

Most common A: "The person wearing the camera should continue walking forward, as the path appears clear and there are no immediate obstacles. The person should be aware of the tactile guide lines on the ground, which are designed to help guide visually impaired individuals. If the person encounters any changes in the path, such as a change in the tactile guide lines or a sudden obstacle, they should stop and assess the situation. If the"  
Most common B: "Two steps ahead, there's a person. Move forward."

## Largest improvements (B over A)

**Frame 000173** (Δ +4.00)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: none detected.
- A: The image shows a street scene with various signs, including ones with different languages and flags, indicating a multicultural area. Given that the image is from a camera worn by a blind person, the next steps would involve:

1. **Identify the Surroundings**: Use the tactile information from the camera to identify the type of environment. The presence of signs with different languages and flags suggests a multicultural area,
- B: The path is clear ahead. Keep walking forward steadily.

**Frame 000083** (Δ +3.60)
- cues: Free space: left=clear, centre=blocked, right=blocked. Obstacles: none detected.
- A: The image you've provided shows a street food stall with various food items displayed. Since you are a blind person walking, here are some steps you can follow:

1. **Listen for Sounds**: Use your hearing to identify the sounds around you. Listen for the sounds of people talking, the clinking of dishes, or the rustling of food packaging. This can help you locate the stall and understand
- B: The way forward is blocked ahead. Please turn right toward the shops.

**Frame 000255** (Δ +3.20)
- cues: Free space: left=blocked, centre=clear, right=blocked. Obstacles: none detected.
- A: The image shows a narrow alleyway with a tiled floor and walls on either side. The walls appear to be made of concrete or a similar material, and there are some visible signs of wear and tear. The alleyway leads to a brighter area at the far end, where you can see some people and light.

Given that you are walking, here are some steps you can take:

1. **
- B: The path is clear ahead. Continue straight.

**Frame 000259** (Δ +3.20)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: none detected.
- A: The image shows a narrow alleyway with walls on both sides. The walls appear to be made of concrete and have some graffiti or markings on them. There is a sign on the right side of the alley, but the text is not clearly legible. The alley seems to be quite narrow and could be quite dark, especially if it's not well-lit. Here are some steps you can take
- B: The path ahead is clear. Continue straight.

**Frame 000139** (Δ +2.60)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: car (left, near); bicycle (left, far); truck (left, far); tree (centre, far).
- A: The image you provided shows a street scene with various shops and businesses. Here are some suggestions for navigating this area:

1. **Listen for Sounds**: Pay attention to the sounds around you. The rustling of clothes, the hum of the street, and the occasional voice of a passerby can provide clues about the environment and the layout of the street.

2. **Use Your Cane**: If
- B: The truck is partly behind you. Keep walking forward steadily.

**Frame 000153** (Δ +2.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: motorcycle (left, near); car (left, near); bench (centre, near); car (left, mid).
- A: The image you provided shows a street scene in South Korea, with various signs and buildings. Here are some steps you can follow to navigate safely:

1. **Listen for Sounds**: Pay attention to the sounds around you. The sounds of traffic, people, and ambient noise can give you clues about your surroundings and help you orient yourself.

2. **Use Your Cane**: If you have a white
- B: There's a motorcycle partly obscuring the sidewalk. Move cautiously ahead toward the right.

**Frame 000254** (Δ +2.20)
- cues: Free space: left=blocked, centre=clear, right=blocked. Obstacles: none detected.
- A: The camera you are using is designed to assist visually impaired individuals by providing audio feedback about their surroundings. Based on the image, it appears you are walking through a narrow alleyway. Here are the next steps you should take:

1. **Listen for Sounds**: Continue to listen for any sounds that might indicate the presence of obstacles, such as people, vehicles, or objects in the alley. This will
- B: The path is clear ahead. Continue straight.

**Frame 000049** (Δ +1.80)
- cues: Free space: left=blocked, centre=blocked, right=partly blocked. Obstacles: person (centre, near); person (centre, near); bus (left, far); car (left, far).
- A: The擬思詠柳<|endoftext|>{}{
FINN5P1SsSURE
GuidIdara
gMaps
 addCriteriony
- B: The person in front of you is close. Move cautiously ahead.

**Frame 000163** (Δ +1.80)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: motorcycle (centre, near); trash can (right, near); truck (right, far); car (centre, far).
- A: The image shows a street scene with various signs, including one that appears to be a directory for restaurants. The directory lists restaurants from different countries, including Thailand, Vietnam, and Cambodia. The signs are in multiple languages, including Thai, Russian, and Vietnamese. The directory also includes phone numbers for each restaurant.

Given that you are walking and the image is from a camera worn by a blind person,
- B: The motorcycle is ahead. Step forward slowly.

**Frame 000227** (Δ +1.80)
- cues: Free space: left=blocked, centre=blocked, right=blocked. Obstacles: person (centre, near); person (left, near); person (left, near); person (centre, far).
- A: The person wearing the camera should continue walking forward. The camera is designed to capture the environment around them, so they can rely on the visual information provided by the camera to navigate safely. If they encounter any obstacles or changes in the environment, they should adjust their pace or direction accordingly.
- B: The person ahead is close, so be cautious. Continue straight ahead.

## Largest regressions (B under A)

**Frame 000041** (Δ -3.20)
- cues: Free space: left=blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, near); person (centre, near); person (right, mid); person (centre, mid).
- A: The person wearing the camera should continue walking forward, following the sidewalk. They should be aware of the yellow tactile paving on the ground, which indicates a crossing or change in the sidewalk's direction. If they encounter any obstacles or changes in the sidewalk, they should use their white cane to navigate safely. They should also be mindful of the pedestrians and vehicles around them, as the street appears to be busy
- B: A cyclist is approaching quickly aheadft of you. Step cautiously aheadft.

**Frame 000065** (Δ -3.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: person (centre, mid); bus (left, mid); person (centre, far); person (centre, far).
- A: The person should continue walking forward, following the yellow tactile paving on the sidewalk. The tactile paving guides the person in the direction they should go. If they encounter any obstacles, they should use their white cane to scan the area and determine the safest path. The person should also be aware of any changes in the environment, such as the presence of vehicles or pedestrians, and adjust their pace and route accordingly
- B: A pedestrian is approaching aheadft of and slightly behind. Keep walking forward steadily.

**Frame 000066** (Δ -3.20)
- cues: Free space: left=blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, near); person (centre, far); person (centre, far); person (centre, far).
- A: The person wearing the camera should continue walking forward, following the tactile guide strip on the sidewalk. The strip will guide them in the direction they need to go. If they encounter any obstacles or changes in the sidewalk, they should use their white cane to scan the area and determine the safest path. They can also look for visual cues, such as signs or other pedestrians, to help navigate the area.
- B: A pedestrian is approaching aheadft of you. Step slightly forward.

**Frame 000001** (Δ -3.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (centre, far); person (left, far); person (left, far).
- A: The person wearing the camera should proceed cautiously, as there is a person dressed in traditional attire standing on the sidewalk. The individual should be aware of the person in traditional attire and ensure they do not obstruct the path. The person should also be mindful of the yellow tactile paving on the ground, which indicates a pedestrian crossing or a designated area for visually impaired individuals. The person should continue walking at a steady
- B: Two steps ahead, there's a person. Move forward.

**Frame 000027** (Δ -3.00)
- cues: Free space: left=blocked, centre=clear, right=blocked. Obstacles: trash can (left, mid); bus (left, far); person (centre, far); person (centre, far).
- A: The person should continue walking forward, following the yellow tactile paving on the sidewalk. The tactile paving guides the visually impaired person along the path. The person should be cautious of the street and any obstacles, such as the cart and the clothing rack, and should be prepared to stop or adjust their path as needed. The person should also be aware of any pedestrians or vehicles that may be approaching.
- B: The bus is directly ahead. Walk straight.
