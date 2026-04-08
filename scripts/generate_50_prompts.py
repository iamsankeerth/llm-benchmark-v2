import json

prompts = []
id_counter = 1

# --- CODING (13 Prompts) ---
coding_queries = [
    "Write a highly optimized self-balancing Red-Black Tree implementation in Rust with complete edge case handling for thread-safety.",
    "Implement a lock-free concurrent queue in C++20 using atomic operations and memory order relaxed where appropriate.",
    "Draft a Python decorator that limits the execution rate of a function across a distributed cluster using Redis and Redis Lua scripts to ensure atomicity.",
    "Write a zero-allocation JSON parser in C that operates strictly on memory-mapped files.",
    "Develop a CUDA kernel in C++ for performing an optimally tiled matrix multiplication utilizing shared memory and loop unrolling.",
    "Create a React custom hook named useVirtualization that intelligently dynamically renders 100,000 deep-nested DOM items with O(1) scroll lag.",
    "Write a WebAssembly-compatible Go function that compresses an incoming byte stream using Huffman coding coupled with Run Length Encoding.",
    "Construct a completely verifiable smart contract in Solidity mapping a fractional NFT marketplace bypassing the ERC-1155 standard limitations with reentrancy guards.",
    "Implement from scratch the A* Pathfinding algorithm for a 3D isometric grid in Python where movement costs reflect simulated terrain elevation.",
    "Write a PostgreSQL stored procedure that recursively calculates the complete hierarchical supply chain cost for a manufacturing BOM (Bill of Materials).",
    "Develop a robust memory allocator (malloc/free clone) in C using segregated free lists and boundary tag coalescing.",
    "Provide a minimal working implementation of a Transformer attention head mechanism purely in base Python without NumPy or PyTorch.",
    "Solve the Byzantine Generals Problem for 5 nodes using a Python message passing interface simulating network latency."
]

for q in coding_queries:
    prompts.append({"id": id_counter, "category": "Coding Generation", "prompt": q})
    id_counter += 1

# --- REASONING (13 Prompts) ---
reasoning_queries = [
    "Three prisoners are placed in a room. Guard A tells the truth 50% of the time, Guard B lies if it's raining, and Guard C tells the truth if Guard A lied. If it's raining and Guard C says the sky is green, deduce the exact probability that Guard B is holding a red apple.",
    "Analyze the geopolitical implications of a hypothetical sudden global depletion of lithium reserves by 2030, contrasting the economic shifts between South America and East Asia.",
    "Explain quantum superposition using only vocabulary appropriate for a medieval blacksmith.",
    "Given the premises: 1. All flurbs are blorps. 2. Some blorps are glims. 3. No glims are flurbs. Prove or disprove whether a flurb could theoretically be a glim.",
    "If a perfectly spherical cow in a vacuum absorbs solar radiation but cannot emit infrared, calculate the timeline to its thermal explosion. Detail the thermodynamic principles.",
    "You are given 12 identical-looking coins, but one is counterfeit (either lighter or heavier). Using a balance scale exactly three times, how do you find the fake coin and determine if it is heavy or light?",
    "A self-driving car is programmed strictly with Utilitarian ethics. Suddenly, it must choose between hitting a renowned surgeon who treats 1,000 patients a year, or five elderly retirees. Break down how the algorithms value assignment models would compute this.",
    "Why does time seemingly only move forward, strictly referencing entropy and the Arrow of Time paradox without relying on general relativity?",
    "Evaluate the logical contradictions within the Grandfather Paradox and propose a resolution using the Many-Worlds interpretation of quantum mechanics.",
    "Deconstruct the economic argument that Universal Basic Income causes hyperinflation, using historical precedents from post-WWI Germany and contrasting modern fiat monetary policy.",
    "Assuming human memory is stored via chemical synapses, logically defend a biological mechanism wherein a memory could theoretically be erased specifically via targeted protein synthesis inhibitors.",
    "Explain how a 4-dimensional hypercube (tesseract) casts a 3-dimensional shadow, using analogies connecting 3D shapes casting 2D shadows.",
    "A sealed box contains a paradox: the box is empty, but the weight of the box fluctuates by 2 grams every hour. Reason out the most logical, physics-compliant explanation for this anomaly."
]

for q in reasoning_queries:
    prompts.append({"id": id_counter, "category": "Medium Reasoning", "prompt": q})
    id_counter += 1

