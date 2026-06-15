# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
ANS: search_listings will search items from the listings.json based on the user query.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ...
- `size` (str): ...
- `max_price` (float): ...

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
Ans:It returns a list of dict of the best matching value from listing.json file.The result contain
1.Discription(str)
2.size(str/none)
3.price(float/none) 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
Ans: If it fails, returns empty list, it will not raise an error, instead set a freindly message
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
This tool will take the output/selected list from the search_lists and user's wardrobe, then propose outfit
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...
This is selected list dict, and represents the best matching items from the listings.
- `wardrobe` (dict): ...
This one is the users wardrobe from wardrobe_schema.json

**What it returns:**
<!-- Describe the return value -->
It returns non empty short discription of a complet outfit

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the return is empyt if suggest other styling advise, but do not through exception.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
fit card" for the UI containing the selected listing, price, platform, and 2–3 styling bullets explaining why it works.
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): ...
- `outfit` (string suggestion
- `new_list` a listing dictionary from choosen listing

**What it returns:**
<!-- Describe the return value -->
It return string sugestion sentence usable as instagram caption. 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->if the outfit is missing/empty return a freindly error message but do not raise exception error.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The planning loop first analyzes the user's request and determines which tool, if any, is required. It selects the most appropriate tool based on the task and executes it. After receiving the tool's output, the agent evaluates whether the user's request has been fully satisfied. If additional information or actions are needed, it selects and calls the next tool. This process repeats until all sub-tasks are completed or no further tool calls are necessary.

If a required tool returns no results or insufficient data for the primary request, the agent stops execution and returns a friendly "not found" or failure message rather than continuing with downstream tool calls.

Once all required information has been collected, the LLM synthesizes the tool outputs into the final response, which may be returned as a structured list of dictionaries or another application-specific format.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
The agent stores each tool's return value in a session dictionary as state. Each subsequent tool call can access this stored data when needed. The session tracks the collected list of dictionaries, intermediate results, and request progress until all queries are answered. Once all required data has been collected, the LLM combines and synthesizes the stored information into the final response.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Set `session["error"]` with guidance: "No listings found|
| suggest_outfit | Wardrobe is empty | Return a friendly message asking the user to add basics|
| create_fit_card | Outfit input is missing or incomplete | return a freindly error message but do not raise exception error|

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---User_input =>handle_query() with app.py =>'run_agen()' with agent.py => 'planning_lop: parse query -> search_listings() ->suggest_outfit() ->create_fit_card()`
-`state lives in SESSION and flows step by step. The UI maps the session output in to three panels.

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->
     I will use claude, Gemenia or ChatGPT. if i stuck or unable to debug the error i wil past the error and ask to help me. also will ask to summerize my sentence in short and precise way.

**Milestone 3 — Individual tool implementations:**
implementation:search_listing(parsed) in tool.py, by using utils.data_loader.load_listing(), then keyword price/size filter the top
implementation:suggest_outfit(new_item, wardrobe) to pick matching items, then return short string
implementation:create_fit_card(outfit, selected_item) creates instagram caption

**Milestone 4 — Planning loop and state management:**
implemetnation: run_agent() in `agent.py` following the loop above; test with the CLI tests at the bottom of agent.py  and the Gradio UI

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->handle_query()` receives the text and the chosen wardrobe (example or empty)

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? --> `handle_query()` calls `run_agent(query, wardrobe)

**Step 3:**
<!-- Continue until the full interaction is complete -->
run_agent()` parses the query: `description = "vintage graphic tee"`, `size = None`, `max_price = 30.0`

**Step 4:**run_agent()` calls `search_listings(parsed)` → returns a list of matching listings.

**Step 5:** run_agent()` picks the first result and stores it in `selected_item

**Step 6:** run_agent()` calls `suggest_outfit(selected_item, wardrobe)` → returns a short outfit suggestion text.

**Step 7:** run_agent()` calls `create_fit_card(outfit_text, selected_item)` → returns a formatted fit card string

**Step 8:** run_agent()` returns the `session` dict with `selected_item`, `outfit_suggestion`, `fit_card`, and `error = None`.



**Final output to user:**
<!-- What does the user actually see at the end? -->
Final output to the user by using Gardio shows listing text, outfit suggestion and fit card or freindly not found/suggestion message.
