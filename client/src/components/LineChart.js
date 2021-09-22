import { Line } from 'vue-chartjs';


export default {
  extends: Line,
  props: ["chartdata"],
  data: () => ({
    options: {
      maintainAspectRatio: false,
      responsive: true,
      legend: { display: false }
    }
  }),
  mounted () {
    this.renderChart(this.chartdata, this.options);
  },
  watch: {
    chartdata: function(val) {
      this.$data._chart.data.labels = val.labels;
      this.$data._chart.data.datasets[0].data = val.datasets[0].data;
      console.log(this.$data._chart.data);
      this.$data._chart.update();
    }
  }
}