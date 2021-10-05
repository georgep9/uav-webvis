<template>
  <div id="airquality">

    <div id="aq-live" v-if="charts.live.barData !== null">
      <AQBarChart id="aq-bar-chart" :aqData="charts.live.barData" />
    </div>

    <div id="aq-history" v-if="charts.hist.lineData !== null">

      <div id="sensor-buttons">
        <button id="sensor-button" type="button"
          style="
            font-size: max(min(1.5vw, 16px), 9px); 
            font-weight:bold;
            margin:1%;
            width:12%;
            padding:0
          "
          v-for="sensor in charts.sensors" :key="sensor" :ref="sensor"
          v-bind:class="[charts.selected === sensor ? 'btn btn-primary' : 'btn btn-secondary']"
          v-on:click="changeHistory(sensor)">
          {{ sensor.toUpperCase() }}
        </button>
      </div>

      <AQLineChart 
        id="aq-line-chart" 
        :sensorName="charts.selected" 
        :histData="charts.hist.lineData" 
        style="padding-top: 20px"
      />

      <div id="history-range">
        <p id="history-range-text" style="margin:0"><b>Range:</b> {{charts.hist.maxHistSamples}} samples</p>
        <input id="history-range-input" type="range" class="form-range" min="20" max="100" step="10"
          v-model="charts.hist.maxHistSamples" v-on:input="updateHistoryWindow">
      </div>

    </div>

    
    
    
  </div>
</template>


<script>

import AQBarChart from './AQBarChart.vue';
import AQLineChart from './AQLineChart.vue';
import time from '../assets/js/time-func.js'

//const updateDelay = 1;

export default {

  name: 'AirQuality',

  components: {
    AQBarChart,
    AQLineChart
  },

  data: () => ({
    
    api: {
      lastTs: 0,
      liveData: {new: false, data: null},
      histData: {new: false, data: null}
    },

    charts: {
      sensors: [],
      selected: null,
      refreshHist: false,
      live: {
        barData: null,
        barDataMax: {},
        barDataMin: {}
      },
      hist: {
        maxHistSamples: 20,
        lineData: new Array(
          new Array(), 
          new Array()
        )
      },
    }
    
  }),

  mounted() {
    //setTimeout(this.update, updateDelay);
    this.update();
  },

  methods: {

    update: async function () {
      for(;;) {
        await this.fetchData();
        this.updateChartData();
      }
    },

    fetchData: async function () {
      let dataToFetch = "live";
      if (this.charts.refreshHist) {
        dataToFetch = "hist"; 
        this.charts.refreshHist = false;
      }

      if (dataToFetch === "live") {
        const newLiveData = await this.fetchLiveData();
        if (newLiveData) { 
          this.api.liveData = {new:true, data:newLiveData}; 
          this.api.lastTs = newLiveData[newLiveData.length - 1].ts;
        }
      }
      else if (dataToFetch === "hist") {
        const newHistData = await this.fetchSenHistData();
        if (newHistData) { 
          this.api.histData = {new:true, data:newHistData}; 
          this.api.lastTs = newHistData[newHistData.length - 1].ts;
        }
      }
    },

    fetchLiveData: async function() {
      const apiEndpoint = `${process.env.VUE_APP_API_HOST}/api/aq/live`;
      const apiArgs = `?from_ts=${this.api.lastTs}`;
      const apiUrl = apiEndpoint + apiArgs ;

      let apiData;
      try { apiData = await fetch(apiUrl).then((res) => res.json()); }
      catch (e) { return; }
      if (apiData.length === 0) { return; }

      return apiData;
    },

    fetchSenHistData: async function() {
      const apiEndpoint= `${process.env.VUE_APP_API_HOST}/api/aq/sen`
      let apiArgs = `?sensor=${this.charts.selected}`
      apiArgs += `&samples=${this.charts.hist.maxHistSamples}`;
      const apiUrl = apiEndpoint + apiArgs;

      let apiData;
      try { apiData = await fetch(apiUrl).then((res) => res.json()); } 
      catch (e) { return; }

      return apiData;
    },

    updateChartData: async function() {
      const liveData = this.api.liveData;
      const histData = this.api.histData;
      if (liveData.new === false && histData.new === false) { return; }

      this.charts.sensors = Object.keys(liveData.data[0].sensors);

      if (liveData.new) { 
        this.updateBarData(liveData.data);
        if (this.charts.selected !== null) {
          this.updateLineData(liveData.data);
        }
      }
      else if (histData.new) {
        this.updateLineData(histData.data);
      }

      if (this.charts.selected === null) { 
        this.charts.selected = this.charts.sensors[0]; 
      }

      this.api.liveData.new = false;
      this.api.histData.new = false;
    },

    updateBarData: function (data) {
      const sensorsData = data[data.length - 1].sensors;

      var newBarData = new Map();
      this.charts.sensors.forEach(sensor => {
        const val = sensorsData[sensor].val;
        
        // update normalisation scales
        if (!Object.prototype.hasOwnProperty
              .call(this.charts.live.barDataMax, sensor) ||
            this.charts.live.barDataMax[sensor] < val) { 
          this.charts.live.barDataMax[sensor] = val;
        }
        if (!Object.prototype.hasOwnProperty
              .call(this.charts.live.barDataMin, sensor) ||
            this.charts.live.barDataMin[sensor] > val) {
          this.charts.live.barDataMin[sensor] = val;
        }

        const scaledVal = val / this.charts.live.barDataMax[sensor] * 100;
        newBarData.set(sensor, {'normal': val, 'scaled': scaledVal})
      });

      this.charts.live.barData = newBarData;
    },

    updateLineData: function(data) {
      data.forEach(sample => {
        const unixTs = sample.ts;
        const ts = time.getTimestamp(new Date(unixTs))
        const val = sample.sensors[this.charts.selected].val;

        if (this.charts.hist.lineData[0].length >= 
            this.charts.hist.maxHistSamples) { 
          this.charts.hist.lineData[0].shift();
          this.charts.hist.lineData[1].shift();
        }
        this.charts.hist.lineData[0].push(ts);
        this.charts.hist.lineData[1].push(val);
      })
    },

    changeHistory: function(sensor) {
      if (sensor === this.charts.selected) { return; }

      this.charts.hist.lineData = new Array(
        new Array(), 
        new Array()
      );
      this.charts.selected = sensor;
      this.charts.refreshHist = true
    },

    updateHistoryWindow: function() {
      const selectedSamples = this.charts.hist.maxHistSamples;
      const currentSamples = this.charts.hist.lineData[0].length;

      const startIndex = currentSamples - selectedSamples;
      if (startIndex < 0) { return; }

      this.charts.hist.lineData[0].splice(0, startIndex);
      this.charts.hist.lineData[1].splice(0, startIndex);
    }
  },
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
#history-range {
  margin:0 auto;
  margin-top: 10px;
  max-width: 800px;
}
#history-range-input {
  width: 180px;
}
</style>