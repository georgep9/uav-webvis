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

const maxLineSteps = 20;

export default {

  name: 'AirQuality',

  components: {
    AQBarChart,
    AQLineChart
  },

  data: () => ({
    sensors: [],
    barData: null,
    barDataMax: {},
    barDataMin: {},
    lineData: null
  }),

  mounted() {
    setInterval(this.fetchBarData, 1000);
    setInterval(this.fetchLineData, 100);
  },

  methods: {

    fetchBarData: async function() {

      let liveData;
      try {
        liveData = await 
          fetch(`${process.env.VUE_APP_API_HOST}/api/aq/live`)
          .then((res) => res.json());
      } catch (e) {
        console.log('error')
        return;
      }

      const data = liveData.sensors;
      const sensors = Object.keys(data);

      var newBarData = new Map();
      sensors.forEach(sensor => {

        const val = data[sensor].val;
        
        // update normalisation scales
        if (!Object.prototype.hasOwnProperty.call(this.barDataMax, sensor) 
            || this.barDataMax[sensor] < val) {
          this.barDataMax[sensor] = val;
        }
        if (!Object.prototype.hasOwnProperty.call(this.barDataMin, sensor) 
            || this.barDataMin[sensor] > val) {
          this.barDataMin[sensor] = val;
        }

        const scaledVal = val / this.barDataMax[sensor] * 100;
        newBarData.set(sensor, {'normal': val, 'scaled': scaledVal})

      });
      this.barData = newBarData;
    },

    fetchLineData: async function() {

      let sensorData;
      try {
        sensorData = await 
          fetch(`${process.env.VUE_APP_API_HOST}/api/aq/sen`)
          .then((res) => res.json());
      } catch (e) {
        return;
      }
      
      const unixTs = sensorData.ts;
      const ts = time.getTimestamp(new Date(unixTs));
      const val = sensorData.val;

      if (this.lineData === null) { 
        // [[ts], [val]]
        this.lineData  = new Array(new Array(), new Array());
      }
      else if (this.lineData[0].length >= maxLineSteps) { 
        this.lineData[0].shift();
        this.lineData[1].shift();
      }
      
      this.lineData[0].push(ts);
      this.lineData[1].push(val);

    }

  }
}

</script>

<style>
</style>