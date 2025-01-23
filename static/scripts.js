document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");
    form.addEventListener("submit", (event) => {
        let valid = true;
        const inputs = form.querySelectorAll("input[type='number']");

        inputs.forEach(input => {
            const value = parseInt(input.value);
            const min = parseInt(input.min);
            const max = parseInt(input.max);

            if (isNaN(value) || value < min || value > max) {
                alert(`${input.previousElementSibling.textContent} must be between ${min} and ${max}`);
                valid = false;
                input.focus();
            }
        });

        if (!valid) {
            event.preventDefault();
        }
    });

    const resultsLink = document.querySelector("a[href='/results']");
    resultsLink.addEventListener("click", (event) => {
        const confirmNavigate = confirm("Are you sure you want to navigate to the results page?");
        if (!confirmNavigate) {
            event.preventDefault();
        }
    });
});
