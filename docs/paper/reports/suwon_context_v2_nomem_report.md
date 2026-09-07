# Paired comparison: `suwon_naive` (A) vs `suwon_context_v2_nomem` (B)

Judged file: `judged.jsonl`.
Frames judged: A = 295, B = 295, paired = 295.
B better on 142 frames, worse on 85, tied on 68.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 2.753 | 2.993 | 0.24 |
| actionability | 3.241 | 3.542 | 0.301 |
| spatial accuracy | 2.736 | 3.034 | 0.298 |
| conciseness | 2.614 | 3.112 | 0.498 |
| hallucination | 4.519 | 3.563 | -0.956 |
| **overall** | **3.173** | **3.249** | **0.076** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.928 | 4.656 |
| p90 latency (s) | 5.895 | 4.796 |
| mean words / instruction | 66.034 | 8.549 |
| conciseness, computed (1–5) | 1.231 | 4.932 |
| unique instructions / frames | 0.973 | 0.397 |
| share of most common instruction | 0.007 | 0.085 |

Most common A: "The person wearing the camera should continue walking forward, as the path appears clear and there are no immediate obstacles. The person should be aware of the tactile guide lines on the ground, which are designed to help guide visually impaired individuals. If the person encounters any changes in the path, such as a change in the tactile guide lines or a sudden obstacle, they should stop and assess the situation. If the"  
Most common B: "STOP. There's a person directly ahead."

## Largest improvements (B over A)

**Frame 000095** (Δ +4.00)
- cues: Free space: left=clear, centre=blocked, right=blocked. Obstacles: none detected.
- A: The image you provided shows a butcher shop with various cuts of meat displayed in a refrigerated case. The shop has a sign with Korean text and a phone number. Here are the steps you can follow:

1. **Identify the Shop**: The sign indicates that this is a butcher shop, specifically one that sells meat. You can confirm this by the display of meat and the sign.

2.
- B: The centre is blocked. Stop.

**Frame 000174** (Δ +4.00)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: none detected.
- A: The image you provided shows a signpost with various flags and contact information for different countries. Since you are a blind person walking and using a camera, here are the steps you can follow:

1. **Identify the Surroundings**: Use your surroundings to orient yourself. Notice the buildings, signs, and any other landmarks that might help you navigate.

2. **Locate the Signpost**: Use
- B: Continue. There's a sign with a phone number for Russia ahead.

**Frame 000088** (Δ +3.20)
- cues: Free space: left=clear, centre=blocked, right=blocked. Obstacles: person (right, far); person (centre, far); person (centre, far).
- A: The image shows a food stall with various cooked items displayed on trays. Since you are blind and using a camera, here are the steps you can follow:

1. **Locate the Food Stall**: Use your surroundings to locate the food stall. You can ask for directions or use your sense of smell to identify the area where food is being cooked or served.

2. **Identify the Stall**:
- B: The centre is blocked. There's a person directly ahead. Please stop.

**Frame 000099** (Δ +3.20)
- cues: Free space: left=partly blocked, centre=blocked, right=clear. Obstacles: person (left, far); person (left, far).
- A: The image shows a green shopping cart attached to a motorized scooter, parked in front of a store. The store appears to be a convenience store or a small market, as indicated by the signage and the items displayed inside. Here are some steps you can take next:

1. **Check the Surroundings**: Look around to ensure there are no pedestrians, vehicles, or obstacles that might pose a risk
- B: STOP. There's a person far ahead on the left.

**Frame 000101** (Δ +3.20)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: motorcycle (right, near); person (left, far); person (left, far).
- A: The image shows a street food stall with a sign that appears to be in Korean. There is a motorcycle parked in front of the stall, and a person standing near the stall. Here are some steps you can take:

1. **Listen for Sounds**: Use your hearing to identify any sounds that might indicate the location of the stall or any nearby people. Listen for the sound of people talking, the
- B: Continue. There's a motorcycle to your right, close by.

**Frame 000142** (Δ +3.20)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: truck (left, far); bicycle (left, far); bicycle (left, far); bicycle (centre, far).
- A: The image you provided shows a street scene with various shops and businesses. Here are some suggestions for navigating this area:

1. **Listen for Sounds**: Pay attention to the sounds around you. The sounds of traffic, people, and shop noises can help you orient yourself and identify your location.

