# Paired comparison: `london_naive` (A) vs `london_context_v1_nomem` (B)

Judged file: `judged.jsonl`.
Frames judged: A = 285, B = 285, paired = 285.
B better on 67 frames, worse on 159, tied on 59.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 3.151 | 2.084 | -1.067 |
| actionability | 3.888 | 2.902 | -0.986 |
| spatial accuracy | 3.126 | 2.319 | -0.807 |
| conciseness | 2.93 | 2.593 | -0.337 |
| hallucination | 4.86 | 4.172 | -0.688 |
| **overall** | **3.591** | **2.814** | **-0.777** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.845 | 4.157 |
| p90 latency (s) | 5.978 | 4.283 |
| mean words / instruction | 63.256 | 8.923 |
| conciseness, computed (1–5) | 1.607 | 4.993 |
| unique instructions / frames | 0.965 | 0.47 |
| share of most common instruction | 0.014 | 0.06 |

Most common A: "The person wearing the camera should continue walking forward. The sidewalk appears to be clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's texture or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles"  
Most common B: "A person is directly ahead. Walk forward."

## Largest improvements (B over A)

**Frame 000005** (Δ +4.00)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: none detected.
- A: The image you provided shows a view from a camera worn by a blind person, likely a smart camera or a similar assistive device. The scene appears to be a busy urban area, possibly near a subway or train station, given the visible signage and the bustling environment. Here are some steps you can take next:

1. **Listen for Sounds**: Focus on the sounds around you. Listen for the
- B: The way ahead is clear. Continue straight.

**Frame 000002** (Δ +3.20)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: traffic light (right, mid); traffic light (right, mid); person (right, mid); person (right, mid).
- A: The image shows a busy street scene with a clear view of the road and surrounding buildings. To navigate from Leicester Square to Charing Cross, you can follow these steps:

1. **Identify Your Current Location**: You are at Leicester Square, as indicated by the sign and the surrounding architecture.
2. **Determine Your Destination**: Your destination is Charing Cross.
3. **Cross the Road
- B: The traffic light is red ahead. Wait for it to turn green before crossing.

