from http import client
from tracemalloc import start
from groq import Groq
import json

from sympy import content

from Config.Paths import HERO_SUMMARY



with open('config.json', 'r') as f:
    config = json.load(f)

class AIConnection:
    def __init__(self):
      self.client = Groq(api_key=config["groq_api_key"])
      self.previous_char = {'unique_id': "xx"}
      self.chat_history = []

    
    def resolve_action(self, input_text):
      completion = self.client.chat.completions.create(
      model="llama-3.1-8b-instant",
      messages=[
        {
          "role": "system",
          "content": "Task: Convert Input to JSON mechanics.\nMode: Strict Deterministic.\n\n### DEFINITIONS\nACTIONS = [attack, talk, flee, trade]\nSTATS   = [Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma]\n\n### ALGORITHM (Priority Order)\n1. PARSE Input for verbs/intent.\n2. MAP to Action:\n   IF (harm, grab, kidnap, destroy, grapple) -> \"attack\"\n   IF (run, hide, sneak, escape)             -> \"flee\"\n   IF (persuade, lie, intimidate, charm)     -> \"talk\"\n   IF (buy, sell, barter, give)              -> \"trade\"\n\n3. MAP to Stats (per roll):\n   IF (sneak, aim, throw, balance) -> \"Dexterity\"\n   IF (lift, smash, grapple, hold) -> \"Strength\"\n   IF (resist, endure, sprint)     -> \"Constitution\"\n   IF (lie, charm, bargain)        -> \"Charisma\"\n   IF (recall, analyze)            -> \"Intelligence\"\n   IF (perceive, sense)            -> \"Wisdom\"\n\n4. COUNT Rolls:\n   IF single simple action -> 1 roll.\n   IF complex action (Action A + Action B) -> 2 rolls.\n   IF \"attack\" -> Always 2 rolls (Hit + Damage) UNLESS it is a grapple/shove (1 roll).\n\n### OUTPUT SCHEMA\n{\"action\": \"Enum\", \"roll_count\": Int, \"modifiers\": [[\"Enum\"], [\"Enum\"]]}\n\n### ONE-SHOT EXAMPLE\nInput: \"I sneak behind him and choke him out.\"\nLogic: Sneak(Dex) + Choke(Str/Attack).\nOutput: {\"action\": \"attack\", \"roll_count\": 2, \"modifiers\": [[\"Dexterity\"], [\"Strength\"]]}"
        },
        {
          "role": "user",
          "content": f"use JSON, {input_text}"
        }
      ],
      temperature=0,
      max_completion_tokens=50,
      top_p=1,
      stream=False,
      response_format={"type": "json_object"},
      stop=None
      )

      try:
          return json.loads(completion.choices[0].message.content)
      except (json.JSONDecodeError, AttributeError):
          return {"error": "Failed to parse JSON from model response."}
    
    def extract_roleplay_guide(self, file_path):
      with open(file_path, 'r', encoding='utf-8') as f:
          content = f.read()
    
      # Find the start of Roleplay Guide
      start = content.find("#### Roleplay Guide ####")
    
      if start == -1:
         return None
    
      # Find the NEXT section header (skip past the current header first)
      next_section = content.find("####", start + len("#### Roleplay Guide ####"))
    
      if next_section != -1:
          return content[start:next_section].strip()
      else:
        # If no next section, return everything till the end
          return content[start:].strip()
    def Chat(self, char ,input_text):
      prompt = f"""
**Role:** You are the **Game Master** and **{char['name']}** ({char['age']}, {char['profession']}, {char['nature']}, {char['mood']}).
**Context:** Bio: {char['description']} Likes: {char['favor_tags']}. Hates: {char['hate_tags']}.
**Player Info:** {self.extract_roleplay_guide(HERO_SUMMARY)}
**Task:** Respond to input. Treat SYSTEM logs as real physical events.
**Format:** JSON ONLY. No markdown.
**Structure:** `[["Game Master", "Action"], ["{char['name']}", "Dialogue"], ["Impression", INT], ["Done", BOOL]]`

**Logic:**
* **Impression:** Integer -5 (Hated) to +5 (Loved) based on input vs personality.
* **Done:** `true` if conversation ends/user leaves, else `false`.

**Example:**
Input: `Goodbye!`
Output: `[["Game Master", "She waves happily."], ["{char['name']}", "Safe travels, friend!"], ["Impression", 1], ["Done", true]]`
"""
      if self.previous_char['unique_id'] != char['unique_id']:
        self.chat_history.clear()
        self.chat_history.append({"role":"system", "content": prompt})
        self.previous_char = char

      self.chat_history.append({"role":"user", "content": f"use JSON, {input_text}"})
      completion = self.client.chat.completions.create(
      model="llama-3.3-70b-versatile",
      messages=self.chat_history,
      temperature=1,
      max_completion_tokens=1024,
      top_p=1,
      stream=False,
      response_format={"type": "json_object"},
      stop=None
      )

      try:
          response_content = completion.choices[0].message.content
          self.chat_history.append({"role": "assistant", "content": response_content})
          return json.loads(response_content)
      except (json.JSONDecodeError, AttributeError):
          return {"error": "Failed to parse JSON from model response."}
      
    def characterProfiler(self, character_sheet):
      system_prompt = """
### SYSTEM INSTRUCTION ###
You are an **RPG Character Profiler**. Your task is to analyze a structured "Character Sheet" text block and convert it into a rich, immersive narrative profile.
**INPUT FORMAT:**
You will receive a formatted text block with headers like `BASIC INFORMATION`, `ABILITY SCORES`, `COMBAT STATS`, etc.
**OUTPUT INSTRUCTIONS:**
1.  **Narrative Bio:** Write a 3-sentence summary blending their appearance, background, and personality. Focus on the "Character Profile" section.
2.  **Stats Block:** Create a clean summary line for HP, AC, Sanity, and their highest 2 Ability Scores.
3.  **Combat Style:** Synthesize the "Combat Style," "Weapons," and "Class Features" sections. Explain *how* they fight (e.g., "Uses a Revolver and Rifle to control range...").
4.  **Roleplay Guide:**
    * **Vibe:** Infer the atmosphere from the "Notes" and "Appearance".
    * **Strengths/Weaknesses:** Translate "Advantage On" and "Disadvantage On" into narrative traits (e.g., "Struggles in bright light due to fog adaptation").
    * **Motivation:** Combine "Goals" and "Fears".
5.  **Inventory Highlights:** Mention key weapons and flavor items (from "Notes" or "Equipment") that define their look.
**TONE:** Atmospheric, grim-fantasy, and organized. Use formatting (bolding, bullet points) to make it readable.
### END INSTRUCTION ###
"""
      completion = self.client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=[
              {
                  "role": "system",
                  "content": system_prompt
            },
             {
                 "role": "user",
                 "content": f"analyze the following character sheet:\n\n```\n{character_sheet}\n```"
             }
        ],
         temperature=1,
         max_completion_tokens=1000,
         top_p=1,
          stream=True,
         stop=None
      )
    
      for chunk in completion:
          if chunk.choices[0].delta.content:
              yield chunk.choices[0].delta.content