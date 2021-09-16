<template>
  <div id="airquality">

    <AQBarChart id="aq-bar-chart" :aqData="chartdata"/>
    <AQLineChart id="aq-line-chart" style="padding-top: 20px"/>
    
  </div>
</template>
<script>

import AQBarChart from './AQBarChart.vue';
import AQLineChart from './AQLineChart.vue';

export default {

  name: 'AirQuality',

  components: {
    AQBarChart,
    AQLineChart
  },

  data: () => ({
    chartdata: null
  }),

  mounted() {
    setInterval(this.fetchChartData, 500);
  },

  methods: {
    fetchChartData: function() {
      var newData = new Map();
      for(let i = 0; i<8; i++){
        const type = i;
        const value = Math.round(Math.random()*100) / 100;
        const scaledValue = Math.round(value*100);
        newData.set(type, {'normal': value, 'scaled': scaledValue})
      }
      this.chartdata = newData;
    }
  }
}

</script>

<style>
</style>