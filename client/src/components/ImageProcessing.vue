<template>
  <div id="image-processing">

    <h4 style="text-align: center">Image Processing</h4>

    <div id="img-container">
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
    img: "https://via.placeholder.com/1024x768/eee?text=4:3",
    index: 0,
    timestamp: '',
    targets: ''
  }),
  mounted() {
    setInterval(this.fetchImage, 1000);
  },
  methods: {

    fetchImage: function() {

      switch (this.index) {

        case 0:
          this.img = "https://static.scientificamerican.com/sciam/cache/file/7A715AD8-449D-4B5A-ABA2C5D92D9B5A21_source.png"
          this.index = 1;
          this.targets = 'Bag';
          break;
        case 1: 
          this.img = "https://4.img-dpreview.com/files/p/E~TS590x0~articles/3925134721/0266554465.jpeg";
          this.index = 2;
          this.targets = 'Marker';
          break;
        case 2:
          this.img = "https://c4.wallpaperflare.com/wallpaper/866/880/9/birds-owl-bird-wildlife-hd-wallpaper-preview.jpg";
          this.index = 3;
          this.targets = 'Person';
          break;
        case 3:
          this.img ="https://see.news/wp-content/uploads/2020/12/UK_wildbirds-01-robin.jpg"
          this.index = 0;
          this.targets = 'Bag, Marker';
          break;
        default:
          break;        
      }

      this.timestamp = time.getTimestamp(new Date());

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