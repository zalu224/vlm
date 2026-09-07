# Paired comparison: `london_naive` (A) vs `london_context_v1_nomem` (B)

Judged file: `judged_v2_every4.jsonl`.
Frames judged: A = 72, B = 72, paired = 69.
B better on 42 frames, worse on 18, tied on 9.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 1.915 | 1.529 | -0.386 |
| actionability | 3.268 | 3.657 | 0.389 |
| spatial accuracy | 2.746 | 2.586 | -0.16 |
| conciseness | 2.648 | 4.0 | 1.352 |
| hallucination | 2.69 | 4.129 | 1.439 |
| **overall** | **2.653** | **3.18** | **0.527** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.859 | 4.162 |
| p90 latency (s) | 5.856 | 4.275 |
| mean words / instruction | 63.764 | 8.958 |
| conciseness, computed (1–5) | 1.556 | 5.0 |
| unique instructions / frames | 0.972 | 0.708 |
| share of most common instruction | 0.028 | 0.083 |

Most common A: "The person should continue walking forward, staying close to the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they can walk at a steady pace. If they encounter any changes in the sidewalk, such as a curb or a change in the surface, they should adjust their pace accordingly. The person should also be aware of any pedestrians"  
Most common B: "Two steps ahead, there's a person. Move forward."

## Largest improvements (B over A)

**Frame 000020** (Δ +3.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, near); person (right, near); person (centre, mid); person (right, mid).
- A: The person wearing the camera should continue walking forward. The camera is capturing the scene ahead, so they can rely on the visual information provided by the camera to navigate. If they encounter any obstacles or changes in the environment, they should adjust their pace or direction accordingly. The camera will help them stay aware of their surroundings and avoid any potential hazards.
- B: Two steps ahead, there's a person. Move slowly.

**Frame 000128** (Δ +2.60)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: bus (right, far); person (centre, far); person (centre, far); person (centre, far).
- A: The image shows a street scene with a roundabout and a statue in the center. There are construction signs indicating that the road ahead is closed. Here’s what you should do next:

1. **Listen for Traffic Signals**: Use your white cane to scan the area and listen for any traffic signals. If there are traffic lights, ensure they are green before proceeding.

2. **Check for Pedest
- B: The road ahead is clear. Continue straight.

**Frame 000108** (Δ +2.20)
- cues: Free space: left=blocked, centre=clear, right=clear. Obstacles: person (centre, far); person (right, far); motorcycle (right, far); person (centre, far).
- A: The person should continue walking forward, following the sidewalk. The path appears clear, and there are no immediate obstacles. The person should maintain a steady pace and be aware of any changes in the environment, such as the presence of vehicles or pedestrians. If there are any sounds or vibrations that indicate the presence of a vehicle, the person should be prepared to stop or adjust their path to avoid any potential hazards
- B: The path ahead is clear. Continue straight.

**Frame 000036** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, far); person (right, far); person (left, far); person (right, far).
- A: The next step for the blind person walking in the image is to continue walking down the sidewalk. The person should be aware of the visual cues around them, such as the street, buildings, and other pedestrians. They should also be mindful of any tactile cues, such as the texture of the sidewalk or the presence of tactile paving, which can guide them. If they encounter any obstacles or changes in the
- B: A person is directly ahead and to your right. Move forward carefully.

**Frame 000032** (Δ +1.80)
- cues: Free space: left=blocked, centre=partly blocked, right=blocked. Obstacles: bus (right, near); truck (left, near); person (centre, mid); person (centre, far).
- A: The person wearing the camera should continue walking forward. The sidewalk appears clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's surface or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles.
- B: The bus is directly ahead and partly blocked. Move forward slowly.

**Frame 000248** (Δ +1.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, mid); bus (right, mid); person (centre, far); person (right, far).
- A: Based on the image, it appears you are walking down a street in an urban area. Here are some steps you can take to continue your walk safely:

1. **Listen for Sounds**: Continue to listen for the sounds around you. The sound of the bus and other vehicles can help you gauge your surroundings and the distance to them. The sound of pedestrians can also be helpful.

