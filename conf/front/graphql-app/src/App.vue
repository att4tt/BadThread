<template>
  <div id="app">
    <HeaderDev />
    <MenuTop />
    <main>
    </main>
  </div>
</template>

<script>
import HeaderDev from './components/HeaderDev.vue'
import MenuTop from './components/Menu.vue'

export default {
  name: 'App',
  components: {
    HeaderDev,
    MenuTop
  }
}
</script>