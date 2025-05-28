import { useEffect, useState } from 'react';
import * as Y from 'yjs';
import { yCompanies } from './yjs-setup'; // your Yjs setup file

function App() {
  // State for companies, boards, notes
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [boards, setBoards] = useState([]);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const [notes, setNotes] = useState([]);
  const [noteInput, setNoteInput] = useState('');

  // New state for “adding new” UI toggles
  const [addingCompany, setAddingCompany] = useState(false);
  const [addingBoard, setAddingBoard] = useState(false);

  // Input states for new company/board names
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newBoardName, setNewBoardName] = useState('');

  // Edit state for note input
  const [editingIndex, setEditingIndex] = useState(null);
  const [editInput, setEditInput] = useState('');


  // Load companies on mount & observe changes
  useEffect(() => {
    const updateCompanies = () => {
      setCompanies(Array.from(yCompanies.keys()));
    };
    yCompanies.observe(updateCompanies);
    updateCompanies();

    return () => yCompanies.unobserve(updateCompanies);
  }, []);

  // Load boards when selectedCompany changes
  useEffect(() => {
    if (!selectedCompany) {
      setBoards([]);
      setSelectedBoard(null);
      return;
    }

    const companyMap = yCompanies.get(selectedCompany);
    if (!companyMap) {
      setBoards([]);
      setSelectedBoard(null);
      return;
    }

    const updateBoards = () => {
      setBoards(Array.from(companyMap.keys()));
    };

    companyMap.observe(updateBoards);
    updateBoards();

    return () => companyMap.unobserve(updateBoards);
  }, [selectedCompany]);

  // Load notes when selectedBoard changes
  useEffect(() => {
    if (!selectedCompany || !selectedBoard) {
      setNotes([]);
      return;
    }
    const companyMap = yCompanies.get(selectedCompany);
    if (!companyMap) {
      setNotes([]);
      return;
    }
    const boardNotes = companyMap.get(selectedBoard);
    if (!boardNotes) {
      setNotes([]);
      return;
    }

    // Observe changes on the notes Y.Array
    const updateNotes = () => {
      setNotes(boardNotes.toArray());
    };
    boardNotes.observe(updateNotes);
    updateNotes();

    return () => boardNotes.unobserve(updateNotes);
  }, [selectedCompany, selectedBoard]);

  // Add new company
  const addCompany = () => {
    const name = newCompanyName.trim();
    if (name && !yCompanies.has(name)) {
      yCompanies.set(name, new Y.Map());
      setNewCompanyName('');
      setSelectedCompany(name);
    }
  };

  // Add new board
  const addBoard = () => {
    const name = newBoardName.trim();
    if (!name || !selectedCompany) return;
    const companyMap = yCompanies.get(selectedCompany);
    if (companyMap && !companyMap.has(name)) {
      companyMap.set(name, new Y.Array());
      setNewBoardName('');
      setSelectedBoard(name);
    }
  };

  // Add note to selected board
  const addNote = () => {
    if (!selectedCompany || !selectedBoard || noteInput.trim() === '') return;
    const companyMap = yCompanies.get(selectedCompany);
    if (!companyMap) return;
    const boardNotes = companyMap.get(selectedBoard);
    if (!boardNotes) return;
    boardNotes.push([noteInput.trim()]);
    setNoteInput('');
  };

 {selectedBoard && (
  <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
    <h2>Notes for {selectedCompany} / {selectedBoard}</h2>

    <div style={{ flex: 1, overflowY: 'auto', border: '1px solid #ccc', padding: '0.5rem' }}>
      {notes.length === 0 && <p>No notes yet.</p>}
      {notes.map((note, i) => (
        <div key={i} style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center' }}>
          {editingIndex === i ? (
            <>
              <input
                type="text"
                value={editInput}
                onChange={e => setEditInput(e.target.value)}
                style={{ flex: 1 }}
              />
              <button
                onClick={() => {
                  if (editInput.trim() === '') return;
                  // Update note in Yjs
                  const companyMap = yCompanies.get(selectedCompany);
                  if (!companyMap) return;
                  const boardNotes = companyMap.get(selectedBoard);
                  if (!boardNotes) return;

                  boardNotes.delete(i, 1);
                  boardNotes.insert(i, [editInput.trim()]);

                  setEditingIndex(null);
                }}
                style={{ marginLeft: '0.5rem' }}
              >
                Save
              </button>
              <button
                onClick={() => setEditingIndex(null)}
                style={{ marginLeft: '0.5rem' }}
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <div style={{ flex: 1, whiteSpace: 'pre-wrap' }}>{note}</div>
              <button
                onClick={() => {
                  setEditingIndex(i);
                  setEditInput(note);
                }}
                style={{ marginLeft: '0.5rem' }}
              >
                Edit
              </button>
              <button
                onClick={() => {
                  // Delete note in Yjs
                  const companyMap = yCompanies.get(selectedCompany);
                  if (!companyMap) return;
                  const boardNotes = companyMap.get(selectedBoard);
                  if (!boardNotes) return;

                  boardNotes.delete(i, 1);
                }}
                style={{ marginLeft: '0.5rem' }}
              >
                Delete
              </button>
            </>
          )}
        </div>
      ))}
    </div>
  </div>
)}
}


export default App;
