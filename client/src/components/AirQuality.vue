<template>
  <div id="airquality">

    <div id="aq-live" v-if="barData !== null">
      <AQBarChart id="aq-bar-chart" :aqData="barData" />
    </div>

    <div id="aq-history" v-if="lineData !== null">

      <div id="sensor-buttons">
        <button id="sensor-button" type="button"
          style="
            font-size: max(min(1.5vw, 16px), 9px); 
            font-weight:bold;
            margin:1%;
            width:12%;
            padding:0
          "
          v-for="sensor in sensors" :key="sensor" :ref="sensor"
          v-bind:class="[selected === sensor ? 'btn btn-primary' : 'btn btn-secondary']"
          v-on:click="changeHistory(sensor)">
          {{ sensor.toUpperCase() }}
        </button>
      </div>

      <AQLineChart 
        id="aq-line-chart" 
        :sensorName="selected" 
        :histData="lineData" 
        style="padding-top: 20px"
      />
    
    </div>
    
  </div>
</template>


<script>

import AQBarChart from './AQBarChart.vue';
import AQLineChart from './AQLineChart.vue';
import time from '../assets/js/time-func.js'

const updateDelay = 50;

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
    refreshHist: true,

    barData: null,
    barDataMax: {},
    barDataMin: {},

    lineData: new Array(
      new Array(), 
      new Array()
    ),

    maxHistSamples: 20
  }),


  mounted() {
    setTimeout(this.updateAirQuality, Math.round(updateDelay));
  },


  methods: {

    updateAirQuality: async function () {

      await this.fetchData();
      this.updateChartData();
      setTimeout(this.updateAirQuality, updateDelay);

    },

    changeHistory: function(sensor) {
      if (sensor === this.selected) { return; }

      this.lineData = new Array(
        new Array(), 
        new Array()
      );
      this.selected = sensor;
      this.refreshHist = true
    },

    fetchData: async function () {

      let fetchHist = false;
      if (this.selected !== null && this.refreshHist) {
        fetchHist = true;
        this.refreshHist = false;
      }

      if (fetchHist === true){
        const fetchedData = await this.fetchSenHistData();
        if (fetchedData) { this.histData = { new:true, data:fetchedData }; }
      }
      else {
        const fetchedData = await this.fetchLiveData();
        if (fetchedData) { this.liveData = { new:true, data:fetchedData }; }
      }

    },


    updateChartData: function() {

      if (this.liveData.new === false && this.histData.new === false)
      { return; }

      const lData = JSON.parse(JSON.stringify(this.liveData.data));
      const hData = JSON.parse(JSON.stringify(this.histData.data));
      const lNew = this.liveData.new;
      const hNew = this.histData.new;
      this.sensors = Object.keys(lData[0].sensors);

      this.liveData.new = false;
      this.histData.new = false;

      if (lNew === true) { 
        this.lastTs = lData[lData.length - 1].ts
        this.updateBarData(lData);
        if (this.selected !== null)
        { this.updateLineData(lData); }
      }
      else if (hNew === true){
        this.lastTs = hData[hData.length - 1].ts
        this.updateLineData(hData);
      }

      if (this.selected === null) 
      { this.selected = this.sensors[0]; }
  
    },


    fetchLiveData: async function() {
      const apiEndpoint = `${process.env.VUE_APP_API_HOST}/api/aq/live`;
      const apiArgs = `?from_ts=${this.lastTs}`;
      const apiUrl = apiEndpoint + apiArgs ;

      let apiData;
      try { apiData = await fetch(apiUrl).then((res) => res.json()); }
      catch (e) { return; }
      if (apiData.length === 0) { return; }

      return apiData;
    },


    fetchSenHistData: async function() {
      const apiEndpoint= `${process.env.VUE_APP_API_HOST}/api/aq/sen`
      const apiArgs = `?sensor=${this.selected}&samples=${this.maxHistSamples}`;
      const apiUrl = apiEndpoint + apiArgs;

      let apiData;
      try { apiData = await fetch(apiUrl).then((res) => res.json()); } 
      catch (e) { return; }

      return apiData;
    },

    
    updateBarData: function (data) {
      const sensorsData = data[data.length - 1].sensors;

      var newBarData = new Map();
      this.sensors.forEach(sensor => {
        const val = sensorsData[sensor].val;
        
        // update normalisation scales
        if (!Object.prototype.hasOwnProperty.call(this.barDataMax, sensor) ||
            this.barDataMax[sensor] < val)
        { this.barDataMax[sensor] = val; }

        if (!Object.prototype.hasOwnProperty.call(this.barDataMin, sensor) ||
            this.barDataMin[sensor] > val)
        { this.barDataMin[sensor] = val; }

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
    },

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