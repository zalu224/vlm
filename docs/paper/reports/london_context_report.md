# Paired comparison: `london_naive` (A) vs `london_context` (B)

Frames judged: A = 285, B = 285, paired = 285.
B better on 69 frames, worse on 156, tied on 60.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 3.151 | 2.274 | -0.877 |
| actionability | 3.888 | 2.87 | -1.018 |
| spatial accuracy | 3.126 | 2.358 | -0.768 |
| conciseness | 2.93 | 2.537 | -0.393 |
| hallucination | 4.86 | 4.116 | -0.744 |
| **overall** | **3.591** | **2.831** | **-0.76** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.845 | 4.258 |
| p90 latency (s) | 5.978 | 4.389 |
| mean words / instruction | 63.256 | 9.853 |
| unique instructions / frames | 0.965 | 0.144 |
| share of most common instruction | 0.014 | 0.168 |

Most common A: "The person wearing the camera should continue walking forward. The sidewalk appears to be clear, and there are no immediate obstacles in the path. The person should maintain a steady pace and be aware of their surroundings. If they encounter any changes in the environment, such as a change in the sidewalk's texture or the presence of other pedestrians, they should adjust their walking speed and be prepared to navigate any potential obstacles"  
Most common B: "A person is partly blocked directly ahead. Move forward."

## Largest improvements (B over A)

**Frame 000005** (Δ +4.00)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: none detected.
- A: The image you provided shows a view from a camera worn by a blind person, likely a smart camera or a similar assistive device. The scene appears to be a busy urban area, possibly near a subway or train station, given the visible signage and the bustling environment. Here are some steps you can take next:

1. **Listen for Sounds**: Focus on the sounds around you. Listen for the
- B: The way ahead is clear. Continue straight.

**Frame 000053** (Δ +1.20)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: trash can (right, near); bus (right, far); person (centre, far); car (centre, far).
- A: The camera you are using is likely a device that provides audio feedback to assist visually impaired individuals in navigating their environment. Based on the image, here are the next steps you should take:

1. **Listen for the audio feedback**: The camera should be providing you with audio cues about the environment. It might be indicating the presence of obstacles, such as the black box in the foreground, or other pedestrians
- B: The bus is directly ahead. Move slightly to the right.

**Frame 000038** (Δ +1.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, far); bicycle (left, far); truck (centre, far); person (left, far).
- A: The image shows a street scene with bicycles parked on the sidewalk, a road, and buildings in the background. The camera appears to be positioned on the person's chest, capturing the environment as they walk. Here are the next steps you can take:

1. **Look for the Road**: Since the camera is on your chest, you should be able to hear the sounds of the street. Listen for
- B: The truck is partly blocking the way ahead. Move slightly to the right.

**Frame 000002** (Δ +0.80)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: traffic light (right, mid); traffic light (right, mid); person (right, mid); person (right, mid).
- A: The image shows a busy street scene with a clear view of the road and surrounding buildings. To navigate from Leicester Square to Charing Cross, you can follow these steps:

1. **Identify Your Current Location**: You are at Leicester Square, as indicated by the sign and the surrounding architecture.
2. **Determine Your Destination**: Your destination is Charing Cross.
3. **Cross the Road
- B: A person is directly ahead, and a traffic light is at knee height. Cross the street.

**Frame 000020** (Δ +0.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, near); person (right, near); person (centre, mid); person (right, mid).
- A: The person wearing the camera should continue walking forward. The camera is capturing the scene ahead, so they can rely on the visual information provided by the camera to navigate. If they encounter any obstacles or changes in the environment, they should adjust their pace or direction accordingly. The camera will help them stay aware of their surroundings and avoid any potential hazards.
- B: The way ahead is partly blocked. Move slightly to the right.

**Frame 000029** (Δ +0.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, mid); person (centre, mid); bus (right, far); person (centre, far).
- A: The person wearing the camera should continue walking forward. The camera is capturing the scene ahead, so they can rely on the visual information provided by the camera to navigate. If they encounter any obstacles or changes in the environment, they should adjust their pace or direction accordingly. The camera will help them stay aware of their surroundings and avoid any potential hazards.
- B: The bus is partly blocking the way ahead. Move slightly to the right.

**Frame 000039** (Δ +0.80)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: bicycle (left, mid); bicycle (centre, far); person (left, far); truck (right, far).
- A: The image shows a street scene with bicycles parked on the sidewalk, a van parked on the street, and some pedestrians. Here’s what you can do next:

