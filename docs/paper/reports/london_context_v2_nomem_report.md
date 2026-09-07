# Paired comparison: `london_naive` (A) vs `london_context_v2_nomem` (B)

Judged file: `judged.jsonl`.
Frames judged: A = 285, B = 285, paired = 285.
B better on 110 frames, worse on 102, tied on 73.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 3.151 | 3.046 | -0.105 |
| actionability | 3.888 | 3.782 | -0.106 |
| spatial accuracy | 3.126 | 3.056 | -0.07 |
| conciseness | 2.93 | 3.214 | 0.284 |
| hallucination | 4.86 | 4.263 | -0.597 |
| **overall** | **3.591** | **3.472** | **-0.119** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.845 | 4.748 |
| p90 latency (s) | 5.978 | 4.875 |
| mean words / instruction | 63.256 | 9.94 |
| conciseness, computed (1–5) | 1.607 | 4.888 |
| unique instructions / frames | 0.965 | 0.467 |
| share of most common instruction | 0.014 | 0.06 |

Most common A: "The person wearing the camera should continue walking forward. The sidewalk appears to be clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's texture or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles"  
Most common B: "The centre is partly blocked. Slow down and keep to the right."

## Largest improvements (B over A)

**Frame 000249** (Δ +3.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: bus (right, mid); person (right, mid); person (left, far); person (left, far).
- A: The person should continue walking forward, as the bus is moving away from them. The bus has a "First Bus" logo, which indicates it is part of the FirstGroup bus company. The bus is on the right side of the road, and there are no immediate obstacles in the path. The sidewalk is clear, and there are no pedestrians or vehicles directly in front of them. The person should
- B: The bus is close ahead. Slow down and keep to the left.

**Frame 000002** (Δ +2.60)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: traffic light (right, mid); traffic light (right, mid); person (right, mid); person (right, mid).
- A: The image shows a busy street scene with a clear view of the road and surrounding buildings. To navigate from Leicester Square to Charing Cross, you can follow these steps:

1. **Identify Your Current Location**: You are at Leicester Square, as indicated by the sign and the surrounding architecture.
2. **Determine Your Destination**: Your destination is Charing Cross.
3. **Cross the Road
- B: Continue walking. There's a traffic light and a person ahead on your right.

**Frame 000246** (Δ +2.60)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, far); traffic light (right, far); traffic light (right, far); trash can (left, far).
- A: Based on the image, it appears you are walking down a street in an urban area. Here are some steps you can follow to navigate safely:

1. **Listen for Sounds**: Continue listening for the sounds of traffic, pedestrians, and any other environmental noises that can help you gauge your surroundings and potential hazards.

2. **Observe the Sidewalk**: Look for any changes in the sidewalk,
- B: The centre is partly blocked. There's a person far ahead. Continue walking, but keep to the right.

