# Paired comparison: `london_naive` (A) vs `london_context_v2_nomem` (B)

Judged file: `judged_v2_every4.jsonl`.
Frames judged: A = 72, B = 72, paired = 71.
B better on 50 frames, worse on 16, tied on 5.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 1.915 | 2.333 | 0.418 |
| actionability | 3.268 | 3.694 | 0.426 |
| spatial accuracy | 2.746 | 2.972 | 0.226 |
| conciseness | 2.648 | 3.875 | 1.227 |
| hallucination | 2.69 | 4.153 | 1.463 |
| **overall** | **2.653** | **3.405** | **0.752** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.859 | 4.763 |
| p90 latency (s) | 5.856 | 4.849 |
| mean words / instruction | 63.764 | 9.958 |
| conciseness, computed (1–5) | 1.556 | 4.917 |
| unique instructions / frames | 0.972 | 0.667 |
| share of most common instruction | 0.028 | 0.083 |

Most common A: "The person should continue walking forward, staying close to the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they can walk at a steady pace. If they encounter any changes in the sidewalk, such as a curb or a change in the surface, they should adjust their pace accordingly. The person should also be aware of any pedestrians"  
Most common B: "The centre is partly blocked. Slow down and keep to the left."

## Largest improvements (B over A)

**Frame 000152** (Δ +3.20)
- cues: Free space: left=partly blocked, centre=blocked, right=clear. Obstacles: person (centre, near); person (centre, mid); person (left, mid); bicycle (left, mid).
- A: The person wearing the camera should continue walking forward. They can use the tactile cues from the sidewalk and the street to navigate. If they encounter any obstacles, they can adjust their path accordingly. The person should also be aware of any pedestrians or cyclists around them and be prepared to communicate their intentions clearly.
- B: STOP. There's a person directly ahead.

**Frame 000160** (Δ +3.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, mid); person (right, far); person (left, far); person (centre, far).
- A: The person should continue walking straight ahead. There are no immediate obstacles or hazards visible in the immediate path. The person can maintain their current pace and direction.
- B: The centre is partly blocked. Slow down and keep to the left.

**Frame 000008** (Δ +2.40)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: person (right, far); person (right, far); person (right, far); person (right, far).
- A: The next step for the blind person would be to continue walking in the direction they are currently going, as indicated by the red barrier and the sign that points left. The sign also mentions "Leicester Square Station" and "Northern and Piccadilly Lines," which suggests that the person is near a train station. The person should be cautious and continue walking in the direction of the sign, as this
- B: Continue. There's a person far ahead on the right.

**Frame 000032** (Δ +2.40)
- cues: Free space: left=blocked, centre=partly blocked, right=blocked. Obstacles: bus (right, near); truck (left, near); person (centre, mid); person (centre, far).
- A: The person wearing the camera should continue walking forward. The sidewalk appears clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's surface or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles.
- B: The bus is near on the right. Slow down and keep to the left.

**Frame 000072** (Δ +2.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, mid); person (left, far); person (centre, far); bicycle (centre, far).
- A: The person wearing the camera should continue walking forward. They can use the tactile cues from the sidewalk and the objects around them to navigate safely. If they encounter any obstacles, they should pause, assess the situation, and then continue walking. The person should also be aware of any changes in the environment, such as the presence of bicycles or pedestrians, and adjust their pace and path accordingly.
- B: The centre is partly blocked. There's a person directly ahead. Slow down and keep to the right.

**Frame 000076** (Δ +2.40)
- cues: Free space: left=clear, centre=clear, right=partly blocked. Obstacles: person (right, near); person (centre, far); person (centre, far); car (right, far).
- A: The person wearing the camera should continue walking forward. The sidewalk appears to be clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's texture or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles
- B: Continue walking. There's a person near on the right.

**Frame 000248** (Δ +2.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, mid); bus (right, mid); person (centre, far); person (right, far).
- A: Based on the image, it appears you are walking down a street in an urban area. Here are some steps you can take to continue your walk safely:

