<template>
  <div id="app">

    <NavBar/>

  </div>
</template>

<script>

import NavBar from './components/NavBar.vue';

export default {
  name: 'App',
  components: {
    NavBar
  }
}

</script>

<style>
@import './assets/css/bootstrap.min.css';
#nav-time {
  color: white;
}
</style>
