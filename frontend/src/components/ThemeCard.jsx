import React from 'react';

const ThemeCard = ({ theme, quotes, actions }) => {
  return (
    <div className="glass-panel theme-card">
      <h3>{theme}</h3>
      
      {quotes && quotes.length > 0 && (
        <div className="quotes-section">
          {quotes.map((quote, index) => (
            <div key={index} className="quote-item">
              "{quote}"
            </div>
          ))}
        </div>
      )}

      {actions && actions.length > 0 && (
        <div className="actions-section">
          {actions.map((action, index) => (
            <div key={index} className="action-item">
              <span>{action}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ThemeCard;
