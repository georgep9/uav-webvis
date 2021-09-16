<template>
  <div id="bar-chart-container">
    <h4 style="text-align: center">Air Quality</h4>
    <bar-chart v-if="chartdata !== null" :chartdata="chartdata" id="bar-chart"></bar-chart>
  </div>
</template>

<script>

import BarChart from './BarChart.js';

export default {
  name: 'AQBarChart',
  components: { BarChart },
  props: ['aqData'],
  data: () => ({ chartdata: null }),
  watch: {
    aqData: function(data) {
      var newData = {datasets: []}
      data.forEach((value) => {
        newData.datasets.push({
          label: value.normal,
          barPercentage: 0.75,
          categoryPercentage: 1.0,
          data: [value.scaled]
        })
      })
      this.chartdata = newData;
    }
  }
}
</script>

<style>
#bar-chart-container {
  height: 100%;
}
#bar-chart {
  width: 100%;
  max-width: 800px;
  
  height: 100%;
  max-height: 250px;
  margin: 0 auto;
}
</style>