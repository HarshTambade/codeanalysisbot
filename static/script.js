document.addEventListener('DOMContentLoaded', () => {
    const difficultySelect = document.getElementById('difficulty');
    const questionTextArea = document.getElementById('question');
    const form = document.getElementById('codeForm');

    async function fetchQuestion() {
        const difficulty = difficultySelect.value;
        const response = await fetch(`/get_question?difficulty=${difficulty}`);
        const data = await response.json();

        if (response.ok) {
            questionTextArea.value = data.question;
        } else {
            questionTextArea.value = "Error fetching question: " + data.error;
        }
    }

    difficultySelect.addEventListener('change', fetchQuestion);

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const difficulty = difficultySelect.value;
        const userCode = document.getElementById('userCode').value;
        const question = questionTextArea.value;

        const response = await fetch('/analyze_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty, userCode, expected_output: question })
        });

        const result = await response.json();

        document.getElementById('syntaxValid').innerText = result.syntax_valid ? 'Yes' : 'No';
        document.getElementById('functionCheck').innerText = result.function_check;
        document.getElementById('logicCheck').innerText = result.logic_check;
        document.getElementById('qualityCheck').innerText = result.quality_check;
        document.getElementById('score').innerText = result.score;
    });

    fetchQuestion(); // Fetch initial question on page load
});
