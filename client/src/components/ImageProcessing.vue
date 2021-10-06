<template>
  <div id="image-processing">

    <h4 style="text-align: center">Image Processing</h4>

    <div id="img-container" v-if="img !== null">
      <img id="img" :src="img"/>
    </div>

    <table id="info">
      <tr id="info-headers"> <th>Timestamp: </th> <th>Targets detected: </th> </tr>
      <tr> <td> {{timestamp}}</td> <td> {{targets}} </td> </tr>
    </table>

  </div>
</template>

<script>

import time from '../assets/js/time-func.js';

export default {
  name: 'ImageProcessing',
  data: () => ({ 
    img: null,
    timestamp: '',
    targets: ''
  }),
  mounted() {
    setInterval(this.fetchImage, 100);
  },
  methods: {

    fetchImage: async function() {

      const apiEndpoint = `${process.env.VUE_APP_API_HOST}/api/ip/live`;

      let apiData;
      try { apiData = await fetch(apiEndpoint).then((res) => res.json()); }
      catch (e) { return; }
      
      this.timestamp = time.getTimestamp(new Date(apiData.ts))
      this.img = "data:image/jpeg;base64, " + apiData.image;
      let targets_deteceted = "";
      apiData.detected.forEach(target => {
        this.targets_deteceted += " " + target
      });
      this.targets = targets_deteceted;

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
</style>