**Frame 000249** (Δ +3.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: bus (right, mid); person (right, mid); person (left, far); person (left, far).
- A: The person should continue walking forward, as the bus is moving away from them. The bus has a "First Bus" logo, which indicates it is part of the FirstGroup bus company. The bus is on the right side of the road, and there are no immediate obstacles in the path. The sidewalk is clear, and there are no pedestrians or vehicles directly in front of them. The person should
- B: The bus is partly blocking the path. Move slightly to the left.

**Frame 000003** (Δ +1.00)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: traffic light (right, mid); person (right, mid); traffic light (right, mid); person (right, mid).
- A: The image shows a street scene with a visible sign for Leicester Square and Charing Cross. To walk from Leicester Square to Charing Cross, you can follow these steps:

1. **Identify Your Current Location**: You are at Leicester Square, as indicated by the sign.
2. **Head Towards Charing Cross**: Charing Cross is located further down the street, so you should move forward in
- B: The traffic light is red ahead. Wait for it to turn green.

**Frame 000004** (Δ +1.00)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: traffic light (right, mid); person (centre, mid); traffic light (right, mid); person (right, mid).
- A: The image shows a busy street scene with a clear view of the road and surrounding buildings. To navigate from Leicester Square to Charing Cross, you can follow these steps:

1. **Identify Your Current Location**: You are at Leicester Square, as indicated by the sign in the background.
2. **Look for Directions**: Use your white cane or guide dog to scan the area for any visible signs
- B: The traffic light is red ahead. Wait for it to turn green.

**Frame 000023** (Δ +0.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, far); bus (left, far); trash can (left, far); truck (right, far).
- A: The person should continue walking straight ahead. The street appears to be clear, and there are no immediate obstacles. The bus and vehicles are parked, and the sidewalk is visible. The person should maintain a steady pace and be aware of any changes in the environment, such as pedestrians or vehicles moving.
- B: The bus is directly ahead and partly blocking the path. Move slightly to the right.

**Frame 000078** (Δ +0.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: motorcycle (right, far); person (centre, far); person (centre, far); tree (centre, far).
- A: The blind person should continue walking forward, following the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they should maintain a steady pace. If they encounter any changes in the sidewalk, such as a change in texture or a curb, they should be prepared to adjust their walking path accordingly.
- B: The path ahead is partly blocked. Walk carefully around the tree.

**Frame 000105** (Δ +0.80)
- cues: Free space: left=blocked, centre=partly blocked, right=clear. Obstacles: person (right, far); person (right, far).
- A: The person should continue walking forward, following the sidewalk. They can use their white cane to scan the ground and detect any obstacles. The sidewalk appears to be clear, so they should maintain a steady pace. If they encounter any changes in the sidewalk, such as a change in texture or a curb, they should be prepared to adjust their walking path accordingly.
- B: The sidewalk is partly blocked ahead. Walk carefully.

**Frame 000127** (Δ +0.80)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (left, mid); bus (right, far); car (left, far); person (centre, far).
- A: The image shows a busy urban area with a clear view of the street and surrounding buildings. Here are the steps you can follow:

1. **Cross the Street Safely**: Look for a pedestrian crossing or a safe spot to cross the street. Ensure there are no oncoming vehicles and that it is safe to cross.

2. **Listen for Traffic Sounds**: Use your hearing to identify the direction and
- B: A person is ahead and to your left. There's a bus far ahead and to your right. The road ahead is clear.

**Frame 000157** (Δ +0.80)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (centre, near); person (right, near); bicycle (right, near); person (left, near).
- A: The image shows a large, historic building with a clock tower, which appears to be St. Martin-in-the-Fields in London. There are people walking and cycling around the area. Here are some suggestions for what you can do next:

1. **Look for a landmark**: You can use the clock tower as a landmark to orient yourself. It's a well-known and easily identifiable feature in the
- B: A person is near directly ahead. Move slowly.

## Largest regressions (B under A)

**Frame 000000** (Δ -4.00)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (right, mid); traffic light (right, mid); person (centre, mid); traffic light (right, mid).
- A: The image shows a busy urban street with a clear view of a pedestrian crossing and a traffic light. Here’s what you should do next:

1. **Look at the Traffic Light**: Observe the traffic light to determine if it is safe to cross the street. If the light is red, you should wait until it turns green.
2. **Listen for Traffic**: Use your listening skills to identify
- B: A person is directly ahead, and a traffic light is at knee height. Cross the street.

**Frame 000129** (Δ -3.20)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: bus (right, far); person (centre, far).
- A: The image shows a street scene with road signs indicating "No access for HGV" and "Road Ahead Closed Access Only." There are also traffic cones and a statue in the background. Given the road signs, it appears that the road ahead is closed for heavy goods vehicles (HGVs). Since you are blind and using a camera, you should:

1. **Listen for any announcements or instructions
- B: The road ahead is clear. Continue straight.

**Frame 000174** (Δ -3.20)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: person (left, far); person (left, far); person (right, far); person (right, far).
- A: Based on the image, it appears you are walking in a public area with steps, a sidewalk, and some people around. Here are some suggestions for your next steps:

1. **Stay on the Sidewalk**: Continue walking on the sidewalk to avoid the steps and any potential hazards.
2. **Watch for Traffic Signals**: There are traffic lights visible, so be sure to check for any red
- B: Two steps ahead, there's a person. Continue straight.

**Frame 000240** (Δ -3.20)
- cues: Free space: left=blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, near); person (centre, far); person (centre, far); person (centre, far).
- A: The person should continue walking forward, following the sidewalk. They can use the tactile paving on the ground to guide their path. If they encounter a bus stop, they should be cautious and ensure they are in a safe position to board the bus. If they need to cross the street, they should look for a crosswalk and use the tactile paving to navigate safely across the road.
- B: A person is close ahead on your right. Walk straight ahead.

**Frame 000178** (Δ -3.00)
- cues: Free space: left=partly blocked, centre=clear, right=clear. Obstacles: traffic light (centre, far); person (left, far); person (left, far); person (centre, far).
- A: The person wearing the camera should look for the red traffic light, which indicates that they should not cross the street. They should wait until the light turns green before attempting to cross. Additionally, they should be aware of the pedestrians around them and any other potential obstacles in their path. If there are no other pedestrians, they can proceed cautiously, but always be prepared to stop if the light changes.
- B: The traffic light is red ahead. Walk straight ahead.
