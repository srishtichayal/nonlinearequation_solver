function readTextFile(input, callback) {
    const file = input.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
        callback(e.target.result);
    };
    reader.readAsText(file);
}

$(document).ready(function () {
    $('#equationFiles').on('change', function () {
    const files = this.files;
    if (!files.length) return;

    let fileContents = [];

    let loaded = 0;
    for (let i = 0; i < files.length; i++) {
        const reader = new FileReader();
        reader.onload = function (e) {
            fileContents[i] = e.target.result.trim();
            loaded++;
            if (loaded === files.length) {
                const combined = fileContents.join('\n---\n');
                $('#equations').val(combined);
            }
        };
        reader.readAsText(files[i]);
    }
    });

    $('#constantsFile').change(function () {
        readTextFile(this, function (text) {
            $('#constants').val(text);
        });
    });

    $('#solveBtn').click(function () {
        const solver = $('#solver').val();
        const equations = $('#equations').val();
        const constants = $('#constants').val();
        const initialGuessText = $('#initial_guesses').val();
        let initial_guesses = {};

        initialGuessText.split('\n').forEach(line => {
            const parts = line.split('=');
            if (parts.length === 2) {
                const key = parts[0].trim();
                const value = parseFloat(parts[1].trim());
                if (!isNaN(value)) {
                    initial_guesses[key] = value;
                }
            }
        });

        $.ajax({
            url: '/solve',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                solver: solver,
                equations: equations,
                constants: constants,
                initial_guesses: initial_guesses
            }),
            success: function (response) {
                if (response.success) {
                    $('#solutionBox').text(response.solution);
                } else {
                    $('#solutionBox').text("Error: " + response.error);
                }
            },
            error: function () {
                $('#solutionBox').text("An unexpected error occurred.");
            }
        });
    });

    $('#extractBtn').click(function () {
        const solver = $('#solver').val();
        const equations = $('#equations').val();
        const constants = $('#constants').val();

        $.ajax({
            url: '/extract_variables',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                solver: solver,
                equations: equations,
                constants: constants
            }),
            success: function (response) {
                if (response.success) {
                    $('#initial_guesses').text(response.solution);
                } else {
                    $('#initial_guesses').text("Error: " + response.error);
                }


            },
            error: function () {
                alert("An unexpected error occurred during variable extraction.");
            }
        });
    });


    $('#downloadBtn').click(function () {
    const solutionText = $('#solutionBox').text();
    if (!solutionText.trim()) {
        alert("There's no solution to download yet!");
        return;
    }

    const blob = new Blob([solutionText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'solution.txt';
    a.click();
    URL.revokeObjectURL(url);
    });

});
