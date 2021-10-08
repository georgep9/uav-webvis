<template>
  <div id="image-processing" v-if="img !== null">

    <h4 style="text-align: center">Image Processing</h4>

    <div id="live-img">
      <img id="img" :src="img"/>
    </div>

    <table id="info">
      <tr id="info-headers"> <th>Timestamp: </th> <th>Targets detected: </th> </tr>
      <tr> <td> {{timestamp}}</td> <td> {{targets}} </td> </tr>
    </table>

    <div id="vocalise-switch-container">
      <div class="form-check form-switch">
        <input class="form-check-input" type="checkbox" id="vocalise-switch" v-model="vocalise">
        <label class="form-check-label" for="vocalise-switch">Vocalise targets</label>
      </div>
    </div>

    <div id="detected-history">
      <div id="inline-images" style="display: inline;" v-for="timestamp in detectedTimestamps" :key="timestamp">
        <div class="history-item">
          <img class="history-img" :src="'data:image/jpeg;base64, ' + detectedImgHist[timestamp].img"/>
          <p style="text-align: center; margin: 0;">{{ time.getTimestamp(new Date(timestamp)) }}</p>
        </div>
      </div>
    </div>

    

  </div>
</template>

<script>

import time from '../assets/js/time-func.js';

const histLoadRate = 3;

export default {
  name: 'ImageProcessing',
  data: () => ({ 
    img: null,
    timestamp: '',
    targets: '',
    vocalise: false,
    detectedImgHist: {},
    detectedTimestamps: [],
    histLoaded: false,
    time: time
  }),
  mounted() {
    setInterval(this.fetchImage, 500);
    setInterval(this.fetchHist, 1000);
  },
  methods: {

    fetchImage: async function() {
      const apiEndpoint = `${process.env.VUE_APP_API_HOST}/api/ip/live`;

      let apiData;
      try { apiData = await fetch(apiEndpoint).then((res) => res.json()); }
      catch (e) { return; }
      if (apiData === "") { return; }

      this.timestamp = time.getTimestamp(new Date(apiData.ts))
      this.img = "data:image/jpeg;base64, " + apiData.image;

      let targets_detected = "";
      apiData.detected.forEach(target => { targets_detected += target + ", "; });
      
      if (this.targets !== targets_detected){
        this.targets = targets_detected;
        this.voiceTargets();
      }

      if (apiData.detected.length !== '' &&
          ((this.detectedTimestamps.length === 0 ||
            this.detectedTimestamps[0] !== apiData.ts))){
        console.log("here")
        this.detectedImgHist[apiData.ts] = {
          img: apiData.image,
          detected: apiData.detected
        }
        this.detectedTimestamps.unshift(apiData.ts)
      }

    },

    fetchHist: async function () {
      if (this.histLoaded || this.detectedTimestamps.length === 0) { return; }

      console.log(this.histLoaded)

      const oldestTs = this.detectedTimestamps.at(-1)
      const apiArgs = `?beforeTs=${oldestTs}&nFrames=${histLoadRate}`;
      const apiEndpoint = `${process.env.VUE_APP_API_HOST}/api/ip/hist${apiArgs}`;

      let apiData;
      try { apiData = await fetch(apiEndpoint).then((res) => res.json()); }
      catch (e) { return; }
      if (apiData.length === 0) {
        this.histLoaded = true;
        return; 
      }

      console.log("oldest")
      console.log(oldestTs)
      apiData.forEach(sample => {
        console.log(sample.timestamp)
        this.detectedTimestamps.push(sample.timestamp);
        this.detectedImgHist[sample.timestamp] = {
          img: sample.image,
          detected: sample.detected
        }
      })

    },

    voiceTargets() {
      if (this.vocalise){
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(new SpeechSynthesisUtterance(this.targets));
      }
    }
  },

  watch: { vocalise: function() { this.voiceTargets() } }

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
  border: 1px solid rgba(44,62,80,1);
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
  margin-top: 20px;
}

.history-item {
  display: inline-block;
}

.history-img {
  width: 100%;
  height: 100%;
  max-width: 106px;
  max-height: 80px;
}

#info {
  margin-left: auto;
  margin-right: auto;
  width: 100%;
  max-width: 720px;
  border: 1px solid rgba(44,62,80,1);
}

#info-headers {
  color: white;
  background-color: rgba(44,62,80,1);
}

th, td {
  padding-left: 10px;
  padding-right: 10px;
}

#vocalise-switch-container {
  margin:0 auto;
  margin-top: 10px;
  max-width: 720px;
}
</style>