<template>
  <div id="airquality">

    <AQBarChart id="aq-bar-chart" :aqData="barData"/>
    
    <div id="sensor-buttons">
      <button id="sensor-button" type="button"
        style="font-size: max(min(1.5vw, 16px), 9px); font-weight:bold; margin:1%; width:12%; padding:0"
        v-for="sensor in sensors" :key="sensor" :ref="sensor"
        v-bind:class="[selected === sensor ? 'btn btn-primary' : 'btn btn-secondary']"
        v-on:click="changeSelection(sensor)">
        {{ sensor.toUpperCase() }}
      </button>
    </div>

    <AQLineChart id="aq-line-chart" :sensorName="selected" :histData="lineData" style="padding-top: 20px"/>
    
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
    selected: null,
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

    changeSelection: function(sensor) {
      this.lineData = null;
      this.selected = sensor; 
    },

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
      this.sensors = Object.keys(data);

      if (this.selected === null) { this.selected = this.sensors[0]; }
      
      var newBarData = new Map();
      this.sensors.forEach(sensor => {
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

      if (this.selected === null) {return;}

      let sensorData;
      try {
        sensorData = await 
          fetch(`${process.env.VUE_APP_API_HOST}/api/aq/sen?sensor=${this.selected}`)
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
#sensor-buttons {
  display: flex; 
  justify-content: space-around;
  margin:0 auto;
  max-width: 800px;
  padding-left:1%;
}
</style>