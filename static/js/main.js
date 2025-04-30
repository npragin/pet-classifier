/*
 * Pet Breed Classifier - Main JavaScript
 * Handles image upload, preview, and submission functionality
 */

document.addEventListener('DOMContentLoaded', function() {
  // Get DOM elements
  const dropArea = document.querySelector('.upload-area');
  const fileInput = document.getElementById('file-input');
  const browseButton = document.getElementById('browse-button');
  const browseAgainButton = document.getElementById('browse-again-button');
  const previewContainer = document.getElementById('preview-container');
  const imagePreview = document.getElementById('image-preview');
  const submitButton = document.getElementById('submit-button');
  const uploadForm = document.getElementById('upload-form');
  const feedbackButtons = document.querySelectorAll('.feedback-btn');

  // Handle feedback button clicks
  if (feedbackButtons.length > 0) {
    feedbackButtons.forEach(button => {
      button.addEventListener('click', async function() {
        // Get the UUID from the URL
        const uuid = window.location.pathname.split('/').pop();
        const isCorrect = this.classList.contains('correct');
        
        try {
          // Send feedback to the server
          const response = await fetch('/feedback', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              uuid: uuid,
              feedback: isCorrect
            })
          });

          const result = await response.json();
          
          if (result.success) {
            // Disable both buttons or show error message
            feedbackButtons.forEach(btn => {
              btn.disabled = true;
              btn.classList.add('disabled');
            });
            this.classList.add('selected');
          }
        } catch (error) {
          console.error('Error:', error);
        }
      });
    });
  }

  // Only initialize if we're on the upload page
  if (!dropArea) return;

  // Browse button functionality
  if (browseButton) {
      browseButton.addEventListener('click', function() {
          fileInput.click();
      });
  }
  
  // Browse again button functionality
  if (browseAgainButton) {
      browseAgainButton.addEventListener('click', function() {
          fileInput.click();
      });
  }

  // File input change event
  if (fileInput) {
      fileInput.addEventListener('change', function() {
          const file = this.files[0];
          if (file) {
              displayPreview(file);
          }
      });
  }

  // Drag and drop functionality
  if (dropArea) {
      ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
          dropArea.addEventListener(eventName, preventDefaults, false);
      });

      ['dragenter', 'dragover'].forEach(eventName => {
          dropArea.addEventListener(eventName, highlight, false);
      });

      ['dragleave', 'drop'].forEach(eventName => {
          dropArea.addEventListener(eventName, unhighlight, false);
      });

      // Handle dropped files
      dropArea.addEventListener('drop', function(e) {
          const file = e.dataTransfer.files[0];
          fileInput.files = e.dataTransfer.files;
          if (file) {
              displayPreview(file);
          }
      });
  }

  // Submit button functionality
  if (submitButton) {
      submitButton.addEventListener('click', function() {
          uploadForm.submit();
      });
  }

  // Helper functions
  function preventDefaults(e) {
      e.preventDefault();
      e.stopPropagation();
  }

  function highlight() {
      dropArea.classList.add('highlight');
  }

  function unhighlight() {
      dropArea.classList.remove('highlight');
  }

  // Display preview of selected image
  function displayPreview(file) {
      if (!file.type.match('image.*')) {
          alert('Please select an image file');
          return;
      }

      const reader = new FileReader();
      reader.onload = function(e) {
          imagePreview.setAttribute('src', e.target.result);
          previewContainer.style.display = 'block';
          if (browseButton) {
              browseButton.style.display = 'none';
          }
      }
      reader.readAsDataURL(file);
  }
});