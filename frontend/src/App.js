import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Inscription from './components/Inscription';
import UploadPhoto from './components/UploadPhoto';
import Validation from './components/Validation';
import Notifications from './components/Notifications';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/inscription" element={<Inscription />} />
        <Route path="/upload" element={<UploadPhoto />} />
        <Route path="/validation" element={<Validation />} />
        <Route path="/notifications" element={<Notifications />} />
      </Routes>
    </Router>
  );
}

export default App;
