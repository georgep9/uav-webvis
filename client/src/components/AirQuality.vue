<template>
  <div id="airquality">

    <AQBarChart id="aq-bar-chart" :aqData="barData"/>
    <AQLineChart id="aq-line-chart" :histData="lineData" style="padding-top: 20px"/>
    
  </div>
</template>
<script>

import AQBarChart from './AQBarChart.vue';
import AQLineChart from './AQLineChart.vue';

import time from '../assets/js/time-func.js'

const sensCnt = 8;
const maxLineSteps = 20;

export default {

  name: 'AirQuality',

  components: {
    AQBarChart,
    AQLineChart
  },

  data: () => ({
    barData: null,
    lineData: null
  }),

  mounted() {
    setInterval(this.fetchBarData, 100);
    setInterval(this.fetchLineData, 100);
  },

  methods: {
    fetchBarData: function() {
      var newData = new Map();
      for(let i = 0; i<sensCnt; i++){
        const type = i;
        const value = Math.round(Math.random()*100) / 100;
        const scaledValue = Math.round(value*100);
        newData.set(type, {'normal': value, 'scaled': scaledValue})
      }
      this.barData = newData;
    },

  fetchLineData: function() {
    
    if (this.lineData === null) { 
      this.lineData  = new Array(new Array(), new Array());
    }
    else if (this.lineData[0].length >= maxLineSteps) { 
      this.lineData[0].shift();
      this.lineData[1].shift();
    }

    const ts = time.getTimestamp(new Date());
    const val = Math.round(Math.random()*100) / 100;
    
    this.lineData[0].push(ts);
    this.lineData[1].push(val);

  }

  }
}

</script>

<style>
</style>