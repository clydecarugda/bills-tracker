var colorPalette = [
  "#25CCF7","#FD7272","#54a0ff","#00d2d3",
  "#1abc9c","#2ecc71","#3498db","#9b59b6","#34495e",
  "#16a085","#27ae60","#2980b9","#8e44ad","#2c3e50",
  "#f1c40f","#e67e22","#e74c3c","#ecf0f1","#95a5a6",
  "#f39c12","#d35400","#c0392b","#bdc3c7","#7f8c8d",
  "#55efc4","#81ecec","#74b9ff","#a29bfe","#dfe6e9",
  "#00b894","#00cec9","#0984e3","#6c5ce7","#ffeaa7",
  "#fab1a0","#ff7675","#fd79a8","#fdcb6e","#e17055",
  "#d63031","#feca57","#5f27cd","#54a0ff","#01a3a4"
];

$(document).ready(function () {
  var monthlyExpenseUrl = $("#monthly-expense-url").data("url");
  var incomeExpenseUrl = $("#income-expense-url").data("url");
  var expenseTrendsUrl = $("#expense-trend-url").data("url");

  var monthlyExpense = document.getElementById("monthlyExpenseBreakdown").getContext("2d");
  var incomeExpense = document.getElementById("incomeExpenseBreakdown").getContext("2d");
  var expenseTrend = document.getElementById("ExpenseTrendBreakdown").getContext("2d");

  const noDataPlugin = {
    id: 'noData',
    beforeDraw: function (chart) {
      let hasData = chart.data.datasets.some(dataset => dataset.data.length > 0 && dataset.data.some(value => value > 0));

      if (!hasData) {
        const ctx = chart.ctx;
        const { width, height } = chart;

        ctx.save();
        ctx.font = '16px Arial';
        ctx.fillStyle = 'gray';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No Data Available', width / 2, height / 2);
        ctx.restore();
      }
    }
  };  

  var monthlyExpenseChart = new Chart(monthlyExpense, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: '',
        data: [],
        backgroundColor: colorPalette,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    },
    plugins: [noDataPlugin]
  });

  var incomeExpenseChart = new Chart(incomeExpense, {
    type: "bar",
    data: {
      labels: [],
      datasets: [{
        label: '',
        data: [],
        backgroundColor: colorPalette,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    },
    plugins: [noDataPlugin]
  });

  var expenseTrendChart = new Chart(expenseTrend, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: '',
        data: [],
        backgroundColor: colorPalette,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
    },
    plugins: [noDataPlugin]
  });

  function fetchMonthlyExpenseData(month = '') {
    $.ajax({
      url: monthlyExpenseUrl,
      data: { month: month },
      dataType: "json",
      success: function (data) {
        monthlyExpenseChart.data.labels = [];
        monthlyExpenseChart.data.datasets[0].data = [];

        monthlyExpenseChart.data.labels = data.labels;
        monthlyExpenseChart.data.datasets[0].data = data.values;
        monthlyExpenseChart.update();
      }
    });
  }

  function fetchIncomeExpenseData(month = '') {
    $.ajax({
      url: incomeExpenseUrl,
      data: { month: month },
      dataType: "json",
      success: function (data) {
        incomeExpenseChart.data.labels = [];
        incomeExpenseChart.data.datasets[0].data = [];

        incomeExpenseChart.data.labels = data.labels;
        incomeExpenseChart.data.datasets[0].data = data.values;
        incomeExpenseChart.update();
      }
    })
  }

  function fetchExpenseTrendData(value = '') {
    $.ajax({
      url: expenseTrendsUrl,
      data: { option: value },
      dataType: "json",
      success: function (data) {
        expenseTrendChart.data.labels = [];
        expenseTrendChart.data.datasets[0].data = [];

        expenseTrendChart.data.labels = data.labels;
        expenseTrendChart.data.datasets[0].data = data.values;
        expenseTrendChart.update();
      }
    })
  }

  fetchMonthlyExpenseData($("#id_monthly_expense_month").val());
  fetchIncomeExpenseData($('#id_income_expense_month').val());
  fetchExpenseTrendData($('#id_expense_trend_selection').val());

  $("#id_monthly_expense_month_filter").click(function () {
    var selectedMonth = $("#id_monthly_expense_month").val();

    fetchMonthlyExpenseData(selectedMonth)
  });

  $("#id_income_expense_month_filter").click(function () {
    var selectedMonth = $("#id_income_expense_month").val();

    fetchIncomeExpenseData(selectedMonth);
  })

  $("#id_expense_trend_filter").click(function () {
    var selectedOption = $("#id_expense_trend_selection").val();

    fetchExpenseTrendData(selectedOption);
  })

});