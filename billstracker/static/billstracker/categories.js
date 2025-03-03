$(document).ready(function () {
  // Loading Data
  function fetchCategoriesIncome() {
    $.ajax({
      url: "/profile/settings/get-income-category-data/",
      method: "GET",
      dataType: "json",
      success: function (data) {
        var incomeTableBody = $("#incomeCategoriesTable tbody");
        incomeTableBody.empty();

        if (data.length === 0) {
          incomeTableBody.append("<tr><td colspand='2'> No Data Available</td></tr>");
        } else {
          data.forEach(function (category) {
            var row = `
              <tr>
                <td>${category.name}</td>
                <td class="text-end">
                  <button class="btn btn-outline-success btn-sm me-1 edit-category-btn" data-id="${category.id}" data-name="${category.name}" data-type="${category.category_type}"><i class="bi bi-pencil-square"></i></button>
                  <button class="btn btn-outline-danger btn-sm me-1 delete-category-btn" data-id="${category.id}" data-name="${category.name}" data-type="${category.category_type}"><i class="bi bi-trash"></i></button>
                </td>
              </tr>
            `;
            incomeTableBody.append(row);
          });
        }
      },
      error: function () {
        console.error("Failed to fetch Categories.");
      }
    });
  }

  function fetchCategoriesExpense() {
    $.ajax({
      url: "/profile/settings/get-expense-category-data/",
      method: "GET",
      dataType: "json",
      success: function (data) {
        var expenseTableBody = $("#expenseCategoriesTable tbody");
        expenseTableBody.empty();

        if (data.length === 0) {
          expenseTableBody.append("<tr><td colspand='2'> No Data Available</td></tr>");
        } else {
          data.forEach(function (category) {
            var row = `
              <tr>
                <td>${category.name}</td>
                <td class="text-end">
                  <button class="btn btn-outline-success btn-sm me-1 edit-category-btn" data-id="${category.id}" data-name="${category.name}" data-type="${category.category_type}"><i class="bi bi-pencil-square"></i></button>
                  <button class="btn btn-outline-danger btn-sm me-1 delete-category-btn" data-id="${category.id}" data-name="${category.name}" data-type="${category.category_type}"><i class="bi bi-trash"></i></button>
                </td>
              </tr>
            `;
            expenseTableBody.append(row);
          });
        }
      },
      error: function () {
        console.error("Failed to fetch Categories.");
      }
    });
  };

  fetchCategoriesIncome();
  fetchCategoriesExpense();

  // Edit Category
  $(document).on("click", ".edit-category-btn", function (event) {
    event.preventDefault();

    var categoryId = $(this).data("id");
    var categoryName = $(this).data("name");
    var categoryType = $(this).data("type");

    $("#categoryId").val(categoryId);
    $("#categoryName").val(categoryName);
    $("#categoryType").val(categoryType);

    $("#editCategoryModal").modal("show");
  });

  $(document).on("click", "#saveCategoryButton", function (event) {
    event.preventDefault();

    var categoryId = $("#categoryId").val();
    var categoryName = $("#categoryName").val();
    var categoryType = $("#categoryType").val();
    
    $.ajax({
      url: "/profile/settings/update-category/",
      type: "POST",
      data: { id: categoryId, name: categoryName, type: categoryType, csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val() },
      dataType: "json",
      success: function (response) {
        if (response.success) {
          $("#editCategoryModal").modal("hide");
          if (categoryType === "Income") {
            fetchCategoriesIncome();
          } else if (categoryType === "Expense") {
            fetchCategoriesExpense();
          }
        }
      },
      error: function (jqXHR) {
        if (jqXHR.status == 400) {
          let categoryName = document.getElementById("categoryName");
          let categoryError = document.getElementById("categoryError");

          categoryName.classList.add("is-invalid");
          categoryError.textContent = jqXHR.responseJSON.error;
          categoryError.style.display = "block";
        }
      }
    })
  });

  $(document).on("hidden.bs.modal", "#editCategoryModal", function () {
    let categoryName = document.getElementById("categoryName");
    let categoryError = document.getElementById("categoryError");

    categoryName.classList.remove("is-invalid");
    categoryError.style.display = "none";
    categoryError.textContent = "";
  });

  // Delete Category
  $(document).on("click", ".delete-category-btn", function () {
    let categoryId = $(this).data("id");
    let categoryName = $(this).data("name");
    let categoryType = $(this).data("type");

    $("#deleteCategoryId").val(categoryId);
    $("#deleteCategoryType").val(categoryType);
    $("#deleteCategoryName").text(categoryName);

    $("#deleteCategoryModal").modal("show");
  });

  $(document).on("click", "#deleteCategoryButton", function (event) {
    event.preventDefault();

    let categoryId = $("#deleteCategoryId").val();
    let category_type = $("#deleteCategoryType").val();

    $.ajax({
      url: "/profile/settings/delete-category/",
      type: "POST",
      data: {
        id: categoryId,
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
      },
      dataType: "json",
      success: function (response) {
        if (response.success) {
          $("#deleteCategoryModal").modal("hide");
          if (category_type === "Income") {
            fetchCategoriesIncome();
          } else if (category_type === "Expense") {
            fetchCategoriesExpense();
          }
        }
      },
      error: function (jqXHR) {
        if (jqXHR.status == 400) {
          let categoryError = document.getElementById("deleteCategoryError");

          categoryError.textContent = jqXHR.responseJSON.error;
          categoryError.style.display = "block";
        }
      }
    })
  });

  $(document).on("hidden.bs.modal", "#deleteCategoryModal", function () {
    let categoryError = document.getElementById("deleteCategoryError");

    categoryError.style.display = "none";
    categoryError.textContent = "";
  });

  // Add New Category - Income
  $(document).on("click", "#addCategoryIncomeButton", function (event) {
    event.preventDefault();

    let categoryName = document.getElementById("idCategoryIncomeName").value;
    let categoryType = $("#idCategoryTypeIncome").val();

    console.log("CategoryName:", categoryName, "CategoryType:", categoryType);

    $.ajax({
      url: "/profile/settings/create-category/",
      type: "POST",
      data: {
        name: categoryName,
        type: categoryType,
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
      },
      dataType: "json",
      success: function (success) {
        $("#addCategoryIncomeModal").modal("hide");
        fetchCategoriesIncome();
      },
      error: function (jqXHR) {
        if (jqXHR.status == 400) {
          let invalidFeedback = document.getElementById("invalidFeedbackIncome");
          let categoryNameInput = document.getElementById("idCategoryIncomeName");

          categoryNameInput.classList.add("is-invalid");
          invalidFeedback.style.display = "block";
          invalidFeedback.textContent = jqXHR.responseJSON.error;
        }
      }
    })
  });

  $(document).on("hidden.bs.modal", "#addCategoryIncomeModal", function () {
    let invalidFeedback = document.getElementById("invalidFeedbackIncome");
    let categoryNameInput = document.getElementById("idCategoryIncomeName");

    invalidFeedback.style.display = "none";
    invalidFeedback.textContent = "";
    categoryNameInput.classList.remove("is-invalid");
    categoryNameInput.value = "";
  });

  // Add New Category - Expense
  $(document).on("click", "#addCategoryExpenseButton", function (event) {
    event.preventDefault();

    let categoryName = document.getElementById("idCategoryExpenseName").value;
    let categoryType = $("#idCategoryTypeExpense").val();

    console.log("CategoryName:", categoryName, "CategoryType:", categoryType);

    $.ajax({
      url: "/profile/settings/create-category/",
      type: "POST",
      data: {
        name: categoryName,
        type: categoryType,
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
      },
      dataType: "json",
      success: function (success) {
        $("#addCategoryExpenseModal").modal("hide");
        fetchCategoriesExpense();
      },
      error: function (jqXHR) {
        if (jqXHR.status == 400) {
          let invalidFeedback = document.getElementById("invalidFeedbackExpense");
          let categoryNameInput = document.getElementById("idCategoryExpenseName");

          categoryNameInput.classList.add("is-invalid");
          invalidFeedback.style.display = "block";
          invalidFeedback.textContent = jqXHR.responseJSON.error;
        }
      }
    })
  });

  $(document).on("hidden.bs.modal", "#addCategoryExpenseModal", function () {
    let invalidFeedback = document.getElementById("invalidFeedbackExpense");
    let categoryNameInput = document.getElementById("idCategoryExpenseName");

    invalidFeedback.style.display = "none";
    invalidFeedback.textContent = "";
    categoryNameInput.classList.remove("is-invalid");
    categoryNameInput.value = "";
  });

});