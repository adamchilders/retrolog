# backend/app/services.py
import google.generativeai as genai
import os
import datetime
from . import crud

# Configure the Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
gena_api = genai.configure(api_key=GOOGLE_API_KEY)

def get_insights_from_gemini(journal_entry):
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""Analyze the following journal entry and provide insights and actionable suggestions.

    **Time Block:** {journal_entry.time_block}
    **Timestamp:** {journal_entry.timestamp}

    **Answers:**
    """
    for answer in journal_entry.answers:
        prompt += f"- {answer.question}: {answer.content}\n"

    prompt += """\n**Insights:**
    Please provide a brief analysis of this entry, identifying any notable patterns, sentiments, or themes. 

    **Actionable Suggestions:**
    Based on the entry, suggest 1-2 simple, actionable steps the user could take to improve their well-being, productivity, or alignment with their goals."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return "Could not generate insights at this time."

def generate_adaptive_questions(past_entries: list, time_block: str, user_goals: list = None):
    model = genai.GenerativeModel('gemini-pro')

    prompt = f"""Based on the following past journal entries and long-term goals for the '{time_block}' time block, generate 3-5 new, relevant, and engaging questions for the user to answer. The questions should encourage reflection and progress, and ideally build upon themes or challenges identified in previous entries and help track progress on their goals.

    **Long-term Goals:**
    """

    if user_goals:
        for goal in user_goals:
            prompt += f"\n- {goal.title} ({goal.category.value}): {goal.description or 'No description'}"
            prompt += f" [Target: {goal.target_frequency}]"
    else:
        prompt += "No specific goals set yet."

    prompt += "\n\n**Past Entries:**"

    if not past_entries:
        prompt += "\nNo past entries available."
    else:
        for entry in past_entries:
            prompt += f"\n- Entry from {entry.timestamp.strftime('%Y-%m-%d')}:\n"
            for answer in entry.answers:
                prompt += f"  - {answer.question}: {answer.content}\n"

    prompt += """\n**New Questions (list only the questions, one per line):**
    Focus on creating questions that help track progress on their goals and encourage reflection on daily habits that support their long-term objectives.
    """

    try:
        response = model.generate_content(prompt)
        # Assuming Gemini returns questions as a newline-separated list
        questions = [q.strip() for q in response.text.split('\n') if q.strip()]
        # Filter out any non-question lines
        questions = [q for q in questions if q.endswith('?') or any(word in q.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which'])]
        return questions[:5]  # Limit to 5 questions
    except Exception as e:
        print(f"Error generating adaptive questions with Gemini: {e}")
        # Fallback to default questions if AI fails
        return get_fallback_questions(time_block, user_goals)


def get_fallback_questions(time_block: str, user_goals: list = None):
    """Generate fallback questions when AI is unavailable."""
    base_questions = {
        "Morning": [
            "What is one small, actionable step you will take today to move closer to a key habit or goal?",
            "How will you ensure discipline in your most important task today?",
            "What positive intention are you setting for yourself this morning?"
        ],
        "Lunch": [
            "What is one success, no matter how small, you've achieved so far today?",
            "How have you demonstrated discipline or focus in your work/tasks this morning?",
            "What challenge have you faced, and how did you approach it?"
        ],
        "Evening": [
            "What specific actions did you take today that align with your long-term goals or habits?",
            "What was your biggest win or moment of discipline today, and why?",
            "What are you grateful for or proud of from today's efforts?",
            "What is one thing you will do differently tomorrow to improve your discipline or motivation?"
        ]
    }

    questions = base_questions.get(time_block, ["How was your day?"])

    # Add goal-specific questions if goals exist
    if user_goals:
        goal_questions = []
        for goal in user_goals[:2]:  # Limit to 2 goals to avoid too many questions
            if goal.category.value == "health":
                goal_questions.append(f"How did you work on your health goal '{goal.title}' today?")
            elif goal.category.value == "habits":
                goal_questions.append(f"Did you practice the habit '{goal.title}' today? How did it go?")
            elif goal.category.value == "productivity":
                goal_questions.append(f"What progress did you make on '{goal.title}' today?")
            else:
                goal_questions.append(f"How did you work toward your goal '{goal.title}' today?")

        questions.extend(goal_questions)

    return questions

def get_summary_insights(db, user_id: int, time_range: str):
    model = genai.GenerativeModel('gemini-pro')
    
    end_date = datetime.datetime.utcnow()
    if time_range == "daily":
        start_date = end_date - datetime.timedelta(days=1)
    elif time_range == "weekly":
        start_date = end_date - datetime.timedelta(weeks=1)
    elif time_range == "monthly":
        start_date = end_date - datetime.timedelta(days=30) # Approximately a month
    
    entries = crud.get_journal_entries_by_user_and_time_range(db, user_id, start_date, end_date)

    if not entries:
        return f"No journal entries found for the {time_range} period."

    prompt = f"""Analyze the following journal entries from the past {time_range} for a user focused on habit building, discipline, recognizing successes, and motivation. Provide a concise summary of trends, successes, challenges, and areas for improvement. Then, offer 2-3 actionable suggestions for building better habits, discipline, and motivation.

    **Journal Entries ({time_range}):**
    """
    for entry in entries:
        prompt += f"\n--- Entry from {entry.timestamp.strftime('%Y-%m-%d %H:%M')} ({entry.time_block}) ---\n"
        for answer in entry.answers:
            prompt += f"- {answer.question}: {answer.content}\n"

    prompt += """\n**Summary of Trends, Successes, Challenges, and Areas for Improvement:**

**Actionable Suggestions for Habits, Discipline, and Motivation:**
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating summary insights with Gemini: {e}")
        return "Could not generate summary insights at this time."
