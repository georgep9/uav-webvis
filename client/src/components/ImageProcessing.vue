<template>
  <div id="image-processing" v-if="img !== null">

    <h4 style="text-align: center">Image Processing</h4>

    <div id="live-img">
      <img id="img" :src="img"/>
    </div>

    <table id="info">
      <tr id="info-headers"> <th>Timestamp</th> <th>Targets detected</th> </tr>
      <tr> <td> {{time.getTimestamp(new Date(selectedTimestamp))}}</td> <td> {{targets}} </td> </tr>
    </table>

    <div id="switches-container">
      <div class="form-check form-switch" id="vocalise-switch-container">
        <input class="form-check-input" type="checkbox" id="vocalise-switch" v-model="vocalise">
        <label class="form-check-label" for="vocalise-switch">Vocalise targets</label>
      </div>
      <div class="form-check form-switch" id="live-switch-container">
        <input class="form-check-input" type="checkbox" id="live-switch" v-model="live">
        <label class="form-check-label" for="live-switch">Live</label>
      </div>
    </div>

    <p style="width:100%; display: block; float: left; padding-top: 10px"><b> Detection History</b></p>
    <div id="detected-history" ref="histDiv">
      <div id="inline-images" style="display: inline;" v-for="timestamp in detectedTimestamps" :key="timestamp">
        <div v-bind:class="[timestamp === selectedTimestamp ? 'selected-item' : 'history-item']" 
          v-on:click="selectHistItem(timestamp)">
          <img class="history-img" :src="'data:image/jpeg;base64, ' + detectedImgHist[timestamp].img"/>
          <p style="text-align: center; margin: 0;">{{ time.getTimestamp(new Date(timestamp)) }}</p>
        </div>
      </div>
    </div>

    

  </div>
</template>

<script>

import time from '../assets/js/time-func.js';

const histLoadRate = 10;
const histLimit = 100;

export default {
  name: 'ImageProcessing',
  data: () => ({ 
    img: null,
    timestamp: null,
    targets: '',
    vocalise: true,
    live: true,

    detectedImgHist: {},
    detectedTimestamps: [],
    histLoaded: false,
    selectedTimestamp: null,
    fetchingHist: false,

    time: time
  }),
  mounted() {
    setInterval(this.fetchImage, 500);
    setInterval(this.fetchHist, 1000);
  },
  methods: {

    fetchImage: async function() {
      const apiEndpoint = `${process.env.VUE_APP_API_HOST}/api/ip/live?fromTs=${this.timestamp}`;

      let apiData;
      try { apiData = await fetch(apiEndpoint).then((res) => res.json()); }
      catch (e) { return; }
      if (apiData === "") { return; }

      if (this.live) {
        this.timestamp = apiData.ts;
        this.img = "data:image/jpeg;base64, " + apiData.image;

        let targets_detected = "";
        apiData.detected.forEach(target => { targets_detected += target + ", "; });
        
        if (this.targets !== targets_detected){
          this.targets = targets_detected;
          this.voiceTargets();
        }

        this.selectedTimestamp = apiData.ts;
      }

      if (apiData.detected.length !== 0 &&
          ((this.detectedTimestamps.length === 0 ||
            this.detectedTimestamps[0] !== apiData.ts))){
        
        this.detectedImgHist[apiData.ts] = {
          img: apiData.image,
          detected: apiData.detected
        }
        this.detectedTimestamps.unshift(apiData.ts)
      }

    },

    fetchHist: async function () {
      if (this.histLoaded || 
          (this.detectedTimestamps.length === 0 &&
           this.timestamp === null) ||
          this.fetching ||
          this.detectedTimestamps.length > histLimit) 
          { return; }
      else { this.fetching = true; }

      let oldestTs = this.timestamp;
      if (this.detectedTimestamps.length > 0) {
        oldestTs = this.detectedTimestamps.at(-1);
      }
      console.log(oldestTs)
      const apiArgs = `?beforeTs=${oldestTs}&nFrames=${histLoadRate}`;
      const apiEndpoint = `${process.env.VUE_APP_API_HOST}/api/ip/hist${apiArgs}`;

      let apiData;
      try { apiData = await fetch(apiEndpoint).then((res) => res.json()); }
      catch (e) { return; }
      if (apiData.length === 0) {
        this.histLoaded = true;
        return; 
      }
      apiData.forEach(sample => {
        this.detectedTimestamps.push(sample.timestamp);
        this.detectedImgHist[sample.timestamp] = {
          img: sample.image,
          detected: sample.detected
        }
      });

      this.fetching = false;
    },

    voiceTargets() {
      if (this.vocalise){
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(new SpeechSynthesisUtterance(this.targets));
      }
    },

    selectHistItem(timestamp) {
      if (timestamp === this.selectedTimestamp) { return; }

      this.live = false;
      this.selectedTimestamp = timestamp;

      this.img = "data:image/jpeg;base64, " + this.detectedImgHist[timestamp].img
      this.targets = "";
      this.detectedImgHist[timestamp].detected.forEach(target => { this.targets += target + ", "; });

      this.voiceTargets();
    }
  },

  watch: { 
    vocalise: function() { this.voiceTargets() },
    live: function() {
      if (this.live) { 
        this.$refs.histDiv.scrollLeft = this.$refs.histDiv.scrollWidth;
      }
    }
  }
  

}
</script>

<style>

#img {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  max-width: 720px;
  height: 100%;
  max-height: 480px;
  border: 2px solid rgba(44,62,80,1);
  background-color: rgba(44,62,80,1);
}

#detected-history {
  display: block;
  margin-left: auto;
  margin-right: auto;
  overflow: auto;
  overflow-y: hidden;
  white-space: nowrap;
  width: 100%;
  max-width: 720px;
  direction: rtl;
  padding-bottom: 5px;
}

.history-item {
  display: inline-block;
  margin-left: 20px;
  opacity: 0.6;
}

.selected-item {
  display: inline-block;
  border: 2px solid rgba(44,62,80,1);
  margin-left: 20px;
}

.history-img {
  display: block;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  height: 100%;
  max-width: 80px;
}

#info {
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  max-width: 720px;
  border: 2px solid rgba(44,62,80,1);
}

#info-headers {
  color: white;
  background-color: rgba(44,62,80,1);
}

th, td {
  padding-left: 10px;
  padding-right: 10px;
}

#switches-container {
  margin:0 auto;
  margin-top: 10px;
  max-width: 720px;
  padding-bottom: 10px;
}

#vocalise-switch-container {
  width:50%;
  float:left;
}

#live-switch-container {
  float:right;
}
</style>