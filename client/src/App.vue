<template>
  <div id="app">

    <NavBar id="nav-bar-comp"/>
    <AirQuality id="air-quality-comp"/>
    <!--ImageProcessing id="image-processing-comp"/>-->

  </div>
</template>

<script>

import NavBar from './components/NavBar.vue';
import AirQuality from './components/AirQuality.vue';
//import ImageProcessing from './components/ImageProcessing.vue';

export default {
  name: 'App',
  components: {
    NavBar,
    AirQuality,
    //ImageProcessing
  }
}

</script>

<style>
@import './assets/css/bootstrap.min.css';
#air-quality-comp {
  width: 50%;
  min-width: 375px;
  float: left;
  padding: 20px;
}
#image-processing-comp {
  width: 50%;
  min-width: 375px;
  float: left;
  padding: 20px;
}
</style>