2. **Use Your Cane**: If you are using a white cane, use it to scan the ground
- B: Continue. There's a truck far ahead on the left.

**Frame 000149** (Δ +3.20)
- cues: Free space: left=clear, centre=clear, right=partly blocked. Obstacles: motorcycle (left, near); motorcycle (left, near); trash can (centre, mid); truck (left, far).
- A: The image you provided appears to be taken from a street scene in an urban area, likely in Korea, given the Korean text on the signs. Here are some steps you can follow to navigate this area:

1. **Listen for Sounds**: Pay attention to the sounds around you. The sounds of vehicles, people, and the environment can provide clues about the layout and any potential hazards.

2. **
- B: Continue. There's a trash can ahead.

**Frame 000153** (Δ +3.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: motorcycle (left, near); car (left, near); bench (centre, near); car (left, mid).
- A: The image you provided shows a street scene in South Korea, with various signs and buildings. Here are some steps you can follow to navigate safely:

1. **Listen for Sounds**: Pay attention to the sounds around you. The sounds of traffic, people, and ambient noise can give you clues about your surroundings and help you orient yourself.

2. **Use Your Cane**: If you have a white
- B: STOP. There's a motorcycle close ahead.

**Frame 000164** (Δ +3.20)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: truck (right, far); car (centre, far).
- A: The image you've provided shows a signboard with various businesses and their contact information, including restaurants and other establishments. Given that you are a blind person walking and using a camera, here are the steps you can follow:

1. **Identify the Signboard**: Use your camera to take a close-up photo of the signboard. Focus on the text and logos to identify the businesses listed.

2
- B: The centre is blocked. There's a car directly ahead. Stop.

**Frame 000165** (Δ +3.20)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: truck (right, far); car (centre, far).
- A: The image shows a street scene with various signs and businesses. Here’s what you can do next:

1. **Listen for Sounds**: Pay attention to the sounds around you. Listen for the movement of vehicles, people, or any other environmental sounds that might indicate the presence of pedestrians or vehicles.

2. **Observe the Surroundings**: Look for any visible signs or markings on the ground, such
- B: The centre is blocked. There's a car directly ahead. Stop.

## Largest regressions (B under A)

**Frame 000046** (Δ -3.20)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (left, mid); person (centre, mid); person (centre, mid); person (right, mid).
- A: The person wearing the camera should continue walking forward, following the yellow tactile paving on the sidewalk. The tactile paving guides the visually impaired person to the curb and helps them navigate the street safely. The person should be aware of the surrounding environment, including any pedestrians, vehicles, and obstacles. If they encounter any barriers or obstacles, they should use their white cane to detect them and adjust their path accordingly.
- B: Continue walking. There's a person directly ahead.

**Frame 000107** (Δ -3.20)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: person (right, mid); car (left, mid); person (centre, far).
- A: The person should continue walking forward, staying close to the right side of the street to avoid the parked car. They should be aware of the open market stalls on the right side and any pedestrians or vehicles that might be approaching. If they hear any approaching vehicles, they should stop and wait until the vehicle has passed before continuing.
- B: Continue. There's a person ahead and to the right.

**Frame 000234** (Δ -3.20)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: none detected.
- A: The camera wearer should continue walking forward, as the alley appears to be clear and there are no immediate obstacles or hazards visible. The alley seems to be a quiet, narrow passage between buildings, and there are no signs of any immediate danger. The person should maintain a steady pace and be aware of their surroundings, but there are no specific actions required at this moment.
- B: Continue. There's a person far ahead on the right.

**Frame 000239** (Δ -3.20)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: none detected.
- A: The camera wearer should continue walking forward, as the alley appears to be clear and safe. The person should be cautious of any obstacles or uneven surfaces, especially near the entrance of the shops. If there are any signs or objects that seem to be hazards, the person should avoid them. The person should also be mindful of the door on the right, as it might be the entrance to a shop.
- B: Continue. There's a person far ahead.

**Frame 000263** (Δ -3.20)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: person (centre, far).
- A: The image shows a narrow alleyway with a manhole cover in the foreground. The walls are worn and there are posters and signs on the walls. The alley appears to lead to a brighter area with more people visible in the distance. Here are some suggestions for the next steps:

1. **Be cautious of the manhole cover**: Ensure you step over it carefully to avoid tripping.
2.
- B: Continue. A person is far ahead.
