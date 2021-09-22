<template>
  <div id="line-chart-container">
    <h4 style="text-align: center">History</h4>
    <line-chart v-if="chartdata !== null" :chartdata="chartdata" id="line-chart"></line-chart>
  </div>
</template>

<script>

import LineChart from './LineChart.js';


export default {
  name: 'AQLineChart',
  props: ['histData'],
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
            backgroundColor: '#f87979',
            data: values
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
</style>