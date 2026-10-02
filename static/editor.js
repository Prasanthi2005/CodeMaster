// ==========================================
// CodeMaster - Monaco Editor
// ==========================================

require.config({
    paths: {
        vs: "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs"
    }
});

let editor;

require(["vs/editor/editor.main"], function() {

    editor = monaco.editor.create(document.getElementById("editor"), {
        value: "# Write your code here\n",
        language: "python",
        theme: "vs-dark",
        automaticLayout: true
    });

    // Restore saved code
    const saved = localStorage.getItem("codemaster_code");
    if (saved) {
        editor.setValue(saved);
    }

    // Run button
    document.getElementById("runBtn").addEventListener("click", runCode);

    // Language change
    document.getElementById("language").addEventListener("change", function() {
        let lang = this.value;

        if (lang === "cpp") {
            lang = "cpp";
        }

        monaco.editor.setModelLanguage(editor.getModel(), lang);
    });
});

// ==========================================
// Run Code
// ==========================================

async function runCode() {

    const code = editor.getValue();
    const input = document.getElementById("input").value;
    const language = document.getElementById("language").value;

    try {

        const response = await fetch("/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                language: language,
                code: code,
                input: input
            })
        });

        const result = await response.json();

        document.getElementById("output").textContent =
            result.error ? result.error : result.output;
        const output = document.getElementById("output");
        output.scrollTop = output.scrollHeight;

    } catch (err) {

        document.getElementById("output").textContent =
            "Error: " + err.message;

    }

    // Save code
    localStorage.setItem("codemaster_code", code);
}

// ==========================================
// Ctrl + S
// ==========================================

document.addEventListener("keydown", function(event) {

    if (event.ctrlKey && event.key === "s") {

        event.preventDefault();

        if (editor) {
            localStorage.setItem("codemaster_code", editor.getValue());
        }
    }
});