2. **Ob
- B: A person is directly ahead. Walk forward.

**Frame 000264** (Δ +1.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: trash can (right, near); trash can (centre, mid); person (centre, far); person (centre, far).
- A: Based on the image, it appears you are walking down a busy street. Here are some steps you can take to navigate safely:

1. **Listen for Sounds**: Continue to listen for the sounds around you. The sounds of people talking, vehicles, and the environment can provide important clues about your surroundings.

2. **Observe the Sidewalk**: Look for any pedestrians or obstacles on the sidewalk
- B: Two steps ahead, there's a trash can. Move forward.

**Frame 000008** (Δ +1.60)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: person (right, far); person (right, far); person (right, far); person (right, far).
- A: The next step for the blind person would be to continue walking in the direction they are currently going, as indicated by the red barrier and the sign that points left. The sign also mentions "Leicester Square Station" and "Northern and Piccadilly Lines," which suggests that the person is near a train station. The person should be cautious and continue walking in the direction of the sign, as this
- B: The path is clear ahead. Walk forward.

**Frame 000016** (Δ +1.60)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, far); person (centre, far); person (centre, far); person (centre, far).
- A: The person should continue walking forward, staying close to the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they can walk at a steady pace. If they encounter any changes in the sidewalk, such as a curb or a change in the surface, they should adjust their pace accordingly. The person should also be aware of any pedestrians
- B: Two steps ahead, there's a person. Keep walking straight.

**Frame 000092** (Δ +1.60)
- cues: Free space: left=partly blocked, centre=clear, right=blocked. Obstacles: person (right, near); person (centre, far); person (right, far); person (right, far).
- A: The person wearing the camera should continue walking forward. The sidewalk appears to be clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's texture or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles
- B: Two steps ahead, there's a person. Move forward.

## Largest regressions (B under A)

**Frame 000220** (Δ -1.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, near); bus (left, far); person (right, far); person (right, far).
- A: The person should continue walking straight ahead. There are no immediate obstacles or hazards visible in the immediate path. The person can keep their pace steady and focus on the sounds around them to navigate safely.
- B: A person is directly ahead. Walk carefully.

**Frame 000060** (Δ -1.00)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: car (right, near); person (centre, far); person (left, far); person (left, far).
- A: The blind person should continue walking forward, following the sidewalk. They should be aware of the cone and the trash bin in front of them. The cone might indicate a temporary obstacle, so they should be cautious and avoid it. The trash bin is a fixed object and should not pose a risk. The person should maintain a steady pace and be mindful of any other pedestrians or obstacles in their path.
- B: Two steps ahead, there's a car. Keep walking straight.

**Frame 000112** (Δ -1.00)
- cues: Free space: left=partly blocked, centre=clear, right=blocked. Obstacles: person (left, near); car (centre, far); person (centre, far); traffic light (centre, far).
- A: The person should continue walking forward, following the sidewalk. They can use the tactile guide posts and the flow of pedestrians to navigate safely. The person should also be aware of any changes in the environment, such as the presence of vehicles, and should be prepared to stop or adjust their path as needed.
- B: A person is directly ahead. Walk forward.

**Frame 000244** (Δ -1.00)
- cues: Free space: left=blocked, centre=blocked, right=partly blocked. Obstacles: person (left, near); person (left, near); motorcycle (centre, far).
- A: The person should continue walking forward, staying close to the sidewalk. They should be aware of the orange plastic bag in their hand and ensure it does not obstruct their path. The person should also be mindful of any upcoming obstacles, such as the curb or other pedestrians. If they encounter any obstacles, they should use their cane to navigate around them.
- B: A person is close ahead. Move slowly.

**Frame 000100** (Δ -0.80)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: person (right, far); person (right, far); person (right, far); person (centre, far).
- A: The blind person should continue walking forward, following the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they should maintain a steady pace. If they encounter any changes in the sidewalk, such as a change in texture or a curb, they should be prepared to adjust their walking path accordingly.
- B: Two steps ahead, there's a person. Continue straight.
