import json
import itertools

prompts = []
id_counter = 1

# Generate 50 Hard Coding Prompts
coding_topics = ["Rust thread-safe B-Tree", "C++ lock-free queue", "Redis Lua rate limiter", "C memory-mapped JSON parser", "CUDA tiled matrix mult", "React virtualization hook", "Go Huffman + RLE compressor", "Solidity NFT fractional standard", "Python A* 3D pathfinding", "PostgreSQL recursive BOM cost"]
coding_constraints = ["Optimize for O(1) time complexity.", "Guarantee zero heap allocations.", "Ensure absolute cache locality.", "Bypass standard library limitations.", "Ensure strictly wait-free algorithms."]
for idx, (topic, constraint) in enumerate(itertools.product(coding_topics, coding_constraints)):
    prompts.append({"id": id_counter, "category": "Coding Generation", "prompt": f"Write a complete implementation of: {topic}. Constraint: {constraint}"})
    id_counter += 1

# Generate 50 Hard Reasoning Prompts
reasoning_topics = ["The Grandfather Paradox", "Universal Basic Income", "Arrow of Time and Entropy", "Utilitarian self-driving cars", "Byzantine Generals Problem", "Many-Worlds interpretation", "Information Paradox in Black Holes", "Ship of Theseus via biological cells", "Simulated Universe hypothesis", "Game theory of nuclear deterioration"]
reasoning_constraints = ["Critique the foundational logic using deductive reasoning.", "Formulate an original resolution bridging physics and philosophy.", "Extrapolate the economic meta-effects over a 100-year timescale.", "Debunk the counter-arguments using historical precedents.", "Break down the systemic vulnerabilities in a 5-paragraph thesis."]
for idx, (topic, constraint) in enumerate(itertools.product(reasoning_topics, reasoning_constraints)):
    prompts.append({"id": id_counter, "category": "Medium Reasoning", "prompt": f"Analyze the following paradox/concept: {topic}. {constraint}"})
    id_counter += 1

# Generate 50 Hard Chat Prompts
chat_topics = ["A Victorian mother angry about computers", "A passive-aggressive corporate budget denial", "Explaining Inception backwards", "UN alien invasion speech", "AI writing poetry to a toaster", "Imposter syndrome as a dragon fairy tale", "Hot dogs as sandwiches debate", "High-stakes poisoned coffee scene", "Sentient house plant complaining", "Defensive raw chicken Yelp review"]
chat_constraints = ["Write entirely in iambic pentameter.", "Ensure the text is extremely persuasive yet subtle.", "Limit the response to exactly 100 words.", "Utilize an unreliable narrator format.", "End on an unresolved plot twist."]
for idx, (topic, constraint) in enumerate(itertools.product(chat_topics, chat_constraints)):
    prompts.append({"id": id_counter, "category": "Chat & Generation", "prompt": f"Write a creative piece concerning: {topic}. Style condition: {constraint}"})
    id_counter += 1

# Generate 50 Hard Multimodal Vision Prompts
vision_topics = ["Chaotic traffic intersection", "Chest X-ray indicating pneumonia", "Architectural blueprint layout", "Ancient Latin manuscript", "Complex chemical IUPAC diagram", "Satellite Amazon deforestation map", "Dense forest fungi cross-section", "Capacitor circuit board schematic", "Python codebase screenshot with memory leak", "Retail store customer heat map"]
vision_constraints = ["Exhaustively list every anomaly matching the parameters.", "Calculate and output specific geometric/mathematical values derived from the visual data.", "Identify the root cause of the visual anomaly and propose a structural fix.", "Translate or classify all objects present into taxonomical/technical notation.", "Analyze the sub-textual visual cues indicating systemic failure."]
for idx, (topic, constraint) in enumerate(itertools.product(vision_topics, vision_constraints)):
    prompts.append({"id": id_counter, "category": "Multimodal Vision", "prompt": f"Analyze the provided image representing {topic}. Task: {constraint}"})
    id_counter += 1

with open("c:/Users/lenovo/Desktop/San/Fun_Projects/LLM Bench Test/prompts/benchmark_prompts.json", "w") as f:
    json.dump(prompts, f, indent=4)

print(f"Generated {len(prompts)} prompts across 4 categories.")
