<template>
  <div id="app">
    <AppLayout>
    <router-view></router-view>
  </AppLayout>
  </div>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'App',
  components: {
    AppLayout
  }

}
</script>

