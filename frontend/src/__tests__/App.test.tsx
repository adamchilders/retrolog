import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';
import { mockedAxios } from '../setupTests';

// Mock data
const mockUser = {
  id: 1,
  username: 'testuser',
  entries: []
};

const mockToken = 'mock-jwt-token';

const mockJournalEntry = {
  id: 1,
  time_block: 'Morning',
  timestamp: '2024-01-15T10:30:00',
  owner_id: 1,
  answers: [
    {
      id: 1,
      question: 'What is your main goal for today?',
      content: 'Complete the project documentation'
    }
  ]
};

const mockInsights = {
  insights: 'This is a mock insight response with actionable suggestions.'
};

const mockQuestions = {
  questions: [
    'What specific steps will you take today?',
    'How will you measure success?',
    'What obstacles might you face?'
  ]
};

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    localStorage.clear();
    
    // Reset axios mock
    mockedAxios.post.mockReset();
    mockedAxios.get.mockReset();
    mockedAxios.put.mockReset();
  });

  describe('Authentication Flow', () => {
    test('renders login form when not authenticated', () => {
      render(<App />);
      
      expect(screen.getByText('Login')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Username')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
      expect(screen.getByText('Register')).toBeInTheDocument();
    });

    test('successful login stores token and shows main interface', async () => {
      const user = userEvent.setup();
      
      // Mock successful login
      mockedAxios.post.mockResolvedValueOnce({
        data: { access_token: mockToken, token_type: 'bearer' }
      });
      
      // Mock user data fetch
      mockedAxios.get.mockResolvedValueOnce({
        data: mockUser
      });
      
      // Mock journal entries fetch
      mockedAxios.get.mockResolvedValueOnce({
        data: []
      });

      render(<App />);
      
      // Fill in login form
      await user.type(screen.getByPlaceholderText('Username'), 'testuser');
      await user.type(screen.getByPlaceholderText('Password'), 'testpass');
      
      // Submit login
      await user.click(screen.getByRole('button', { name: 'Login' }));
      
      // Wait for successful login
      await waitFor(() => {
        expect(localStorage.setItem).toHaveBeenCalledWith('token', mockToken);
      });
      
      // Should show main interface
      await waitFor(() => {
        expect(screen.getByText('Welcome!')).toBeInTheDocument();
      });
    });

    test('failed login shows error message', async () => {
      const user = userEvent.setup();
      
      // Mock failed login
      mockedAxios.post.mockRejectedValueOnce({
        response: { status: 401 }
      });

      render(<App />);
      
      await user.type(screen.getByPlaceholderText('Username'), 'testuser');
      await user.type(screen.getByPlaceholderText('Password'), 'wrongpass');
      await user.click(screen.getByRole('button', { name: 'Login' }));
      
      await waitFor(() => {
        expect(screen.getByText('Invalid username or password')).toBeInTheDocument();
      });
    });

    test('successful registration shows success message', async () => {
      const user = userEvent.setup();
      
      // Mock successful registration
      mockedAxios.post.mockResolvedValueOnce({
        data: mockUser
      });

      render(<App />);
      
      // Find registration form inputs
      const usernameInputs = screen.getAllByPlaceholderText('Username');
      const passwordInputs = screen.getAllByPlaceholderText('Password');
      
      // Use the second set (registration form)
      await user.type(usernameInputs[1], 'newuser');
      await user.type(passwordInputs[1], 'newpass');
      await user.click(screen.getByRole('button', { name: 'Register' }));
      
      await waitFor(() => {
        expect(screen.getByText(/Registration successful/)).toBeInTheDocument();
      });
    });
  });

  describe('Authenticated User Interface', () => {
    beforeEach(() => {
      // Set up authenticated state
      localStorage.setItem('token', mockToken);
      
      // Mock user data fetch
      mockedAxios.get.mockImplementation((url) => {
        if (url.includes('/users/me/')) {
          return Promise.resolve({ data: mockUser });
        }
        if (url.includes('/journal-entries/')) {
          return Promise.resolve({ data: [mockJournalEntry] });
        }
        return Promise.reject(new Error('Unknown URL'));
      });
    });

    test('renders main interface for authenticated user', async () => {
      render(<App />);
      
      await waitFor(() => {
        expect(screen.getByText('Welcome!')).toBeInTheDocument();
        expect(screen.getByText('Logout')).toBeInTheDocument();
        expect(screen.getByText(/Journal Entry for/)).toBeInTheDocument();
      });
    });

    test('logout clears token and returns to login', async () => {
      const user = userEvent.setup();
      
      render(<App />);
      
      await waitFor(() => {
        expect(screen.getByText('Welcome!')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Logout'));
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(screen.getByText('Login')).toBeInTheDocument();
    });

    test('displays journal entries', async () => {
      render(<App />);
      
      await waitFor(() => {
        expect(screen.getByText('Your Past Journal Entries')).toBeInTheDocument();
        expect(screen.getByText('Morning')).toBeInTheDocument();
        expect(screen.getByText('Complete the project documentation')).toBeInTheDocument();
      });
    });

    test('can start new journal entry', async () => {
      const user = userEvent.setup();
      
      // Mock questions generation
      mockedAxios.post.mockResolvedValueOnce({
        data: mockQuestions
      });
      
      render(<App />);
      
      await waitFor(() => {
        expect(screen.getByText(/Start\/Edit.*Entry/)).toBeInTheDocument();
      });
      
      await user.click(screen.getByText(/Start\/Edit.*Entry/));
      
      await waitFor(() => {
        expect(screen.getByText('What specific steps will you take today?')).toBeInTheDocument();
      });
    });
  });

  describe('Journal Entry Management', () => {
    beforeEach(() => {
      localStorage.setItem('token', mockToken);
      mockedAxios.get.mockImplementation((url) => {
        if (url.includes('/users/me/')) {
          return Promise.resolve({ data: mockUser });
        }
        if (url.includes('/journal-entries/')) {
          return Promise.resolve({ data: [] });
        }
        return Promise.reject(new Error('Unknown URL'));
      });
    });

    test('can save new journal entry', async () => {
      const user = userEvent.setup();
      
      // Mock questions generation
      mockedAxios.post.mockImplementation((url) => {
        if (url.includes('/generate-questions/')) {
          return Promise.resolve({ data: mockQuestions });
        }
        if (url.includes('/journal-entries/')) {
          return Promise.resolve({ data: mockJournalEntry });
        }
        return Promise.reject(new Error('Unknown URL'));
      });
      
      // Mock updated entries fetch
      mockedAxios.get.mockImplementation((url) => {
        if (url.includes('/users/me/')) {
          return Promise.resolve({ data: mockUser });
        }
        if (url.includes('/journal-entries/')) {
          return Promise.resolve({ data: [mockJournalEntry] });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      render(<App />);
      
      // Start new entry
      await waitFor(() => {
        expect(screen.getByText(/Start\/Edit.*Entry/)).toBeInTheDocument();
      });
      
      await user.click(screen.getByText(/Start\/Edit.*Entry/));
      
      // Fill in answers
      await waitFor(() => {
        const textareas = screen.getAllByRole('textbox');
        expect(textareas.length).toBeGreaterThan(0);
      });
      
      const textareas = screen.getAllByRole('textbox');
      await user.type(textareas[0], 'My answer to the first question');
      
      // Save entry
      await user.click(screen.getByText('Save Entry'));
      
      await waitFor(() => {
        expect(mockedAxios.post).toHaveBeenCalledWith(
          expect.stringContaining('/journal-entries/'),
          expect.any(Object),
          expect.any(Object)
        );
      });
    });

    test('can get insights for journal entry', async () => {
      const user = userEvent.setup();
      
      // Mock insights fetch
      mockedAxios.get.mockImplementation((url) => {
        if (url.includes('/users/me/')) {
          return Promise.resolve({ data: mockUser });
        }
        if (url.includes('/journal-entries/') && !url.includes('/insights')) {
          return Promise.resolve({ data: [mockJournalEntry] });
        }
        if (url.includes('/insights')) {
          return Promise.resolve({ data: mockInsights });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      render(<App />);
      
      await waitFor(() => {
        expect(screen.getByText('Get Insights')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Get Insights'));
      
      await waitFor(() => {
        expect(screen.getByText(mockInsights.insights)).toBeInTheDocument();
      });
    });
  });

  describe('Summary Insights', () => {
    beforeEach(() => {
      localStorage.setItem('token', mockToken);
      mockedAxios.get.mockImplementation((url) => {
        if (url.includes('/users/me/')) {
          return Promise.resolve({ data: mockUser });
        }
        if (url.includes('/journal-entries/') && !url.includes('/insights')) {
          return Promise.resolve({ data: [] });
        }
        return Promise.reject(new Error('Unknown URL'));
      });
    });

    test('can fetch summary insights', async () => {
      const user = userEvent.setup();
      
      // Mock summary insights
      mockedAxios.get.mockImplementation((url) => {
        if (url.includes('/users/me/')) {
          return Promise.resolve({ data: mockUser });
        }
        if (url.includes('/journal-entries/') && !url.includes('/insights')) {
          return Promise.resolve({ data: [] });
        }
        if (url.includes('/insights/summary')) {
          return Promise.resolve({ 
            data: { summary_insights: 'Weekly summary insights' }
          });
        }
        return Promise.reject(new Error('Unknown URL'));
      });

      render(<App />);
      
      await waitFor(() => {
        expect(screen.getByText('Get Summary Insights')).toBeInTheDocument();
      });
      
      await user.click(screen.getByText('Get Summary Insights'));
      
      await waitFor(() => {
        expect(screen.getByText('Weekly summary insights')).toBeInTheDocument();
      });
    });

    test('can change time range for summary insights', async () => {
      const user = userEvent.setup();
      
      render(<App />);
      
      await waitFor(() => {
        const select = screen.getByDisplayValue('weekly');
        expect(select).toBeInTheDocument();
      });
      
      const select = screen.getByDisplayValue('weekly');
      await user.selectOptions(select, 'monthly');
      
      expect(select).toHaveValue('monthly');
    });
  });

  describe('Error Handling', () => {
    test('handles API errors gracefully', async () => {
      localStorage.setItem('token', mockToken);
      
      // Mock API error
      mockedAxios.get.mockRejectedValue(new Error('API Error'));
      
      render(<App />);
      
      // Should not crash and should handle error gracefully
      await waitFor(() => {
        expect(screen.getByText('Welcome!')).toBeInTheDocument();
      });
    });

    test('handles network errors during login', async () => {
      const user = userEvent.setup();
      
      mockedAxios.post.mockRejectedValue(new Error('Network Error'));
      
      render(<App />);
      
      await user.type(screen.getByPlaceholderText('Username'), 'testuser');
      await user.type(screen.getByPlaceholderText('Password'), 'testpass');
      await user.click(screen.getByRole('button', { name: 'Login' }));
      
      await waitFor(() => {
        expect(screen.getByText('Invalid username or password')).toBeInTheDocument();
      });
    });
  });
});
