import * as Y from 'yjs';
import { WebrtcProvider } from 'y-webrtc';
import { IndexeddbPersistence } from 'y-indexeddb';

// Create the shared document
const ydoc = new Y.Doc();

// This sets up local persistence in IndexedDB under the name 'notes-ydoc'
const persistence = new IndexeddbPersistence('notes-ydoc', ydoc);

// Log when the data has been loaded from IndexedDB
persistence.once('synced', () => {
  console.log('Loaded data from IndexedDB');
});

// Connect to other peers in the 'notes-room' room
const provider = new WebrtcProvider('notes-room', ydoc);

// Log WebRTC connection status
provider.on('status', (event) => {
  console.log('WebRTC status:', event.status); // connected or disconnected
});

// The shared array of notes
const yCompanies = ydoc.getMap('companies');

export { yCompanies };
export { ydoc, provider, persistence };