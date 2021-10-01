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

    <AQLineChart 
      v-if="lineData !== null"
      id="aq-line-chart" 
      :sensorName="selected" 
      :histData="lineData" 
      style="padding-top: 20px"
    />
    
  </div>
</template>


<script>

import AQBarChart from './AQBarChart.vue';
import AQLineChart from './AQLineChart.vue';
import time from '../assets/js/time-func.js'

const fetchDelay = 100;
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
    lineData: new Array(new Array(), new Array()),
    lastTs: 0,
  }),

  mounted() {
    setTimeout(this.fetchData, fetchDelay);
  },

  methods: {

    changeSelection: function(sensor) {
      if (this.selected !== sensor){
        this.lineData = new Array(new Array(), new Array());
        this.selected = sensor;
      }
    },

    fetchData: async function () {

      if (this.lineData[0].length === 0 && this.selected !== null){
        const senHistData = await this.fetchSenHistData();
        if (senHistData) { this.updateLineData(senHistData); }
      } else {
        const liveData = await this.fetchLiveData();
        if(liveData) {
          this.updateBarData(liveData[liveData.length - 1].sensors);
          
          if (this.lineData[0].length !== 0) {
            this.updateLineData(liveData);
          }
        }
      }

      setTimeout(this.fetchData, fetchDelay);
    },

    fetchLiveData: async function() {

      const api_url = `${process.env.VUE_APP_API_HOST}/api/aq/live?from_ts=${this.lastTs}`;

      let liveData;
      try {
        liveData = await 
          fetch(api_url)
          .then((res) => res.json());
      } catch (e) {
        console.log('error')
        return;
      }

      if (liveData.length === 0) { return; }

      this.sensors = Object.keys(liveData[0].sensors);
      if (this.selected === null) { this.selected = this.sensors[0]; }

      this.lastTs = liveData[liveData.length - 1].ts
      
      return liveData;
    },

    fetchSenHistData: async function() {

      let sensorData;
      try {
        sensorData = await 
          fetch(`${process.env.VUE_APP_API_HOST}/api/aq/sen?sensor=${this.selected}&samples=${maxLineSteps}`)
          .then((res) => res.json());
      } catch (e) {
        return;
      }

      return sensorData;
    },

    updateBarData: function (data) {

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

    updateLineData: function(data) {

      // don't update if new data has not come through
      // if (time.getTimestamp(new Date(data.at(-1).ts)) 
      //   === this.lineData[0].at(-1)) {
      //   return; 
      // }

      //console.log(data)

      data.forEach(sample => {
        const unixTs = sample.ts;
        const ts = time.getTimestamp(new Date(unixTs))
        let val;
        if ("sensors" in sample){
          val = sample.sensors[this.selected].val;
        } else {
          val = sample.val;
        }

        if (this.lineData[0].length >= maxLineSteps) { 
          this.lineData[0].shift();
          this.lineData[1].shift();
        }

        this.lineData[0].push(ts);
        this.lineData[1].push(val);
      })
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