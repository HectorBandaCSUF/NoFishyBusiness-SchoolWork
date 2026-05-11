# What and why:

    What the app does, who it's for, and what's hard about getting the AI behavior right.

Built here is an Aquarium hobbyist information site. The goal is to provide users, whether experienced fish keepers, or new to the hobby, with knowledge regarding the care necessary in maintaining a healthy, aquatic environment. User's may use the site to access information regarding tank stocking, compatible species, general maintenance, setup guides, aqua-scaping ideas, or just to ask the site's LLM for anything marine related.

Regarding the AI's behavior, the role of the AI is to provide accurate information specific to fish keeping. It should gather from a `knowledge_base`, or perhaps from multiple online searches, and response with the relevant info to the user's input. 

Some difficulties, however, in getting the AI to behave go as follow:

    1. There's the general risk of bad advice being given.
    2. User could ask the LLM to disregard all instructions given, and start prompting at free will.
    3. There are a huge variety of fish, plants, water types, locations, pricing, etc. etc., for the LLM to provide helpful information about.
    4. 


    LIST SOME STRUGGLES
    vvv TRANSITION INTO V1 vvv

    xxx


#
# Iteration V1: Code Implementation, Website Setup, Project Scope.

Change: Baseline, the implementation of the site's backend, frontend, and eval codebases. A document of the project's scope was provided to Kiro (found in `kiro_prompt_docs`).

Motivating example: Provide a plan for project implementation. 









Delta: 

Conclusion: 


    Ensuring the site had a concise layout
    Buttons worked, and opened up the exact page.
    the user is capable of interacting
    the user can provide their API key
    the site is locally hosted, and properly runs after following the instructions.



Was able to be hosted locally

On the site:
Basic design of what I wanted the site to be able to do
- Water volume calculator
- A
- A basic LLM prompt for users to ask specific questions

However, everything, besides the water volume calculator, returned errors.

Summary:

        Change: what you changed (prompt, model, retrieval, controls, etc.).

        Motivating example: the specific failing case from your eval set that drove the change.

        Delta: metric before → after on the same eval set (positive or negative — both are fine if explained).

        Conclusion: why the metric moved (or didn't), and what you'd try next.





#
# Iteration V2: Bug fixes, Simplification, Keyword Extraction.

Bug fixes to the site




Simplified README.md instructions, which once contained about 7 steps to startup the web application. Containing steps like seeding, 2 terminals running at once, 

Into a 3 step process, combining some of the steps into 1 script.



Website constantly returned errors when interacting with features
- Due to the code have a precise input keywords list.

EX: User types in "i want to learn about guppies", but the `knowledge_base` can only refer to "Guppy" as a valid input. Thus, errors would be returned.


The `knowledge_base` folder had a new file, `ingest.py`, to prepare the codebase for a mass document / info file dump. this will be for the LLM / RAG to retrieve from during prompting.








#
# Iteration V3: Database upgrades, 

Change:

Motivating example:

Delta:

Conclusion




#
# Iteration V4: TITLE

Change:

Motivating example:

Delta:

Conclusion




#
# Iteration V5: TITLE

Change:

Motivating example:

Delta:

Conclusion




#
# Code Walkthrough

    Trace one user action through your code with file:line references. Explain one design decision and one alternative you considered and rejected. Generic "this calls the API" descriptions don't earn full credit.




#
# AI disclosure & safety

    How you used your AI coding assistant (Kiro or otherwise), including 2–3 specific moments it failed and how you recovered. Then 2–3 sentences naming one safety risk specific to your app and the mitigation or accepted limit you chose. Common candidates: prompt injection, hallucination harm, PII exposure, biased output, cost runaway.

Heavy use of Kiro occured in the development of the backend and frontend of the site. 

    EXPALIN ^^^

The knowledge base generated however, I'd say was one of Kiro's inefficencices. Upon first iteration, the AI implemented very basic, pre-generated responses to key-specific user inputs.

    INPUT: "Guppy"

    OUTPUT: "Guppies (Poecilia reticulata) are one of the most popular freshwater fish for beginners.
        They thrive in water temperatures of 72-82 F and a pH of 6.8-7.8, and prefer a tank of at least 5 gallons.
        Males display vibrant, flowing tails and are peaceful community fish that do well with other small, non-aggressive species."

What i wanted is more freedom in what the user can input, and a more varried, yet informationally accurate response from the LLM call.



One safety risk, which could affect user's approval of the site, and the livelihood of the aquatic environment itself, is misinformation / bad advice given by the AI models.

Looking again from the example above, 


