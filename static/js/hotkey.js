  document.addEventListener("keydown", function (e) {
    // Example: Ctrl+Shift+S to reveal
    if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === "s") {
      const label = document.getElementById("serverLocation");
      if (label) {
        const isVisible = label.style.display !== "none";
        label.style.display = isVisible ? "none" : "inline";
      }
    }
  });
