<template>
  <div id="image-processing" v-if="img !== null">

    <h4 style="text-align: center">Image Processing</h4>

    <div id="img-container">
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

  </div>
</template>

<script>

import time from '../assets/js/time-func.js';

export default {
  name: 'ImageProcessing',
  data: () => ({ 
    img: null,
    timestamp: '',
    targets: '',
    vocalise: false
  }),
  mounted() {
    setInterval(this.fetchImage, 500);
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

      apiData.detected.forEach(target => { targets_detected += target + " "; });

      if (this.targets !== targets_detected){
        this.targets = targets_detected;
        this.voiceTargets();
      }

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
  background-color: rgba(44,62,80,1);;
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