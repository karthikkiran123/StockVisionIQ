"use strict";
function floatchart() {
  new ApexCharts(document.querySelector("#all-earnings-graph"), {
    chart: { type: "bar", height: 50, sparkline: { enabled: !0 } },
    colors: ["#4680FF"],
    plotOptions: { bar: { columnWidth: "80%" } },
    series: [{ data: [10, 30, 40, 20, 60, 50, 20, 15, 20, 25, 30, 25] }],
    xaxis: { crosshairs: { width: 1 } },
    tooltip: {
      fixed: { enabled: !1 },
      x: { show: !1 },
      y: {
        title: {
          formatter: function (e) {
            return "";
          },
        },
      },
      marker: { show: !1 },
    },
  }).render(),
    new ApexCharts(document.querySelector("#page-views-graph"), {
      chart: { type: "bar", height: 50, sparkline: { enabled: !0 } },
      colors: ["#E58A00"],
      plotOptions: { bar: { columnWidth: "80%" } },
      series: [{ data: [10, 30, 40, 20, 60, 50, 20, 15, 20, 25, 30, 25] }],
      xaxis: { crosshairs: { width: 1 } },
      tooltip: {
        fixed: { enabled: !1 },
        x: { show: !1 },
        y: {
          title: {
            formatter: function (e) {
              return "";
            },
          },
        },
        marker: { show: !1 },
      },
    }).render(),
    new ApexCharts(document.querySelector("#total-task-graph"), {
      chart: { type: "bar", height: 50, sparkline: { enabled: !0 } },
      colors: ["#2CA87F"],
      plotOptions: { bar: { columnWidth: "80%" } },
      series: [{ data: [10, 30, 40, 20, 60, 50, 20, 15, 20, 25, 30, 25] }],
      xaxis: { crosshairs: { width: 1 } },
      tooltip: {
        fixed: { enabled: !1 },
        x: { show: !1 },
        y: {
          title: {
            formatter: function (e) {
              return "";
            },
          },
        },
        marker: { show: !1 },
      },
    }).render(),
    new ApexCharts(document.querySelector("#download-graph"), {
      chart: { type: "bar", height: 50, sparkline: { enabled: !0 } },
      colors: ["#DC2626"],
      plotOptions: { bar: { columnWidth: "80%" } },
      series: [{ data: [10, 30, 40, 20, 60, 50, 20, 15, 20, 25, 30, 25] }],
      xaxis: { crosshairs: { width: 1 } },
      tooltip: {
        fixed: { enabled: !1 },
        x: { show: !1 },
        y: {
          title: {
            formatter: function (e) {
              return "";
            },
          },
        },
        marker: { show: !1 },
      },
    }).render(),
    new ApexCharts(document.querySelector("#customer-rate-graph"), {
      chart: { type: "area", height: 300, toolbar: { show: !1 } },
      colors: ["#0d6efd"],
      fill: {
        type: "gradient",
        gradient: {
          shadeIntensity: 1,
          type: "vertical",
          inverseColors: !1,
          opacityFrom: 0.5,
          opacityTo: 0,
        },
      },
      dataLabels: { enabled: !1 },
      stroke: { width: 1 },
      plotOptions: { bar: { columnWidth: "45%", borderRadius: 4 } },
      grid: { strokeDashArray: 4 },
      series: [{ data: [30, 60, 40, 70, 50, 90, 50, 55, 45, 60, 50, 65] }],
      xaxis: {
        categories: [
          "Jan",
          "Feb",
          "Mar",
          "Apr",
          "May",
          "Jun",
          "Jul",
          "Aug",
          "Sep",
          "Oct",
          "Nov",
          "Dec",
        ],
        axisBorder: { show: !1 },
        axisTicks: { show: !1 },
      },
    }).render(),
    new ApexCharts(document.querySelector("#total-tasks-graph"), {
      chart: {
        type: "area",
        height: 60,
        stacked: !0,
        sparkline: { enabled: !0 },
      },
      colors: ["#4680FF"],
      fill: {
        type: "gradient",
        gradient: {
          shadeIntensity: 1,
          type: "vertical",
          inverseColors: !1,
          opacityFrom: 0.5,
          opacityTo: 0,
        },
      },
      stroke: { curve: "smooth", width: 2 },
      series: [{ data: [5, 25, 3, 10, 4, 50, 0] }],
    }).render()
}
document.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
    floatchart();
  }, 500);
});
