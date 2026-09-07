# Paired comparison: `suwon_naive` (A) vs `suwon_context` (B)

Frames judged: A = 295, B = 295, paired = 284.
B better on 69 frames, worse on 176, tied on 39.

## Rubric means (1–5, higher is better)

| Dimension | A | B | Δ (B−A) |
|---|---|---|---|
| safety | 2.753 | 1.423 | -1.33 |
| actionability | 3.241 | 2.144 | -1.097 |
| spatial accuracy | 2.736 | 1.694 | -1.042 |
| conciseness | 2.614 | 2.011 | -0.603 |
| hallucination | 4.519 | 3.085 | -1.434 |
| **overall** | **3.173** | **2.071** | **-1.102** |

## Latency and length

| Metric | A | B |
|---|---|---|
| median latency (s) | 4.928 | 4.144 |
| p90 latency (s) | 5.895 | 4.286 |
| mean words / instruction | 66.034 | 8.014 |
| unique instructions / frames | 0.973 | 0.088 |
| share of most common instruction | 0.007 | 0.349 |

Most common A: "The person wearing the camera should continue walking forward, as the path appears clear and there are no immediate obstacles. The person should be aware of the tactile guide lines on the ground, which are designed to help guide visually impaired individuals. If the person encounters any changes in the path, such as a change in the tactile guide lines or a sudden obstacle, they should stop and assess the situation. If the"  
Most common B: "Two steps ahead, there's a person. Move forward."

## Largest improvements (B over A)

**Frame 000255** (Δ +4.00)
- cues: Free space: left=blocked, centre=clear, right=blocked. Obstacles: none detected.
- A: The image shows a narrow alleyway with a tiled floor and walls on either side. The walls appear to be made of concrete or a similar material, and there are some visible signs of wear and tear. The alleyway leads to a brighter area at the far end, where you can see some people and light.

Given that you are walking, here are some steps you can take:

1. **
- B: The path is clear ahead. Move forward.

**Frame 000254** (Δ +3.20)
- cues: Free space: left=blocked, centre=clear, right=blocked. Obstacles: none detected.
- A: The camera you are using is designed to assist visually impaired individuals by providing audio feedback about their surroundings. Based on the image, it appears you are walking through a narrow alleyway. Here are the next steps you should take:

1. **Listen for Sounds**: Continue to listen for any sounds that might indicate the presence of obstacles, such as people, vehicles, or objects in the alley. This will
- B: The path is clear ahead. Move forward.

**Frame 000259** (Δ +3.20)
- cues: Free space: left=blocked, centre=clear, right=partly blocked. Obstacles: none detected.
- A: The image shows a narrow alleyway with walls on both sides. The walls appear to be made of concrete and have some graffiti or markings on them. There is a sign on the right side of the alley, but the text is not clearly legible. The alley seems to be quite narrow and could be quite dark, especially if it's not well-lit. Here are some steps you can take
- B: The path is clear ahead. Move forward.

**Frame 000084** (Δ +3.00)
- cues: Free space: left=partly blocked, centre=partly blocked, right=blocked. Obstacles: trash can (right, far).
- A: The image you've provided appears to be taken from a camera worn by a blind person who is walking through a market. Here are some steps you can take next:

1. **Identify the Surroundings**: Use your surroundings to orient yourself. Notice the sounds of the market, such as the rustling of food packaging and the chatter of people. This can help you locate the entrance or exit of
- B: Two steps ahead, there's a trash can. Move forward.

