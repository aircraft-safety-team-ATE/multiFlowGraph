<template>
  <div class="main-box">
    <MSFG />
  </div>
</template>

<script>
import MSFG from './MSFG.vue'

export default {
  components: {
    MSFG: MSFG
  },
  data () {
    return {

    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.main-box{
  width: 100%;
  height: 100%
}
</style>
