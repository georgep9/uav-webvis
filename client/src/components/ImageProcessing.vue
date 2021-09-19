<template>
  <div id="image-processing">

    <h4 style="text-align: center">Image Processing</h4>
    <img id="img" :src="img"/>
    <table id="info">
      <tr id="info-headers">
        <th>Timestamp: </th>
        <th>Targets detected: </th>
      </tr>
      <tr>
        <td>time</td>
        <td>targets</td>
      </tr>
    </table>
    
    
  </div>
</template>

<script>
export default {
  name: 'ImageProcessing',
  data: () => ({ 
    img: "https://via.placeholder.com/1024x768/eee?text=4:3",
    index: 0
  }),
  mounted() {
    setInterval(this.fetchImage, 250);
  },
  methods: {

    fetchImage: function() {

      switch (this.index) {

        case 0:
          this.img = "https://static.scientificamerican.com/sciam/cache/file/7A715AD8-449D-4B5A-ABA2C5D92D9B5A21_source.png"
          this.index = 1;
          break;
        case 1: 
          this.img = "https://4.img-dpreview.com/files/p/E~TS590x0~articles/3925134721/0266554465.jpeg";
          this.index = 2;
          break;
        case 2:
          this.img = "https://cdn.download.ams.birds.cornell.edu/api/v1/asset/202984001/1200";
          this.index = 3;
          break;
        case 3:
          this.img ="https://see.news/wp-content/uploads/2020/12/UK_wildbirds-01-robin.jpg"
          this.index = 0;
          break;
        default:
            break;
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
  width: 720px;
  height: 480px;
  border: 3px solid rgba(44,62,80,1);
}

#info {
  margin-left: auto;
  margin-right: auto;
  width: 720px;
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
</style>