**Frame 000284** (Δ +2.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (centre, far); person (right, far); person (centre, far); person (centre, far).
- A: Based on the image, it appears to be a shopping mall with various stores and people walking around. Here are some suggestions for what you might do next:

1. **Look for a Restroom**: If you need to use the restroom, look for a sign that says "화장실" (washroom) or "화장실" (restroom) and follow the direction indicated.

2
- B: The path is clear ahead. Move forward.

**Frame 000291** (Δ +2.80)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: person (left, far); person (left, far); person (centre, far); person (centre, far).
- A: The image shows a shopping mall with various stores and people walking around. Here are some suggestions for what you can do next:

1. **Look for a Restroom**: If you need to use the restroom, look for signs that indicate restrooms. They are often located near the entrance or near the food court areas.

2. **Find a Seat**: If you need a break, look for a
- B: The path is clear ahead. Move forward.

**Frame 000101** (Δ +2.40)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: motorcycle (right, near); person (left, far); person (left, far).
- A: The image shows a street food stall with a sign that appears to be in Korean. There is a motorcycle parked in front of the stall, and a person standing near the stall. Here are some steps you can take:

1. **Listen for Sounds**: Use your hearing to identify any sounds that might indicate the location of the stall or any nearby people. Listen for the sound of people talking, the
- B: Two steps ahead, there's a motorcycle. Move forward.

**Frame 000163** (Δ +2.40)
- cues: Free space: left=clear, centre=blocked, right=clear. Obstacles: motorcycle (centre, near); trash can (right, near); truck (right, far); car (centre, far).
- A: The image shows a street scene with various signs, including one that appears to be a directory for restaurants. The directory lists restaurants from different countries, including Thailand, Vietnam, and Cambodia. The signs are in multiple languages, including Thai, Russian, and Vietnamese. The directory also includes phone numbers for each restaurant.

Given that you are walking and the image is from a camera worn by a blind person,
- B: The motorcycle is partly blocked ahead. Move forward.

**Frame 000167** (Δ +2.40)
- cues: Free space: left=clear, centre=blocked, right=partly blocked. Obstacles: truck (right, mid); car (centre, far); person (left, far).
- A: The image shows a street scene with various signs, including ones for different countries and businesses. Since you are walking and the image is from a camera worn by a blind person, here are some steps you can take:

1. **Listen for Sounds**: Pay attention to the sounds around you. Listen for the sounds of traffic, people, and any announcements that might be playing over a speaker.

2.
- B: The truck is partly blocked ahead. Move forward.

**Frame 000048** (Δ +1.80)
- cues: Free space: left=clear, centre=partly blocked, right=blocked. Obstacles: person (right, near); person (centre, near); person (centre, near); person (left, mid).
- A: Theoretically, ascribingselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselveselves
- B: Two steps ahead, there's a person. Move forward.

## Largest regressions (B under A)

**Frame 000234** (Δ -4.00)
- cues: Free space: left=clear, centre=clear, right=blocked. Obstacles: none detected.
- A: The camera wearer should continue walking forward, as the alley appears to be clear and there are no immediate obstacles or hazards visible. The alley seems to be a quiet, narrow passage between buildings, and there are no signs of any immediate danger. The person should maintain a steady pace and be aware of their surroundings, but there are no specific actions required at this moment.
- B: The person directly ahead is near. Move forward.

**Frame 000059** (Δ -3.40)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, near); person (centre, mid); car (left, far); person (centre, far).
- A: The person should continue walking forward, following the tactile paving on the sidewalk. The tactile paving provides a guide for visually impaired pedestrians. If the tactile paving ends, they should look for a crosswalk or a pedestrian signal to cross the street. If there are no immediate obstacles, they can continue walking in the direction they are currently going.
- B: Two steps ahead, there's a person. Move forward.

**Frame 000011** (Δ -3.20)
- cues: Free space: left=partly blocked, centre=partly blocked, right=partly blocked. Obstacles: person (right, mid); person (left, far); person (left, far); person (centre, far).
- A: The image shows a busy urban area with pedestrians and a person in the foreground who appears to be a vendor. Here are some suggestions for the blind person based on the image:

1. **Cross the Street Safely**: The pedestrian crossing is clearly marked with yellow tactile paving. Ensure the crossing is clear and safe before proceeding.
2. **Watch for Vehicles**: Be cautious of any vehicles approaching the crossing
- B: Two steps ahead, there's a person. Move forward.

**Frame 000029** (Δ -3.20)
- cues: Free space: left=blocked, centre=partly blocked, right=partly blocked. Obstacles: person (centre, mid); person (centre, mid); bus (left, far); bus (left, far).
- A: The person should continue walking forward, following the yellow tactile paving on the sidewalk. The tactile paving guides the person to the curb and helps them navigate the street. When they reach the curb, they should look for a crosswalk or a pedestrian signal to ensure it is safe to cross the street. If there is no crosswalk, they should wait for a safe moment to cross, being cautious of on
- B: Two steps ahead, there's a person. Move forward.

**Frame 000041** (Δ -3.20)
- cues: Free space: left=blocked, centre=partly blocked, right=partly blocked. Obstacles: person (left, near); person (centre, near); person (right, mid); person (centre, mid).
- A: The person wearing the camera should continue walking forward, following the sidewalk. They should be aware of the yellow tactile paving on the ground, which indicates a crossing or change in the sidewalk's direction. If they encounter any obstacles or changes in the sidewalk, they should use their white cane to navigate safely. They should also be mindful of the pedestrians and vehicles around them, as the street appears to be busy
- B: Two steps ahead, there's a person. Move forward.
