// This is the corrected script.js with auto-switching input method based on file input

document.addEventListener('DOMContentLoaded', function() {
    initializeInputMethods();
    initializeFileUpload();
    initializeFormValidation();
    initializeWordCounter();
    initializeLoadingStates();
});

function initializeInputMethods() {
    const methodButtons = document.querySelectorAll('.method-btn');
    const inputSections = document.querySelectorAll('.input-section');
    const inputMethodField = document.getElementById('inputMethod');

    methodButtons.forEach(button => {
        button.addEventListener('click', function() {
            const method = this.dataset.method;

            methodButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            inputSections.forEach(section => section.classList.add('hidden'));
            const targetSection = document.getElementById(method + 'Input');
            if (targetSection) targetSection.classList.remove('hidden');

            inputMethodField.value = method;
            clearOtherInputs(method);
        });
    });
}

function clearOtherInputs(activeMethod) {
    const inputs = {
        text: document.getElementById('text_input'),
        file: document.getElementById('file'),
        url: document.getElementById('url_input')
    };
    Object.keys(inputs).forEach(method => {
        if (method !== activeMethod && inputs[method]) {
            inputs[method].value = '';
            if (method === 'file') hideFileName();
        }
    });
    updateWordCount();
}

function initializeFileUpload() {
    const fileInput = document.getElementById('file');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const inputMethodField = document.getElementById('inputMethod');

    fileUploadArea.addEventListener('click', function(e) {
        if (e.target !== fileInput) fileInput.click();
    });

    fileInput.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            setFileInputMethod();
            showFileName(file.name, file.size);
            validateFile(file);
        } else {
            hideFileName();
        }
    });

    fileUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            fileInput.files = files;
            setFileInputMethod();
            showFileName(file.name, file.size);
            validateFile(file);
        }
    });

    function setFileInputMethod() {
        inputMethodField.value = 'file';
        document.querySelectorAll('.method-btn').forEach(btn => btn.classList.remove('active'));
        const fileBtn = document.querySelector('[data-method="file"]');
        if (fileBtn) fileBtn.classList.add('active');
        document.querySelectorAll('.input-section').forEach(section => section.classList.add('hidden'));
        const fileInputSection = document.getElementById('fileInput');
        if (fileInputSection) fileInputSection.classList.remove('hidden');
    }
}

function showFileName(name, size) {
    const fileNameDiv = document.getElementById('fileName');
    const sizeStr = formatFileSize(size);
    fileNameDiv.innerHTML = `<strong>${name}</strong> (${sizeStr})`;
    fileNameDiv.classList.add('show');
}

function hideFileName() {
    const fileNameDiv = document.getElementById('fileName');
    fileNameDiv.classList.remove('show');
    fileNameDiv.innerHTML = '';
}