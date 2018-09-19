<template>
  <div>
    <HotTable root= "hot" ref="hot" :settings="$store.hotSettings"></HotTable>
  </div>
</template>

<script>
import "handsontable/dist/handsontable.full.css";
import HotTable from "@handsontable/vue";
export default {
  components: {
    HotTable: HotTable
  },
  methods: {},
  mounted() {
    this.$store.vars.hot = this.$refs.hot;
  }
};
</script>

<style lang="scss" scoped>
</style>
