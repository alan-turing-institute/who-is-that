function showContextMenu(event) {
    const dropdown = document.getElementById("dropdown");
    const dynamicContent = document.getElementById("dynamic-content");
    const elemSelectedText = document.getElementById("selected-text");
    const elemSelectedTextContext = document.getElementById("selected-text-context");

    event.preventDefault();

    // Extract and trim selected text
    const selectedRange = window.getSelection().getRangeAt(0);
    const selectedText = selectedRange.toString().replace(/\s\s+/g, " ").trim()
    if (selectedText) {
        // Extract text up to selection
        const preRange = document.createRange();
        preRange.selectNodeContents(dynamicContent);
        preRange.setEnd(selectedRange.startContainer, selectedRange.startOffset);

        // Replace repeated whitespace with a single space and trim
        const selectedTextContext = preRange.toString().replace(/\s\s+/g, " ").trim()

        // Save the selection and context into hidden DOM elements
        elemSelectedTextContext.value = selectedTextContext
        elemSelectedText.value = selectedText

        // Show the dropdown
        dropdown.style.display = "block";
        dropdown.style.left = `${event.pageX}px`;
        dropdown.style.top = `${event.pageY}px`;
    } else {
        dropdown.style.display = "none";
    }
}

function hideContextMenu(event) {
    const dropdown = document.getElementById("dropdown");
    if (!dropdown.contains(event.target)) {
        dropdown.style.display = "none";
    }
}

function modalHelper(content) {

    let modal = document.getElementById('summary-modal');
    // Check if the modal exists
    if (!modal) {
        // Create the modal if it doesn't exist
        console.log('Creating modal')
        modal = document.createElement('div');
        modal.id = 'summary-modal';
    }
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-background"></div>
        <div class="modal-content">
            <!-- Content will be inserted here -->
        </div>
        <button class="modal-close is-large" aria-label="close"></button>
    `;
    document.body.appendChild(modal);

    // Add event listener to close button
    modal.querySelector('.modal-close').addEventListener('click', () => {
        modal.classList.remove('is-active');
    });

    if (content == null) {
        title = 'Please wait while I read the book...';
        text = '';
    } else {
        title = content.question;
        text = content.summary;
    }
    // Update modal content
    modal.querySelector('.modal-content').innerHTML = `
        <div class="box">
            <h2 class="title">${title}</h2>
            <p>${text}</p>
        </div>
    `;

    if (content == null) {
        // Show a progress bar
        let progress = document.createElement('progress');
        progress.className = 'progress is-large is-warning';
        progress.max = 100;
        modal.querySelector('.modal-content').appendChild(progress);
    } else {
        // Create the Close button programmatically
        let closeButton = document.createElement('button');
        closeButton.className = 'button is-warning is-centered';
        closeButton.textContent = 'Close';
        closeButton.addEventListener('click', () => {
            modal.classList.remove('is-active');
        });

        // Append the Close button to the modal content
        modal.querySelector('.modal-content').appendChild(closeButton);
    }

    // Show the modal
    modal.classList.add('is-active');
}


// If we need to wait for the response, we can't go through the form submission
// Using Fetch API instead
function submitQuery(option) {

    // Prevent the default form submission
    event.preventDefault();

    document.getElementById("option").value = option;

    // Gather form data
    const formData = new FormData(document.getElementById("query-form"));

    console.log(formData);

    // Remove the dropdown
    const dropdown = document.getElementById("dropdown");
    dropdown.style.display = "none";

    // TODO: Indicate loading
    modalHelper();

    fetch('/query', {
        method: 'POST',
        body: formData // Send the form data
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        modalHelper(data);
    })
    .catch(error => {
        console.error('Error:', 'Failed to get answer to query.\n' + error );
    });
}