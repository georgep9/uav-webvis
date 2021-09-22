import { Bar } from 'vue-chartjs';

const maxValue = 100;
const minValue = 0;

export default {
  extends: Bar,
  props: ["chartdata"],
  data: () => ({
    options: {
      maintainAspectRatio: false,
      scales: {
        xAxes: [{ ticks: { display: false } }],
        yAxes: [{
          ticks: { 
            display: false,
            min: minValue,
            max: maxValue
          }
        }]
      },
      legend: { display: false },
      animation: {
        // draw value labels on bars
        onProgress: function() {
          var ctx = this.ctx;
          ctx.font = "14px Arial";
          ctx.textAlign = "center";
          if (this.data.datasets){
            this.data.datasets.forEach(data => {
              const value = data.label;
              const meta_data_chart = Object.values(data._meta)[0].data[0]
              const _model = meta_data_chart._model;
              const x = _model.x;
              const y = _model.y + (_model.base - _model.y)/2 + 5;
              ctx.fillText(value,x,y)
            });
          }
        },
        duration: 500
      },
      events: [],
      responsive: true
    }
  }),
  mounted () {
    this.renderChart(this.chartdata, this.options)
  },
  watch: {
    chartdata: function(val) {
      this.$data._chart.data.datasets.forEach((element, index) => {
        element.data = val.datasets[index].data;
        element.label = val.datasets[index].label;
      })
      this.$data._chart.update();
    }
  }
}