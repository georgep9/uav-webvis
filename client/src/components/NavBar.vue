<template>
  <div id="navbar">
    <nav class="navbar navbar-dark bg-primary">
      <div class="container-fluid" id="title">
        <div class="navbar-brand">UAV Payload Data Visualization </div>
        <div id="nav-time">{{ currentTime }}</div>
      </div>
    </nav>
  </div>
</template>

<script>
import time from '../assets/js/time-func.js';

export default {

  name: 'NavBar',

  data() { 
    return { currentTime: "" } 
  },

  created() { 
    setInterval(this.getCurrentTime, 50); 
  },
  
  methods: {
    getCurrentTime: function() { 
      this.currentTime = time.getFullTime(new Date()) 
    }
  }

}
</script>

<style>
#nav-time {
  color: white;
}
</style>