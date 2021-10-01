<template>
  <div id="line-chart-container" v-if="chartdata !== null">
    <h4 style="text-align: center"> {{ sensorName.toUpperCase() }} History</h4>
    <line-chart :chartdata="chartdata" id="line-chart"></line-chart>
  </div>
</template>

<script>

import LineChart from './LineChart.js';


export default {
  name: 'AQLineChart',
  props: ['sensorName', 'histData'],
  components: { LineChart },
  data: () => ({ chartdata: null }),
  watch: {
    histData: function(data) {
      const timestamps = data[0];
      const values = data[1];
      this.chartdata = {
        labels: timestamps,
        datasets: [
          {
            data: values,
            lineTension: 0.5,
            fill: false
          }
        ]
      };

    }
  }
}
</script>

<style>
#line-chart-container {
  height: 100%;
}
#line-chart {
  width: 100%;
  max-width: 800px;
  
  height: 100%;
  max-height: 250px;
  margin: 0 auto;
}
</style>