# 🎙️ Bilingual Offline Voice Assistant (English / Arabic)

A desktop voice assistant built with Python that supports:
- Offline speech recognition (VOSK)
- English & Arabic input
- Text-to-speech responses
- Intelligent prompt selection using a genetic-inspired algorithm
- Optional GPT integration (API-based)

## ✨ Features
- 🎧 Offline speech recognition (no internet required)
- 🧠 Category-aware prompt generation
- 🌍 English & Arabic support (RTL fixed)
- 🖥️ GUI built with CustomTkinter
- 🔌 Optional OpenAI API integration

## 🛠️ Installation

```bash
git clone https://github.com/moehabx/bilingual-voice-assistant.git
cd bilingual-voice-assistant
pip install -r requirements.txt
```


# **Genetic Algorithm (GA) in Your Prompt Selector**

## **1. What is a Genetic Algorithm?**

A **genetic algorithm** is a type of **search and optimization algorithm** inspired by **natural evolution**.

Key ideas:

* **Population:** A set of candidate solutions.
* **Fitness:** A way to measure how good each solution is.
* **Selection:** Prefer better solutions for the next generation.
* **Crossover / Mutation:** Introduce variations to explore new solutions.
* **Iteration:** Repeat selection and variation until an optimal or satisfactory solution is found.

In essence, it tries to "evolve" the best solution over several generations.

---

## **2. How GA Works in Your Code**

Your GA is simplified. It doesn’t use full evolution, crossover, or mutation; it uses **fitness-based random selection**. Let’s break it down.

---

### **Step 1: Detect Categories with Keywords**

```python
category_weights = detect_categories_with_weights(user_text, KEYWORDS_MAP)
```

* `user_text` is what the user said or typed.
* `KEYWORDS_MAP` contains **keywords for each category** (medical, technology, finance, etc.).
* The function `detect_categories_with_weights()` counts **how many times keywords appear** in the text for each category.

**Example:**

User text: `"I have a headache and feel dizzy"`

* `"headache"` and `"dizzy"` are in `"medical"` keywords → weight = 2
* No other category matches → only `"medical"` detected

✅ Output: `{"medical": 2}`

---

### **Step 2: Select Number of Prompts (Fitness-Based)**

```python
selection_count = min(len(prompts), max(1, weight))
```

* **`weight`** = number of keyword matches → used as a measure of importance (fitness).
* **`max(1, weight)`** ensures we always select at least **1 prompt**.
* **`min(len(prompts), …)`** ensures we don’t select more prompts than exist in the category.

**Example:**

* `"medical"` has 10 prompts, weight = 2 → pick 2 prompts
* `"finance"` has 5 prompts, weight = 0 → pick 1 prompt (default minimum)

---

### **Step 3: Randomly Select Prompts (Genetic Selection)**

```python
selected_prompts = random.sample(prompts, selection_count)
```

* This is like **"survival of the fittest"** in a simple way:

  * Prompts from categories with more keyword matches (“higher fitness”) are more likely to appear in the output.
* `random.sample()` ensures **different prompts are chosen each time**, giving variation.

**Example Output:**

```python
{
  "medical": ["Explain the symptoms of common flu to a patient.", "Provide first-aid advice for minor injuries."]
}
```

---

### **Step 4: Return the Result**

```python
result[category] = selected_prompts
```

* All selected prompts are stored in a dictionary by category.
* If no category matches, the **default is “general”**.

**Example:**

User text: `"I want to learn AI and programming"`

* Matches `"technology"` keywords → weight = 2
* Selected prompts:

```python
{
  "technology": ["Explain this technology concept in simple terms.", "Give beginner tips for learning programming."]
}
```

---

### **Step 5: Formatting for Output**

```python
def format_prompt_output(genetic_result):
    lines = []
    for category, prompts in genetic_result.items():
        joined = ", ".join(prompts)
        lines.append(f"{category.upper()}:\n{joined}")
    return "\n\n".join(lines)
```

* Combines prompts into a **user-friendly string**, grouped by category.
* Example Output:

```
TECHNOLOGY:
Explain this technology concept in simple terms., Give beginner tips for learning programming.
```

---

## **3. Key Points of GA in This Code**

1. **Fitness Function:**

   * Number of keyword matches (`weight`) determines “fitness” of each category.
   * Higher fitness → more prompts selected.

2. **Selection:**

   * Random selection of prompts from high-fitness categories.
   * Ensures diversity (not always the same prompts).

3. **No Crossover or Mutation:**

   * Classic GA steps like combining prompts from multiple “solutions” or mutating them are not used.
   * This is a simplified GA, mainly using **fitness-based random sampling**.

4. **Default Behavior:**

   * If no keywords match, default to `"general"` category to avoid empty output.

5. **Advantages:**

   * Adapts to the user’s input dynamically.
   * Gives more relevant prompts for categories that appear more in the text.
   * Introduces randomness for variety.

---

## **4. Example Flow**

User input: `"I have a headache and want to know how to code in Python"`

1. Detect keywords → `"medical": 1`, `"technology": 1`
2. Select number of prompts → 1 prompt from medical, 1 from technology
3. Randomly pick prompts from each category
4. Return result:

```
MEDICAL:
Explain the symptoms of common flu to a patient.

TECHNOLOGY:
Give beginner tips for learning programming.
```



