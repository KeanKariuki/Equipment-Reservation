(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var fileInput = document.querySelector('input[type="file"][name="image"]');
    if (!fileInput) return;

    // The readonly "Current photo" preview field, so we can update it
    // live when a new file is chosen -- staff shouldn't have to save
    // and reload just to see what they picked.
    var previewRow = document.querySelector(".field-photo_preview .readonly");

    var dropzone = document.createElement("div");
    dropzone.className = "fm-dropzone";
    dropzone.innerHTML =
      '<div class="fm-dropzone__label">Drag a photo here, or use the field below to browse</div>';
    fileInput.parentNode.insertBefore(dropzone, fileInput);

    function showPreview(file) {
      if (!file || !file.type || file.type.indexOf("image/") !== 0) return;
      var reader = new FileReader();
      reader.onload = function (e) {
        if (!previewRow) return;
        var img = previewRow.querySelector("img.fm-thumb");
        if (!img) {
          previewRow.innerHTML = '<img class="fm-thumb fm-thumb--large" />';
          img = previewRow.querySelector("img.fm-thumb");
        }
        img.src = e.target.result;
        var badge = previewRow.querySelector(".fm-unsaved-badge");
        if (!badge) {
          badge = document.createElement("div");
          badge.className = "fm-unsaved-badge";
          badge.textContent = "New photo selected — not saved yet";
          previewRow.appendChild(badge);
        }
      };
      reader.readAsDataURL(file);
    }

    fileInput.addEventListener("change", function () {
      if (fileInput.files && fileInput.files[0]) {
        showPreview(fileInput.files[0]);
      }
    });

    ["dragenter", "dragover"].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add("fm-dropzone--active");
      });
    });

    ["dragleave", "drop"].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove("fm-dropzone--active");
      });
    });

    dropzone.addEventListener("click", function () {
      fileInput.click();
    });

    dropzone.addEventListener("drop", function (e) {
      var files = e.dataTransfer && e.dataTransfer.files;
      if (!files || !files.length) return;

      // Assign the dropped file to the real <input type="file"> so it's
      // actually submitted with the form, then show its preview.
      var dataTransfer = new DataTransfer();
      dataTransfer.items.add(files[0]);
      fileInput.files = dataTransfer.files;

      showPreview(files[0]);
    });
  });
})();