# --- CHAT / GENERAL (12 Prompts) ---
chat_queries = [
    "Adopt the persona of an overbearing 19th-century Victorian mother who is furious that her son wants to study computer science. Scold him.",
    "Write a highly engaging, subtly passive-aggressive corporate email denying a coworker's request to use your project budget for an offsite pizza party.",
    "Explain the plot of the movie Inception backwards, starting from the end credits and regressing strictly in reverse chronological order.",
    "Draft a diplomatic speech for the United Nations announcing that hostile extraterrestrials will arrive in 48 hours, balancing transparency with panic control.",
    "Write a romantic poem about an AI falling in love with a toaster, strictly using iambic pentameter.",
    "Translate the concept of 'imposter syndrome' into a mythological fairy tale with a dragon who fears he isn't breathing real fire.",
    "Debate yourself on whether hot dogs are sandwiches. Spend exactly one paragraph firmly arguing yes, and one paragraph firmly arguing no.",
    "Compose a high-stakes thriller scene where the protagonist realizes the person they are drinking coffee with has poisoned the sugar, using only 50 words.",
    "Adopt the persona of a sentient house plant complaining about its owner's terrible watering schedule, emphasizing dramatic irony.",
    "Write an extremely defensive Yelp review from a restaurant owner who was accused of serving undercooked chicken, but the owner believes 'rare chicken' is a delicacy.",
    "Rewrite the iconic 'To be or not to be' soliloquy from Hamlet as if it were a modern hip-hop diss track.",
    "Describe the color blue to someone who was born completely blind without referencing the sky, ocean, or temperature."
]

for q in chat_queries:
    prompts.append({"id": id_counter, "category": "Chat & Generation", "prompt": q})
    id_counter += 1

# --- MULTIMODAL/VISION (12 Prompts) ---
# Note for Vision: The vision model will expect an image. Since we are bulk-testing via standard Ollama client in Phase 1,
# we need to simulate complex spatial reasoning queries. If the model accepts pure text for evaluating its text-reasoning, it works.
# Or these prompts can be paired with an image injection in an updated API.
vision_queries = [
    "Analyze the provided image of a chaotic traffic intersection. Count the exact number of pedestrian crossing violations and determine who has the legal right of way based on standard international traffic laws.",
    "Look at this chest X-ray. Identify the radiopacity in the lower left lobe and argue whether it is indicative of pneumonia or a mass, citing the specific rib borders it occludes.",
    "Given this architectural blueprint, calculate the total square footage of the master bedroom, excluding the walk-in closet space and structural support columns.",
    "Examine this photograph of an ancient manuscript. Transcribe the obscured Latin script in the top right corner and translate it to modern English, inferring missing letters based on context.",
    "Looking at this complex chemical structural formula diagram, identify the IUPAC name of the molecule and point out any chiral centers.",
    "Analyze the provided satellite image of the Amazon rainforest deforested zone. Estimate the square mileage of the burned area and predict the likely vector of the fire's spread based on wind topography.",
    "From this photograph of a dense forest floor, identify the three types of fungi present and classify which ones possess toxic properties.",
    "Examine this circuit board schematic. Trace the electrical path from the power relay to the capacitor C4 and deduce what failure would occur if Resistor R12 blew out.",
    "Look at this screenshot of a messy Python codebase. Visually locate where the memory leak in the nested loop occurs and strictly output the rewritten lines.",
    "Analyze this heat map of a retail store's customer flow. Identify the dead zones where product placement is failing and recommend structural layout changes to maximize foot traffic.",
    "Look at this historical painting. Identify the exact art period, the subtle lighting techniques used, and deduce the socio-political context the artist was critiquing via the background figures.",
    "Evaluate this geometric optical illusion. Explicitly describe why the brain perceives movement in the static image, citing lateral inhibition and retinal micro-saccades."
]

for q in vision_queries:
    # A flag structure allows the benchmarker to optionally load a mock image if the model supports multimodal inputs
    prompts.append({"id": id_counter, "category": "Multimodal Vision", "prompt": q})
    id_counter += 1

with open("c:/Users/lenovo/Desktop/San/Fun_Projects/LLM Bench Test/prompts/benchmark_prompts.json", "w") as f:
    json.dump(prompts, f, indent=4)
