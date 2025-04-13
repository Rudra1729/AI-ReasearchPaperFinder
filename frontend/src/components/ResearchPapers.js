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


  const handleLinkClick = (paper) => {
    fetch("http://localhost:5000/log-click", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(paper), // Send title and url
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Successfully sent to backend:", data);
        
        // Redirect to Flask server (PDF analyzer app, for example)
        window.location.href = "http://localhost:5001/";
      })
      .catch((error) => {
        console.error("Error sending to backend:", error);
      });
  };
  
  return (
    <div className="research-container">
      <h2>Research Paper Results</h2>
      {results.length > 0 ? (
        <ul>
          {results.map((paper, index) => (
            <li key={index}>
               <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => handleLinkClick(paper)}
              >
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