let searchTimeout

$(document).ready(function() {
  var billsListUrl = $("#bills-list-url").data("url");
  var billsTableBody = $("#billsTableBody");

  function fetchBills(month = '', search = '', showAll) {
    $.ajax({
      url: billsListUrl,
      method: "GET",
      data: {month_filter: month, search_input: search, show_all_bills: showAll},
      dataTpye: "json",
      success: function (data) {
        billsTableBody.empty();

        console.log(data);

        if (data.length === 0) {
          billsTableBody.append("<tr><td colspan='3'>No Bills Avaialble</td></tr>");
        } else {
          data.forEach(function (bill) {
            var formattedAmount = Number(bill.amount_payable).toLocaleString("en-US", {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            });

            var row = `
              <tr>
                <td>${bill.bill_detail__name}</td>
                <td>${bill.bill_detail__category__name}</td>
                <td>${bill.due_date}</td>
                <td>&#8369; ${formattedAmount}</td>
                <td>
                  <a href="/bills-tracker/bill/${bill.id}" class="btn btn-outline-primary btn-sm me-1"><i class="bi bi-info-circle"></i></a>
                  <a href="/bills-tracker/bill/update-bill/${bill.id}" class="btn btn-outline-success btn-sm me-1"><i class="bi bi-pencil-square"></i></a>
                  <a href="/bills-tracker/bill/pay-bill/${bill.id}/${bill.bill_detail__id}" class="btn btn-outline-warning btn-sm me-1"><i class="bi bi-wallet2"></i></a>
                </td>
              </tr>
            `;
            billsTableBody.append(row);
          })
        }
      },
      error: function () {
        console.error("Failed to fetch bills.");
      }
    });
  }


  fetchBills();

  $("#idSearchInput").on("input", function () {
    clearTimeout(searchTimeout);

    searchTimeout = setTimeout(() => {
      var selectedMonth = $("#idBillsMonthFilter").val();
      var searchInput = $("#idSearchInput").val();
      var showAllBills = $("#idShowAllBills").is(":checked");

      if (searchInput.length > 0 || selectedMonth) {
        fetchBills(selectedMonth, searchInput, showAllBills);
      }
    }, 500);
  });

  $("#idBillsMonthFilter").change(function () {
    var selectedMonth = $("#idBillsMonthFilter").val();
    var searchInput = $("#idSearchInput").val();
    var showAllBills = $("#idShowAllBills").is(":checked");

    fetchBills(selectedMonth, searchInput, showAllBills);
  });

  $("#idShowAllBills").change(function () {
    var selectedMonth = $("#idBillsMonthFilter").val();
    var searchInput = $("#idSearchInput").val();
    var showAllBills = $("#idShowAllBills").is(":checked");

    fetchBills(selectedMonth, searchInput, showAllBills);
  });

})