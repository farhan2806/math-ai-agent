import React, { useState } from 'react';
import axios from 'axios';
import { Send, BookOpen, Globe, Brain, Star, ChevronRight, Lightbulb, Calculator } from 'lucide-react';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [rating, setRating] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);

  const API_URL = 'http://localhost:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setLoading(true);
    setResponse(null);
    setShowFeedback(false);
    setRating(0);

    try {
      const result = await axios.post(`${API_URL}/api/solve`, {
        question: question
      });
      setResponse(result.data);
      setShowFeedback(true);
    } catch (error) {
      setResponse({
        success: false,
        message: error.response?.data?.detail || 'An error occurred while processing your question. Please try again.'
      });
    }
    setLoading(false);
  };

  const handleFeedback = async (ratingValue) => {
    setRating(ratingValue);
    try {
      await axios.post(`${API_URL}/api/feedback`, {
        question: question,
        solution: response.solution || '',
        rating: ratingValue
      });
      // Optional: Show a subtle notification instead of alert
    } catch (error) {
      console.error('Feedback error:', error);
    }
  };

  const getSourceIcon = () => {
    if (!response) return null;
    switch (response.source) {
      case 'knowledge_base': return <BookOpen size={18} />;
      case 'web_search': return <Globe size={18} />;
      case 'llm_knowledge': return <Brain size={18} />;
      default: return <Lightbulb size={18} />;
    }
  };

  const getSourceColor = () => {
    if (!response) return '#6B7280';
    switch (response.source) {
      case 'knowledge_base': return '#10B981';
      case 'web_search': return '#3B82F6';
      case 'llm_knowledge': return '#8B5CF6';
      default: return '#6B7280';
    }
  };

  const exampleQuestions = [
    "Solve x² - 5x + 6 = 0",
    "What is the derivative of sin(x)?",
    "Explain the Pythagorean theorem",
    "How to calculate the area of a circle?",
    "Solve ∫(2x dx) from 0 to 3"
  ];

  return (
    <div className="App">
      <div className="background-gradient">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
        </div>
      </div>

      <div className="app-container">
        <header className="app-header">
          <div className="header-content">
            <div className="logo">
              <Calculator size={32} />
              <h1>Math Routing Agent</h1>
            </div>
            <p className="subtitle">AI-Powered Mathematical Problem Solver</p>
          </div>
        </header>

        <main className="main-content">
          <div className="container">
            <div className="card question-card">
              <div className="card-header">
                <h2>Ask a Math Question</h2>
                <p>Get step-by-step solutions from multiple knowledge sources</p>
              </div>
              
              <form onSubmit={handleSubmit} className="question-form">
                <div className="input-container">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Enter your mathematics question here... (e.g., 'Find the roots of x² - 4x + 4 = 0')"
                    rows={isExpanded ? "4" : "3"}
                    disabled={loading}
                    onFocus={() => setIsExpanded(true)}
                    onBlur={() => !question && setIsExpanded(false)}
                  />
                  <div className="input-decoration"></div>
                </div>
                
                <button 
                  type="submit" 
                  disabled={loading || !question.trim()}
                  className={`submit-btn ${loading ? 'loading' : ''}`}
                >
                  {loading ? (
                    <>
                      <div className="spinner"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send size={18} />
                      Solve Problem
                    </>
                  )}
                </button>
              </form>

              <div className="examples-section">
                <p className="examples-title">Try these examples:</p>
                <div className="examples-grid">
                  {exampleQuestions.map((example, index) => (
                    <button
                      key={index}
                      className="example-chip"
                      onClick={() => setQuestion(example)}
                      disabled={loading}
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {response && (
              <div className="card response-card">
                {response.success ? (
                  <>
                    <div className="response-header">
                      <div 
                        className="source-indicator"
                        style={{ backgroundColor: getSourceColor() }}
                      >
                        {getSourceIcon()}
                        <span>
                          {response.source.replace(/_/g, ' ').toUpperCase()}
                        </span>
                      </div>
                      <div className="confidence-score">
                        <Star size={16} fill="#FBBF24" color="#FBBF24" />
                        <span>AI Generated Solution</span>
                      </div>
                    </div>

                    <div className="solution-content">
                      <h3>Step-by-Step Solution:</h3>
                      <div className="solution-text">
                        <pre>{response.solution}</pre>
                      </div>
                    </div>

                    {response.references && response.references.length > 0 && (
                      <div className="references-section">
                        <h4>📚 Reference Materials</h4>
                        <div className="references-list">
                          {response.references.map((ref, idx) => (
                            <a 
                              key={idx} 
                              href={ref.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="reference-link"
                            >
                              <ChevronRight size={16} />
                              <span>{ref.title}</span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {showFeedback && (
                      <div className="feedback-section">
                        <div className="feedback-header">
                          <h4>Was this solution helpful?</h4>
                          <p>Rate your experience to help us improve</p>
                        </div>
                        <div className="rating-buttons">
                          {[1, 2, 3, 4, 5].map((val) => (
                            <button
                              key={val}
                              onClick={() => handleFeedback(val)}
                              className={`rating-btn ${rating === val ? 'selected' : ''}`}
                            >
                              <Star 
                                size={20} 
                                fill={rating >= val ? "#FBBF24" : "none"} 
                                color={rating >= val ? "#FBBF24" : "#D1D5DB"} 
                              />
                            </button>
                          ))}
                        </div>
                        {rating > 0 && (
                          <div className="feedback-thankyou">
                            <Star size={16} fill="#FBBF24" color="#FBBF24" />
                            Thank you for your feedback!
                          </div>
                        )}
                      </div>
                    )}
                  </>
                ) : (
                  <div className="error-state">
                    <div className="error-icon">⚠️</div>
                    <h3>Unable to Process Request</h3>
                    <p>{response.message}</p>
                    <button 
                      onClick={() => setResponse(null)}
                      className="retry-btn"
                    >
                      Try Again
                    </button>
                  </div>
                )}
              </div>
            )}

            {loading && (
              <div className="card loading-card">
                <div className="loading-indicator">
                  <div className="pulse-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                  </div>
                  <p>Analyzing your question and finding the best solution...</p>
                </div>
              </div>
            )}
          </div>
        </main>

        <footer className="app-footer">
          <p>Math Routing Agent • AI-Powered Mathematics Assistant</p>
        </footer>
      </div>
    </div>
  );
}

export default App;