**Frame 000282** (Δ +2.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=clear. Obstacles: car (centre, near); car (right, mid); car (centre, far); car (centre, far).
- A: The next station you want to see a walk between is the one located to the east of this area. You can walk straight ahead and turn right at the next intersection to reach it.
- B: The car in the centre is near. Slow down and keep to the right.

**Frame 000284** (Δ +2.40)
- cues: Free space: left=blocked, centre=clear, right=clear. Obstacles: car (left, near); car (right, far); car (centre, far); car (centre, far).
- A: The image shows a street scene with a large, ornate building in the background. There are several cars parked or moving on the street. Here are some steps you can take next:

1. **Listen for Sounds**: Pay attention to the sounds around you. Listen for the movement of vehicles, people, and any other environmental noises that can help you navigate the area.

2. **Use Your Surround
- B: Continue. There's a car close ahead.

**Frame 000224** (Δ +2.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: person (centre, far); bus (centre, far); person (left, far); trash can (left, far).
- A: The blind person should continue walking forward, as the path appears clear and there are no immediate obstacles. The red double-decker bus and the ice cream stand are visible, indicating that the person is in an urban area. The person should maintain a steady pace and be aware of any changes in the environment, such as the presence of pedestrians or vehicles. If the person encounters any obstacles or changes in the
- B: The centre is partly blocked. There's a person far ahead. Slow down and keep to the right.

**Frame 000160** (Δ +1.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, mid); person (right, far); person (left, far); person (centre, far).
- A: The person should continue walking straight ahead. There are no immediate obstacles or hazards visible in the immediate path. The person can maintain their current pace and direction.
- B: The centre is partly blocked. Slow down and keep to the left.

**Frame 000281** (Δ +1.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: car (right, mid); car (centre, mid); car (left, mid); car (right, far).
- A: The next station you want to see a walk between is the one located between the two stations mentioned in the text. You can proceed to walk between these two stations.
- B: The centre is partly blocked. There's a car directly ahead. Continue walking, but keep to the right.

**Frame 000283** (Δ +1.60)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: car (right, far); car (centre, far); car (centre, far); person (right, far).
- A: The next station you want to see a walk between is the one you mentioned. You can continue walking in the direction you are currently going. If you need assistance, feel free to ask for directions.
- B: Continue walking. There's a car far ahead on the right.

**Frame 000091** (Δ +1.20)
- cues: Free space: left=partly blocked, centre=blocked, right=blocked. Obstacles: person (centre, near); person (right, near); person (left, mid); person (centre, far).
- A: The person wearing the camera should continue walking forward. The camera is capturing the scene ahead, so they can rely on the visual information provided by the camera to navigate. If they encounter any obstacles or changes in the environment, they can adjust their path accordingly. The camera will help them stay aware of their surroundings and ensure they are moving in the right direction.
- B: STOP. There's a person directly ahead.

## Largest regressions (B under A)

**Frame 000000** (Δ -3.20)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (right, mid); traffic light (right, mid); person (centre, mid); traffic light (right, mid).
- A: The image shows a busy urban street with a clear view of a pedestrian crossing and a traffic light. Here’s what you should do next:

1. **Look at the Traffic Light**: Observe the traffic light to determine if it is safe to cross the street. If the light is red, you should wait until it turns green.
2. **Listen for Traffic**: Use your listening skills to identify
- B: Continue walking. There's a person ahead and to the right.

**Frame 000120** (Δ -3.20)
- cues: Free space: left=partly blocked, centre=clear, right=blocked. Obstacles: person (left, mid); person (left, mid); person (centre, far).
- A: The person should continue walking forward, following the tactile guide on the sidewalk. The guide will help them navigate the street safely. If they encounter any obstacles or changes in the sidewalk, they should be prepared to adjust their path. The person should also be aware of any traffic signs and pedestrian signals to ensure they cross the street safely.
- B: Continue walking. There's a person ahead and to the right.

**Frame 000129** (Δ -3.20)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: bus (right, far); person (centre, far).
- A: The image shows a street scene with road signs indicating "No access for HGV" and "Road Ahead Closed Access Only." There are also traffic cones and a statue in the background. Given the road signs, it appears that the road ahead is closed for heavy goods vehicles (HGVs). Since you are blind and using a camera, you should:

1. **Listen for any announcements or instructions
- B: Continue. There's a bus far ahead on the right.

**Frame 000047** (Δ -2.60)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (centre, far); person (right, far); trash can (left, far); person (right, far).
- A: The person should continue walking forward, staying close to the sidewalk. They can use the tactile guide on the sidewalk to navigate. If they encounter any obstacles, such as the tree trunk or the cardboard box, they should move around them carefully. The person should also be aware of any pedestrians or vehicles on the street and adjust their pace accordingly. If they need to cross the street, they should look both
- B: Continue walking. There's a person far ahead on the right.

**Frame 000109** (Δ -2.40)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: person (centre, far); person (right, far); person (centre, far); person (centre, far).
- A: The next step for the blind person walking in this image is to continue straight ahead. The "Diversion ENDS" sign indicates that the detour or alternate route has concluded, and the person should now follow the main path. The sidewalk appears clear, and there are no immediate obstacles or hazards visible. The person should maintain a steady pace and be aware of any pedestrians or cyclists around them.
- B: Continue. There's a person far ahead on the right.