1. **Look for the tactile paving**: If you are walking on a street, look for the tactile paving, which is a series of raised dots or bumps on the sidewalk. These are designed to guide visually impaired pedestrians.

2. **
- B: The truck is partly blocking the way ahead. Move slightly to the right.

**Frame 000044** (Δ +0.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); motorcycle (left, far); person (centre, far); person (centre, far).
- A: The blind person should continue walking forward, following the sidewalk. They should be aware of the bollard in front of them and adjust their pace to avoid it. The sidewalk appears to be clear ahead, so they can proceed at a steady pace. If they encounter any obstacles or changes in the environment, they should use their other senses, such as listening for sounds or feeling the ground, to navigate
- B: The person in the center is partly blocking the way. Move slightly to the right.

**Frame 000060** (Δ +0.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: car (right, near); person (centre, far); person (left, far); person (left, far).
- A: The blind person should continue walking forward, following the sidewalk. They should be aware of the cone and the trash bin in front of them. The cone might indicate a temporary obstacle, so they should be cautious and avoid it. The trash bin is a fixed object and should not pose a risk. The person should maintain a steady pace and be mindful of any other pedestrians or obstacles in their path.
- B: The car is directly ahead. Move slightly to the right.

**Frame 000127** (Δ +0.80)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (left, mid); bus (right, far); car (left, far); person (centre, far).
- A: The image shows a busy urban area with a clear view of the street and surrounding buildings. Here are the steps you can follow:

1. **Cross the Street Safely**: Look for a pedestrian crossing or a safe spot to cross the street. Ensure there are no oncoming vehicles and that it is safe to cross.

2. **Listen for Traffic Sounds**: Use your hearing to identify the direction and
- B: The road ahead is clear. Move slightly to the right.

## Largest regressions (B under A)

**Frame 000000** (Δ -4.00)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (right, mid); traffic light (right, mid); person (centre, mid); traffic light (right, mid).
- A: The image shows a busy urban street with a clear view of a pedestrian crossing and a traffic light. Here’s what you should do next:

1. **Look at the Traffic Light**: Observe the traffic light to determine if it is safe to cross the street. If the light is red, you should wait until it turns green.
2. **Listen for Traffic**: Use your listening skills to identify
- B: A person is directly ahead, and a traffic light is at knee height. Cross the street.

**Frame 000130** (Δ -3.20)
- cues: Free space: left=blocked, centre=clear, right=clear. Obstacles: bus (right, far); person (centre, far); person (centre, far); traffic light (centre, far).
- A: The image shows a road ahead that is closed, with a sign indicating "Road Ahead Closed Access Only" and a diversion sign pointing left. There are also traffic cones and a barrier blocking the road. Given this information, you should:

1. **Stop and look around** to ensure there are no vehicles or pedestrians approaching from the direction of the closed road.
2. **Listen for any traffic or
- B: The road ahead is clear. Move slightly to the right.

**Frame 000218** (Δ -3.20)
- cues: Free space: left=clear, centre=partly blocked, right=blocked. Obstacles: person (centre, mid); traffic light (right, far); truck (right, far); person (centre, far).
- A: The next step for the blind person is to enter the underground station. The entrance is clearly visible in front of them, with a set of stairs leading down. The person should follow these steps:

1. **Locate the Entrance**: The entrance is marked by a sign that reads "UNDERGROUND" and has a circular symbol with a red circle and a diagonal line through it, indicating the London Underground
- B: A person is partly blocked directly ahead. Move forward.

**Frame 000140** (Δ -3.00)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: traffic light (centre, far); person (centre, far); person (centre, far); traffic light (right, far).
- A: The traffic light is green, indicating that it is safe for you to cross the street. However, it's important to be cautious and ensure that there are no oncoming vehicles or pedestrians before proceeding. Look both ways to confirm that it is safe to cross. If you see any vehicles or pedestrians, wait until they have passed before crossing. Once it is clear, you can proceed across the street.
- B: The road ahead is clear. Move slightly to the right.

**Frame 000156** (Δ -2.80)
- cues: Free space: left=clear, centre=clear, right=clear. Obstacles: person (centre, near); person (right, mid); motorcycle (right, mid); bicycle (right, mid).
- A: The person should continue walking forward, as the path appears clear and there are no immediate obstacles. The person can use the tactile guide lines on the ground to navigate safely. If they encounter any changes in the environment, such as a change in the surface or the presence of other pedestrians, they should be prepared to adjust their path accordingly. The person should also be aware of any audible cues, such as
- B: A person is near directly ahead. Move forward.
