<template>
  <div id="app">

    <NavBar/>

    <AirQuality/>

  </div>
</template>

<script>

import NavBar from './components/NavBar.vue';
import AirQuality from './components/AirQuality.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    AirQuality
  }
}

</script>

<style>
@import './assets/css/bootstrap.min.css';
</style>
