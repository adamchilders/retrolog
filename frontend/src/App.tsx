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

  useEffect(() => {
    if (token) {
      axios.get(`${API_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(response => {
        fetchEntries();
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
      if (currentEntry.id && currentEntry.id !== 0) { // Existing entry
        await axios.put(`${API_URL}/journal-entries/${currentEntry.id}`, {
          time_block: currentEntry.time_block,
          answers: currentEntry.answers.map(a => ({ question: a.question, content: a.content }))
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else { // New entry
        await axios.post(`${API_URL}/journal-entries/`, {
          time_block: currentEntry.time_block,
          answers: currentEntry.answers.map(a => ({ question: a.question, content: a.content }))
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setIsEditing(false);
      setCurrentEntry(null);
      fetchEntries();
    } catch (error) {
      console.error('Failed to save entry', error);
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
      <hr />
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
