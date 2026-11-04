/**
 * The application shell: two landmarks, nothing else yet.
 *
 * The editor (black ink, the author's text) and the review pane (red ink, the agent's
 * proposals) are empty regions with accessible names. The ProseMirror editor and the
 * review list land here in later tasks; this component holds no state (INV-02: no truth
 * in the view).
 */
export function App() {
  return (
    <>
      <header>
        <h1>Tlilli</h1>
      </header>
      <main aria-labelledby="editor-heading">
        <h2 id="editor-heading">Editor</h2>
      </main>
      <aside aria-labelledby="review-heading">
        <h2 id="review-heading">Review</h2>
      </aside>
    </>
  );
}
