document.getElementById("idNewFeedbackForm").addEventListener("submit", function (event) {
  event.preventDefault();

  let name = document.getElementById("idFeedbackFormName").value;
  let message = document.getElementById("idFeedbackFormMessage").value;
  let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  let errormessage = document.getElementById("feedbackError");

  fetch("/feedback/add-feedback/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken
    },
    body: JSON.stringify({ name: name, message: message }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      let table = document.getElementById("feedbackTable").getElementsByTagName("tbody")[0];
      let modal = bootstrap.Modal.getInstance(document.getElementById("newFeedbackModal"));

      let newRow = table.insertRow();
      newRow.innerHTML = `
        <td>${data.message}</td>
        <td></td>
        <td><input type="checkbox" class="form-check-input" disabled></td>`;

        document.getElementById("idFeedbackFormName").value = "";
        document.getElementById("idFeedbackFormMessage").value = "";
        errormessage.style.display = "none";

        modal.hide();
    } else {
      errormessage.textContent = data.error;
      errormessage.style.display = "block";
    }
  })
  .catch(error => console.error("Error:", error));
});

document.addEventListener("change", function (event) {
  if (event.target.matches("input[type='checkbox']")) {
    let feedbackId = event.target.getAttribute("data-id");
    
    console.log("Feedback ID: ", feedbackId)
  }
});