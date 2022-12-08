function deleteNote(noteId) {
    fetch("/delete-note",{
        method: "POST",
        body: JSON.stringify({ noteId: noteId })
    }).then((_res) => {
        window.location.href="/";
    });
}

function deleteUser(userId) {
    fetch("/delete-user", {
        method: "POST",
        body: JSON.stringify({userId: userId})
    }).then((_res) => {
        window.location.href="/admin"
    })
}

function deleteNoteAdmin(noteId) {
    fetch("/delete-note-admin",{
        method: "POST",
        body: JSON.stringify({ noteId: noteId })
    }).then((_res) => {
        window.location.href="/admin";
    });
}
