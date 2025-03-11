import React, { useEffect, useState } from "react";
import "./ResearchPapers.css"; // Make sure to create this CSS file with the styles above

const Research = () => {
  const [results, setResults] = useState([]);

  useEffect(() => {
    const storedResults = localStorage.getItem("searchResult");
    if (storedResults) {
      setResults(JSON.parse(storedResults)); // Parse the stored JSON
    }
  }, []);

  return (
    <div className="research-container">
      <h2>Research Paper Results</h2>
      {results.length > 0 ? (
        <ul>
          {results.map((paper, index) => (
            <li key={index}>
              <a href={paper.url} target="_blank" rel="noopener noreferrer">
                {paper.title}
              </a>
            </li>
          ))}
        </ul>
      ) : (
        <p>No research papers found</p>
      )}
    </div>
  );
};

export default Research;