1. **Listen for Sounds**: Continue to listen for the sounds around you. The sound of the bus and other vehicles can help you gauge your surroundings and the distance to them. The sound of pedestrians can also be helpful.

2. **Ob
- B: The centre is partly blocked. Slow down and keep to the left.

**Frame 000020** (Δ +2.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, near); person (right, near); person (centre, mid); person (right, mid).
- A: The person wearing the camera should continue walking forward. The camera is capturing the scene ahead, so they can rely on the visual information provided by the camera to navigate. If they encounter any obstacles or changes in the environment, they should adjust their pace or direction accordingly. The camera will help them stay aware of their surroundings and avoid any potential hazards.
- B: Continue walking. There's a person ahead and to the right.

**Frame 000024** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, mid); bus (centre, far); trash can (left, far); car (right, far).
- A: The person should continue walking straight ahead. The street appears to be clear, and there are no immediate obstacles. The bus and other vehicles are parked or moving at a safe distance. The person should maintain a steady pace and be aware of any pedestrians or cyclists who might be crossing the street.
- B: The person ahead is close, so slow down and keep to the left.

**Frame 000064** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=blocked, right=blocked. Obstacles: person (left, near); person (right, far); person (right, far); person (right, far).
- A: The person should continue walking forward, staying close to the sidewalk. They can use the tree as a guide to their right, ensuring they stay on the path. The sidewalk appears to be clear, so they can move at a steady pace. If they encounter any obstacles or changes in the sidewalk, they should be prepared to adjust their path accordingly.
- B: STOP. There's a person close ahead.

## Largest regressions (B under A)

**Frame 000044** (Δ -1.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); motorcycle (left, far); person (centre, far); person (centre, far).
- A: The blind person should continue walking forward, following the sidewalk. They should be aware of the bollard in front of them and adjust their pace to avoid it. The sidewalk appears to be clear ahead, so they can proceed at a steady pace. If they encounter any obstacles or changes in the environment, they should use their other senses, such as listening for sounds or feeling the ground, to navigate
- B: Continue. There's a person far ahead on the left.

**Frame 000084** (Δ -1.20)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: person (left, far); person (centre, far); trash can (right, far); person (centre, far).
- A: The next step for the blind person walking in this area would be to continue walking forward, following the sidewalk. The person should be aware of the street and any potential obstacles, such as the black pole in the foreground, which might be a streetlight or a decorative post. The person should also be mindful of the pedestrians and any vehicles that might be approaching. If there are any tactile clues, such
- B: Continue. There's a person far ahead on the left.

**Frame 000136** (Δ -1.20)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: bus (centre, far); traffic light (centre, far); person (centre, far); person (right, far).
- A: Based on the image, it appears that the person is walking down a street with a clear path ahead. Here are the steps you can follow:

1. **Cross the Street**: The traffic lights are green, indicating that it is safe to cross the street. Look for any oncoming traffic and ensure it has stopped before crossing.

2. **Watch for Vehicles**: Be cautious of any vehicles that might
- B: Continue. There's a bus far ahead.

**Frame 000148** (Δ -1.20)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: car (right, near); bicycle (left, mid); person (left, far); truck (centre, far).
- A: The person should continue walking straight ahead. The street appears to be clear, and there are no immediate obstacles or hazards visible. The sidewalk is wide, and there are trees and buildings on both sides, which can provide some natural guidance. The person should maintain a steady pace and be aware of any changes in the environment, such as pedestrians or vehicles. If there are any sounds or movements that indicate the
- B: Continue. There's a car near on the right.

**Frame 000168** (Δ -1.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, far); person (centre, far); truck (right, far); motorcycle (centre, far).
- A: As you continue walking, you will soon reach Trafalgar Square. Keep moving forward and you should be able to see the square ahead.
- B: The centre is partly blocked. Slow down and keep to the left.
