<template>
  <div id="airquality">

    <AQBarChart/>
    <AQLineChart/>
    
  </div>
</template>

<script>

import AQBarChart from './AQBarChart.vue';
import AQLineChart from './AQLineChart.vue'

export default {

  name: 'AirQuality',

  components: {
    AQBarChart,
    AQLineChart
  }

}

</script>

<style>
</style>