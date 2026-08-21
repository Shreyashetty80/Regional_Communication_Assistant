import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Language from "./pages/Language";
import Chat from "./pages/Chat";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/language" element={<Language />} />

        <Route path="/chat" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;