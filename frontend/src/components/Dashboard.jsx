import React, { useEffect, useState } from 'react';
import ThemeCard from './ThemeCard';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysisData = async () => {
      try {
        const response = await fetch('/data/latest_analysis.json');
        if (!response.ok) {
          throw new Error('Failed to fetch data. Is the pipeline running?');
        }
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading Weekly Pulse AI Insights...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-container">
        <header>
          <h1>Groww Weekly Pulse</h1>
          <p className="subtitle">Failed to load insights</p>
        </header>
        <div className="glass-panel" style={{ padding: '24px', color: '#f87171' }}>
          <p>Error: {error}</p>
        </div>
      </div>
    );
  }

  // Parse the structured data
  // data format: { week: "...", run_date: "...", analysis: { themes: [...], quotes: [...], actions: [...] } }
  const weekLabel = data?.week || "Current Week";
  const runDate = data?.run_date ? new Date(data.run_date).toLocaleString() : "";
  const themes = data?.analysis?.themes || [];
  const quotes = data?.analysis?.quotes || [];
  const actions = data?.analysis?.actions || [];

  // Re-zip the data by index (assuming the analysis engine generated them in 1:1:1 mapping)
  // If not exactly 1:1:1, we just group them loosely.
  const cardsData = themes.map((theme, idx) => ({
    theme: theme,
    quotes: quotes.slice(idx * 2, idx * 2 + 2), // rough chunking assuming 2 quotes per theme
    actions: actions[idx] ? [actions[idx]] : [] // assuming 1 action per theme
  }));

  return (
    <div className="app-container">
      <header>
        <span className="badge">AI Insights</span>
        <h1>Groww Weekly Pulse</h1>
        <p className="subtitle">
          Displaying top feature requests and bug reports for <strong>{weekLabel}</strong>
          <br/>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Last run: {runDate}
          </span>
        </p>
      </header>

      {cardsData.length === 0 ? (
        <div className="glass-panel" style={{ padding: '24px', textAlign: 'center' }}>
          <p>No actionable insights found for this week.</p>
        </div>
      ) : (
        <div className="dashboard-grid">
          {cardsData.map((card, idx) => (
            <ThemeCard 
              key={idx} 
              theme={card.theme} 
              quotes={card.quotes} 
              actions={card.actions} 
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;
