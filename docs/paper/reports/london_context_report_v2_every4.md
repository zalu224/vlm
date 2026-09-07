# Paired comparison: `london_naive` (A) vs `london_context` (B)

Judged file: `judged_v2_every4.jsonl`.
Frames judged: A = 72, B = 72, paired = 71.
B better on 37 frames, worse on 28, tied on 6.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 1.915 | 1.847 | -0.068 |
| actionability | 3.268 | 3.25 | -0.018 |
| spatial accuracy | 2.746 | 2.264 | -0.482 |
| conciseness | 2.648 | 3.861 | 1.213 |
| hallucination | 2.69 | 3.736 | 1.046 |
| **overall** | **2.653** | **2.992** | **0.339** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.859 | 4.258 |
| p90 latency (s) | 5.856 | 4.413 |
| mean words / instruction | 63.764 | 9.931 |
| conciseness, computed (1–5) | 1.556 | 5.0 |
| unique instructions / frames | 0.972 | 0.361 |
| share of most common instruction | 0.028 | 0.167 |

Most common A: "The person should continue walking forward, staying close to the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they can walk at a steady pace. If they encounter any changes in the sidewalk, such as a curb or a change in the surface, they should adjust their pace accordingly. The person should also be aware of any pedestrians"  
Most common B: "A person is partly blocked directly ahead. Move forward."

## Largest improvements (B over A)

**Frame 000032** (Δ +2.40)
- cues: Free space: left=blocked, centre=partly blocked, right=blocked. Obstacles: bus (right, near); truck (left, near); person (centre, mid); person (centre, far).
- A: The person wearing the camera should continue walking forward. The sidewalk appears clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's surface or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles.
- B: The bus is partly blocking the way ahead. Move slightly to the right.

**Frame 000036** (Δ +2.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, far); person (right, far); person (left, far); person (right, far).
- A: The next step for the blind person walking in the image is to continue walking down the sidewalk. The person should be aware of the visual cues around them, such as the street, buildings, and other pedestrians. They should also be mindful of any tactile cues, such as the texture of the sidewalk or the presence of tactile paving, which can guide them. If they encounter any obstacles or changes in the
- B: The bus is partly blocking the way ahead. Move slightly to the right.

**Frame 000016** (Δ +2.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, far); person (centre, far); person (centre, far); person (centre, far).
- A: The person should continue walking forward, staying close to the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they can walk at a steady pace. If they encounter any changes in the sidewalk, such as a curb or a change in the surface, they should adjust their pace accordingly. The person should also be aware of any pedestrians
- B: The way ahead is partly blocked. Move slightly to the right.

**Frame 000020** (Δ +2.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, near); person (right, near); person (centre, mid); person (right, mid).
- A: The person wearing the camera should continue walking forward. The camera is capturing the scene ahead, so they can rely on the visual information provided by the camera to navigate. If they encounter any obstacles or changes in the environment, they should adjust their pace or direction accordingly. The camera will help them stay aware of their surroundings and avoid any potential hazards.
- B: The way ahead is partly blocked. Move slightly to the right.

**Frame 000128** (Δ +2.20)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: bus (right, far); person (centre, far); person (centre, far); person (centre, far).
- A: The image shows a street scene with a roundabout and a statue in the center. There are construction signs indicating that the road ahead is closed. Here’s what you should do next:

1. **Listen for Traffic Signals**: Use your white cane to scan the area and listen for any traffic signals. If there are traffic lights, ensure they are green before proceeding.

2. **Check for Pedest
- B: The road ahead is clear. Move slightly to the right.

**Frame 000024** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, mid); bus (centre, far); trash can (left, far); car (right, far).
- A: The person should continue walking straight ahead. The street appears to be clear, and there are no immediate obstacles. The bus and other vehicles are parked or moving at a safe distance. The person should maintain a steady pace and be aware of any pedestrians or cyclists who might be crossing the street.
- B: The bus is partly blocking the way ahead. Move slightly to the right.

