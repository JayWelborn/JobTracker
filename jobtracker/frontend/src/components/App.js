import React from "react";
import ReactDOM from "react-dom";

export const App = () => (
  <h1>Hello Django React</h1>
);
const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App />, wrapper) : null;