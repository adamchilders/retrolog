import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface Answer {
  question: string;
  content: string;
  id?: number; // Optional for new answers
}

interface JournalEntry {
  id: number;
  time_block: string;
  timestamp: string;
  owner_id: number;
  answers: Answer[];
  insights?: string;
}

interface Goal {
  id: number;
  title: string;
  description?: string;
  category: string;
  status: string;
  created_at: string;
  updated_at: string;
  target_frequency: string;
  is_active: boolean;
}

function getCurrentTimeBlock(): "Morning" | "Lunch" | "Evening" {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) {
    return "Morning";
  } else if (hour >= 12 && hour < 17) {
    return "Lunch";
  } else {
    return "Evening";
  }
}

const defaultQuestions = {
  "Morning": [
    "What is one small, actionable step you will take today to move closer to a key habit or goal?",
    "How will you ensure discipline in your most important task today?",
    "What positive intention are you setting for yourself this morning?"
  ],
  "Lunch": [
    "What is one success, no matter how small, you'sve achieved so far today?",
    "How have you demonstrated discipline or focus in your work/tasks this morning?",
    "What challenge have you faced, and how did you approach it?"
  ],
  "Evening": [
    "What specific actions did you take today that align with your long-term goals or habits?",
    "What was your biggest win or moment of discipline today, and why?",
    "What are you grateful for or proud of from today's efforts?",
    "What is one thing you will do differently tomorrow to improve your discipline or motivation?"
  ]
};

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [error, setError] = useState('');
  const [currentEntry, setCurrentEntry] = useState<JournalEntry | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // State for summary insights
  const [summaryInsights, setSummaryInsights] = useState<string>('');
  const [selectedTimeRange, setSelectedTimeRange] = useState<"daily" | "weekly" | "monthly">("weekly");

  // State for registration
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerError, setRegisterError] = useState('');

  // State for goals
  const [goals, setGoals] = useState<Goal[]>([]);
  const [showGoalsManager, setShowGoalsManager] = useState(false);
  const [showGoalsAnalytics, setShowGoalsAnalytics] = useState(false);
  const [goalsAnalytics, setGoalsAnalytics] = useState<any>(null);
  const [goalProgress, setGoalProgress] = useState<{[key: number]: {rating: number, note: string}}>({});
  const [newGoal, setNewGoal] = useState({
    title: '',
    description: '',
    category: 'habits',
    target_frequency: 'daily'
  });

  useEffect(() => {
    if (token) {
      axios.get(`${API_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(response => {
        fetchEntries();
        fetchGoals();
      })
      .catch(error => {
        localStorage.removeItem('token');
        setToken(null);
      });
    }
  }, [token]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/token`, new URLSearchParams({
        username,
        password
      }));
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setError('');
    } catch (error) {
      setError('Invalid username or password');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/users/`, {
        username: registerUsername,
        password: registerPassword
      });
      setRegisterError('Registration successful! You can now log in.');
      setRegisterUsername('');
      setRegisterPassword('');
    } catch (error) {
      setRegisterError('Registration failed. Username might already be taken.');
    }
  };

  const fetchEntries = async () => {
    if (!token) return;
    try {
      const response = await axios.get(`${API_URL}/journal-entries/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEntries(response.data);
    } catch (error) {
      console.error('Failed to fetch entries', error);
    }
  };

  const fetchInsights = async (entryId: number) => {
    if (!token) return;
    try {
      const response = await axios.get(`${API_URL}/journal-entries/${entryId}/insights`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEntries(prevEntries =>
        prevEntries.map(entry =>
          entry.id === entryId ? { ...entry, insights: response.data.insights } : entry
        )
      );
    } catch (error) {
      console.error('Failed to fetch insights', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setEntries([]);
    setCurrentEntry(null);
    setIsEditing(false);
    setSummaryInsights('');
  };

  const fetchSummaryInsights = async () => {
    if (!token) return;
    try {
      const response = await axios.get(`${API_URL}/journal-entries/insights/summary?time_range=${selectedTimeRange}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSummaryInsights(response.data.summary_insights);
    } catch (error) {
      console.error('Failed to fetch summary insights', error);
      setSummaryInsights('Could not fetch summary insights.');
    }
  };

  const handleNewOrEditEntry = async () => {
    const timeBlock = getCurrentTimeBlock();
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const existingEntry = entries.find(entry => {
      const entryDate = new Date(entry.timestamp);
      entryDate.setHours(0, 0, 0, 0);
      return entry.time_block === timeBlock && entryDate.getTime() === today.getTime();
    });

    if (existingEntry) {
      setCurrentEntry(existingEntry);
      setIsEditing(true);
    } else {
      // Fetch past entries for adaptive questioning
      const pastEntriesResponse = await axios.get(`${API_URL}/journal-entries/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const pastEntriesForTimeBlock = pastEntriesResponse.data.filter((entry: JournalEntry) => {
        const entryDate = new Date(entry.timestamp);
        entryDate.setHours(0, 0, 0, 0);
        return entry.time_block === timeBlock && entryDate.getTime() < today.getTime(); // Only consider past days
      });

      let generatedQuestions: string[] = [];
      try {
        const questionsResponse = await axios.post(`${API_URL}/generate-questions/`, {
          past_entries: pastEntriesForTimeBlock,
          time_block: timeBlock
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        generatedQuestions = questionsResponse.data.questions;
      } catch (qError) {
        console.error('Failed to generate adaptive questions', qError);
        // Fallback to default questions if AI fails
        generatedQuestions = defaultQuestions[timeBlock] || ["How was your day?"];
      }

      const newAnswers = generatedQuestions.map(q => ({ question: q, content: "" }));
      setCurrentEntry({
        id: 0, // Temporary ID for new entry
        time_block: timeBlock,
        timestamp: new Date().toISOString(),
        owner_id: 0, // Will be set by backend
        answers: newAnswers,
      });
      setIsEditing(true);
    }
  };

  const handleAnswerChange = (index: number, value: string) => {
    if (currentEntry) {
      const updatedAnswers = [...currentEntry.answers];
      updatedAnswers[index].content = value;
      setCurrentEntry({ ...currentEntry, answers: updatedAnswers });
    }
  };

  const saveEntry = async () => {
    if (!currentEntry || !token) return;

    try {
      let entryResponse;
      if (currentEntry.id && currentEntry.id !== 0) { // Existing entry
        entryResponse = await axios.put(`${API_URL}/journal-entries/${currentEntry.id}`, {
          time_block: currentEntry.time_block,
          answers: currentEntry.answers.map(a => ({ question: a.question, content: a.content }))
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else { // New entry
        entryResponse = await axios.post(`${API_URL}/journal-entries/`, {
          time_block: currentEntry.time_block,
          answers: currentEntry.answers.map(a => ({ question: a.question, content: a.content }))
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }

      // Save goal progress if any
      const progressData = Object.entries(goalProgress)
        .filter(([goalId, progress]) => progress.rating > 0)
        .map(([goalId, progress]) => ({
          goal_id: parseInt(goalId),
          rating: progress.rating,
          progress_note: progress.note || ''
        }));

      if (progressData.length > 0) {
        try {
          const entryId = entryResponse.data.id || currentEntry.id;
          await axios.post(`${API_URL}/journal-entries/${entryId}/goal-progress`, progressData, {
            headers: { Authorization: `Bearer ${token}` }
          });
        } catch (error) {
          console.error('Failed to save goal progress', error);
        }
      }

      setIsEditing(false);
      setCurrentEntry(null);
      setGoalProgress({});
      fetchEntries();
    } catch (error) {
      console.error('Failed to save entry', error);
    }
  };

  // Goals management functions
  const fetchGoals = async () => {
    if (!token) return;
    try {
      const response = await axios.get(`${API_URL}/goals/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGoals(response.data);
    } catch (error) {
      console.error('Failed to fetch goals', error);
    }
  };

  const createGoal = async () => {
    if (!token || !newGoal.title.trim()) return;
    try {
      await axios.post(`${API_URL}/goals/`, newGoal, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNewGoal({ title: '', description: '', category: 'habits', target_frequency: 'daily' });
      fetchGoals();
    } catch (error) {
      console.error('Failed to create goal', error);
    }
  };

  const deleteGoal = async (goalId: number) => {
    if (!token) return;
    try {
      await axios.delete(`${API_URL}/goals/${goalId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchGoals();
    } catch (error) {
      console.error('Failed to delete goal', error);
    }
  };

  const fetchGoalsAnalytics = async () => {
    if (!token) return;
    try {
      const response = await axios.get(`${API_URL}/goals/analytics`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGoalsAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch goals analytics', error);
    }
  };

  if (!token) {
    return (
      <div className="terminal-container">
        <h2>Login</h2>
        <form onSubmit={handleLogin}>
          <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
          <button type="submit">Login</button>
        </form>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <hr />
        <h2>Register</h2>
        <form onSubmit={handleRegister}>
          <input type="text" placeholder="Username" value={registerUsername} onChange={e => setRegisterUsername(e.target.value)} />
          <input type="password" placeholder="Password" value={registerPassword} onChange={e => setRegisterPassword(e.target.value)} />
          <button type="submit">Register</button>
        </form>
        {registerError && <p style={{ color: 'red' }}>{registerError}</p>}
      </div>
    );
  }

  return (
    <div className="terminal-container">
      <h2>Welcome!</h2>
      <button onClick={handleLogout}>Logout</button>
      <button onClick={() => setShowGoalsManager(!showGoalsManager)}>
        {showGoalsManager ? 'Hide Goals' : 'Manage Goals'}
      </button>
      <button onClick={() => {
        setShowGoalsAnalytics(!showGoalsAnalytics);
        if (!showGoalsAnalytics) fetchGoalsAnalytics();
      }}>
        {showGoalsAnalytics ? 'Hide Analytics' : 'Goals Analytics'}
      </button>
      <hr />

      {showGoalsManager && (
        <div>
          <h3>Long-term Goals</h3>
          <div>
            <h4>Add New Goal</h4>
            <input
              type="text"
              placeholder="Goal title (e.g., Wake up early)"
              value={newGoal.title}
              onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
            />
            <textarea
              placeholder="Description (optional)"
              value={newGoal.description}
              onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
              rows={2}
              cols={50}
            />
            <select
              value={newGoal.category}
              onChange={(e) => setNewGoal({ ...newGoal, category: e.target.value })}
            >
              <option value="health">Health</option>
              <option value="productivity">Productivity</option>
              <option value="habits">Habits</option>
              <option value="personal_development">Personal Development</option>
              <option value="relationships">Relationships</option>
              <option value="career">Career</option>
              <option value="finance">Finance</option>
              <option value="other">Other</option>
            </select>
            <select
              value={newGoal.target_frequency}
              onChange={(e) => setNewGoal({ ...newGoal, target_frequency: e.target.value })}
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
            <button onClick={createGoal}>Add Goal</button>
          </div>

          <div>
            <h4>Your Goals</h4>
            {goals.length === 0 ? (
              <p>No goals yet. Add your first goal above!</p>
            ) : (
              <ul>
                {goals.map(goal => (
                  <li key={goal.id}>
                    <strong>{goal.title}</strong> ({goal.category}, {goal.target_frequency})
                    {goal.description && <p>{goal.description}</p>}
                    <button onClick={() => deleteGoal(goal.id)}>Delete</button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <hr />
        </div>
      )}

      {showGoalsAnalytics && goalsAnalytics && (
        <div>
          <h3>Goals Analytics</h3>
          <div>
            <p><strong>Total Goals:</strong> {goalsAnalytics.total_goals}</p>

            <h4>Goals by Category</h4>
            <ul>
              {Object.entries(goalsAnalytics.goals_by_category).map(([category, count]) => (
                <li key={category}>{category}: {count as number}</li>
              ))}
            </ul>

            <h4>Goals by Frequency</h4>
            <ul>
              {Object.entries(goalsAnalytics.goals_by_frequency).map(([frequency, count]) => (
                <li key={frequency}>{frequency}: {count as number}</li>
              ))}
            </ul>

            {goalsAnalytics.recent_progress.length > 0 && (
              <div>
                <h4>Recent Progress</h4>
                <ul>
                  {goalsAnalytics.recent_progress.map((progress: any) => (
                    <li key={progress.goal_id}>
                      <strong>{progress.goal_title}</strong>: {progress.entries_count} entries,
                      avg rating: {progress.average_rating}/5
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          <hr />
        </div>
      )}
      <h3>Journal Entry for {getCurrentTimeBlock()}</h3>
      {!isEditing && (
        <button onClick={handleNewOrEditEntry}>Start/Edit {getCurrentTimeBlock()} Entry</button>
      )}

      {isEditing && currentEntry && (
        <div>
          <h4>{currentEntry.time_block} Entry - {new Date(currentEntry.timestamp).toLocaleDateString()}</h4>
          {currentEntry.answers.map((answer, index) => (
            <div key={index}>
              <p>{answer.question}</p>
              <textarea
                value={answer.content}
                onChange={(e) => handleAnswerChange(index, e.target.value)}
                rows={3}
                cols={50}
              />
            </div>
          ))}

          {goals.length > 0 && (
            <div>
              <h4>Goal Progress (Optional)</h4>
              <p>Rate your progress on your goals today (1-5 scale):</p>
              {goals.map(goal => (
                <div key={goal.id} style={{ marginBottom: '10px' }}>
                  <label>
                    <strong>{goal.title}</strong> ({goal.category}):
                    <select
                      value={goalProgress[goal.id]?.rating || ''}
                      onChange={(e) => setGoalProgress({
                        ...goalProgress,
                        [goal.id]: {
                          ...goalProgress[goal.id],
                          rating: parseInt(e.target.value) || 0
                        }
                      })}
                    >
                      <option value="">No rating</option>
                      <option value="1">1 - Poor</option>
                      <option value="2">2 - Below Average</option>
                      <option value="3">3 - Average</option>
                      <option value="4">4 - Good</option>
                      <option value="5">5 - Excellent</option>
                    </select>
                  </label>
                  <textarea
                    placeholder="Progress note (optional)"
                    value={goalProgress[goal.id]?.note || ''}
                    onChange={(e) => setGoalProgress({
                      ...goalProgress,
                      [goal.id]: {
                        ...goalProgress[goal.id],
                        note: e.target.value
                      }
                    })}
                    rows={2}
                    cols={40}
                  />
                </div>
              ))}
            </div>
          )}

          <button onClick={saveEntry}>Save Entry</button>
          <button onClick={() => setIsEditing(false)}>Cancel</button>
        </div>
      )}

      <hr />
      <h3>Your Past Journal Entries</h3>
      <ul>
        {entries.map(entry => (
          <li key={entry.id}>
            <p><strong>Time Block:</strong> {entry.time_block}</p>
            <p><strong>Timestamp:</strong> {new Date(entry.timestamp).toLocaleString()}</p>
            <ul>
              {entry.answers.map((answer: any) => (
                <li key={answer.id}><strong>{answer.question}:</strong> {answer.content}</li>
              ))}
            </ul>
            <button onClick={() => fetchInsights(entry.id)}>Get Insights</button>
            {entry.insights && <p><strong>Insights:</strong> {entry.insights}</p>}
          </li>
        ))}
      </ul>

      <hr />

      <h3>AI Summary Insights</h3>
      <div>
        <button onClick={() => setSelectedTimeRange("daily")}>Daily</button>
        <button onClick={() => setSelectedTimeRange("weekly")}>Weekly</button>
        <button onClick={() => setSelectedTimeRange("monthly")}>Monthly</button>
      </div>
      <p>Time Range: {selectedTimeRange}</p>
      <button onClick={fetchSummaryInsights}>Get Summary Insights</button>
      {summaryInsights && (
        <div style={{ whiteSpace: 'pre-wrap' }}>
          <h4>Summary:</h4>
          <p>{summaryInsights}</p>
        </div>
      )}
    </div>
  );
}

export default App;