**Frame 000048** (Δ +2.00)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); bus (right, far); bus (centre, far); car (right, far).
- A: The person should continue walking forward, staying close to the sidewalk. They should be aware of the van parked on the right side of the street and any pedestrians or vehicles that might be approaching. The person should also be mindful of the tree trunk on the right side of the image, as it might obstruct their path. If they encounter any obstacles, they should use their white cane to navigate around them.
- B: The person is directly ahead. Move slightly to the right.

**Frame 000040** (Δ +1.80)
- cues: Free space: left=blocked, centre=partly blocked, right=clear. Obstacles: bicycle (left, near); person (centre, far); bicycle (centre, far); person (centre, far).
- A: The person should continue walking forward, as the path appears clear and there are no immediate obstacles. The sidewalk is visible, and there are no pedestrians or vehicles directly in front of them. The person should maintain a steady pace and be aware of their surroundings, including any potential changes in the environment.
- B: The bicycle is partly blocking the way ahead. Move slightly to the right.

**Frame 000144** (Δ +1.80)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: trash can (right, mid); person (right, far); person (right, far); bicycle (centre, far).
- A: The person should continue walking forward, as the path appears clear and there are no immediate obstacles. The trees and bicycles suggest a pedestrian-friendly area, so it's safe to proceed. If the person feels comfortable, they can look around to see if there are any specific directions they need to take or if they want to stop and explore the area further.
- B: The path is clear ahead. Move forward.

**Frame 000280** (Δ +1.80)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: car (right, mid); car (centre, mid); car (left, mid); car (right, far).
- A: The next step in your walk would be to choose two stations you would like to see between. You can ask for directions or suggestions from someone you are with, or you can use your phone to search for the locations and get directions. If you need assistance, you can ask for help from a guide dog or a sighted companion.
- B: The way ahead is clear. Move forward.

## Largest regressions (B under A)

**Frame 000168** (Δ -2.60)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, far); person (centre, far); truck (right, far); motorcycle (centre, far).
- A: As you continue walking, you will soon reach Trafalgar Square. Keep moving forward and you should be able to see the square ahead.
- B: A person is near directly ahead. Move forward.

**Frame 000276** (Δ -2.60)
- cues: Free space: left=blocked, centre=clear, right=blocked. Obstacles: person (left, near); person (left, mid); car (left, far); person (centre, far).
- A: The person wearing the camera should continue walking down the sidewalk. The camera is capturing the surroundings, including the Charing Cross Station entrance. The person should stay close to the entrance and follow the path that leads into the station. The text overlay indicates that the walk to the station is under five minutes, so the person should proceed at a steady pace.
- B: The person ahead is partly blocking the way. Move forward.

**Frame 000260** (Δ -1.60)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, far); trash can (centre, far); person (centre, far); traffic light (left, far).
- A: The image shows a busy urban street with pedestrians, vehicles, and buildings. Here are some steps you can follow to navigate safely:

1. **Listen for Traffic Sounds**: Pay attention to the sounds of vehicles, especially cars, buses, and bicycles. This will help you gauge the traffic flow and any potential hazards.

2. **Observe Traffic Signals**: Look for traffic lights and follow their instructions.
- B: The bus is partly blocking the way ahead. Move forward.

**Frame 000100** (Δ -1.20)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: person (right, far); person (right, far); person (right, far); person (centre, far).
- A: The blind person should continue walking forward, following the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they should maintain a steady pace. If they encounter any changes in the sidewalk, such as a change in texture or a curb, they should be prepared to adjust their walking path accordingly.
- B: The person ahead is directly ahead. Move slightly to the left.

**Frame 000164** (Δ -1.20)
- cues: Free space: left=partly blocked, centre=clear, right=blocked. Obstacles: person (left, near); person (centre, far); person (right, far); bicycle (centre, far).
- A: The sign in the image indicates that buses on the 19, 38, N19, and N38 routes are on diversion. To the left, you can see St Martin-in-the-Fields church, which you visited in a previous video. Since the buses are on diversion, you should take the left turn towards the church. After reaching the church, you can continue walking
- B: A person is near directly ahead. Move forward.
