<template>
  <div>
    <editor ref="ace_editor" v-model="$store.query._session._tab._child_tab.query.sql"
              @init="editorInit" v-if="$store.vars.show_tab_sql"
              @keyup.120="execute_sql($store.query._session._tab._child_tab.query.sql, $store.query._session._tab.id)"
              lang="pgsql" theme="chrome" width="100%" height="100"
              title="F9 to Submit"></editor>
  </div>
</template>

<script>


export default {
  components: {
    editor: require('vue2-ace-editor')
  },
  methods: {
    editorInit() {
      require('brace/ext/language_tools') //language extension prerequsite...
      require('brace/mode/html')                
      require('brace/mode/javascript')    //language
      require('brace/mode/pgsql')    //language
      require('brace/mode/less')
      require('brace/theme/chrome')
      require('brace/snippets/javascript') //snippet
      self=this
      // Add F9 command
      this.$refs.ace_editor.editor.commands.addCommand({
        name: "Execute SQL",
        exec: function() {
          // self.execute_sql(self.$store.query._session._tab._child_tab.query.sql, self.$store.query._session._tab.id)
          // self.get_ace_selection()
          self.get_ace_cursor_query()
        },
        bindKey: {mac: "f9", win: "f9"}
      })

      // Add F4 command
      this.$refs.ace_editor.editor.commands.addCommand({
        name: "Get Object",
        exec: function() {
          // self.execute_sql(self.$store.query._session._tab._child_tab.query.sql, self.$store.query._session._tab.id)
          self.get_ace_selection(null, true)
          // self.log('hey')
        },
        bindKey: {mac: "f4", win: "f4"}
      })
    },
    },
  mounted() {
    this.$store.vars.ace_editor = this.$refs.ace_editor;
  }
};
</script>

<style lang="scss" scoped>
</style>
