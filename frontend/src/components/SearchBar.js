import React from "react";
import "./SearchBar.css";

const SearchBar = () => (
  <div className="search-box">
    <h2>Search for Research Papers</h2>
    <p>Enter a topic, question, or research area</p>
    <div className="search-inputs">
      <input type="text" placeholder="e.g., 'Effects of climate change on marine ecosystems'" />
      <select>
        <option>All Papers</option>
      </select>
    </div>
    <div className="filter-options">
      <select>
        <option>Relevance</option>
      </select>
      <select>
        <option>Last 5 years</option>
      </select>
      <button className="search-button">Search Papers</button>
    </div>
  </div>
);

export default SearchBar;
