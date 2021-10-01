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

const fetchDelay = 50;
const updateDelay = 100;

export default {

  name: 'AirQuality',

  components: {
    AQBarChart,
    AQLineChart
  },

  data: () => ({
    sensors: [],
    selected: null,

    lastTs: 0,
    liveData: {new: false, data: null},
    histData: {new: false, data: null},

    barData: null,
    barDataMax: {},
    barDataMin: {},

    lineData: new Array(new Array(), new Array()),

    maxHistSamples: 20
  }),

  mounted() {
    setTimeout(this.fetchData, Math.round(fetchDelay/2));
    setInterval(this.updateChartData, updateDelay);
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
        const fetchedData = await this.fetchSenHistData();
        if (fetchedData) { 
          this.histData.new = true;
          this.histData.data = fetchedData; 
        }
      } 
      else {
        const fetchedData = await this.fetchLiveData();
        if(fetchedData) {
          this.liveData.new = true;
          this.liveData.data = fetchedData;
        }
      }

      setTimeout(this.fetchData, fetchDelay);
    },

    updateChartData: function() {

      if (this.liveData.new === false && this.histData.new === false) {
        return;
      }

      else if (this.liveData.new === true && this.histData.new === false) {
        const chartData = this.liveData.data;

        this.lastTs = chartData[chartData.length - 1].ts
        this.sensors = Object.keys(chartData[0].sensors);
        if (this.selected === null) { this.selected = this.sensors[0]; }

        this.updateBarData(chartData[chartData.length - 1].sensors)
        if (this.lineData[0].length > 0) { this.updateLineData(chartData); }

        this.liveData.new = false;
      }

      else if (this.histData.new === true) {

        this.updateLineData(this.histData.data);
        this.histData.new = false;
      }
    },

    fetchLiveData: async function() {
      const apiUrl = `${process.env.VUE_APP_API_HOST}/api/aq/live?from_ts=${this.lastTs}`;

      let apiData;
      try { apiData = await fetch(apiUrl).then((res) => res.json()); }
      catch (e) { return; }
      if (apiData.length === 0) { return; }

      return apiData;
    },

    fetchSenHistData: async function() {
      let apiUrl = `${process.env.VUE_APP_API_HOST}/api/aq/sen`
      apiUrl += `?sensor=${this.selected}&samples=${this.maxHistSamples}`;

      let apiData;
      try { apiData = await fetch(apiUrl).then((res) => res.json()); } 
      catch (e) { return; }

      return apiData;
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

      data.forEach(sample => {
        const unixTs = sample.ts;
        const ts = time.getTimestamp(new Date(unixTs))
        const val = sample.sensors[this.selected].val;

        if (this.lineData[0].length >= this.maxHistSamples) { 
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