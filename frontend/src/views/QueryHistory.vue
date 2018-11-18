<template>
  <div>
    <b-field horizontal label="Filter">
        <b-input expanded
          v-model="history_filter"
          @keyup.native.esc="history_filter = ''"
          @keyup.native.enter="get_queries(history_filter, null)"
          @input="dbc_get_query({get_queries: get_queries, history_filter: history_filter})"
          placeholder="Filter History..." type="search">
        </b-input>
        <p class="control">
          <b-tooltip label="Search" position="is-bottom" type="is-dark">
            <a class="button is-outlined is-info" @click="get_queries(history_filter, null)">
              <b-icon pack="fa" icon="search" size="is-small"></b-icon>
            </a>
          </b-tooltip>
        </p>
    </b-field>
    

    <div class="history_div">
      <select multiple v-model="history_selected"
              class="schema_select item_select" style="font-size: 0.7em; width:100%; height: 150px">
        <option v-for="object in filtered_history()" class="codelike"
          @click="history_selected_sql = $store.queue.rcv_queries.filter(rec => rec.task_id == object.split(' | ')[1])[0].sql_text"
          @dblclick="execute_sql(history_selected_sql = $store.queue.rcv_queries.filter(rec => rec.task_id == object.split(' | ')[1])[0].sql_text)"
          v-bind:key="object"
          :value="object"
        >{{object}}</option>
      </select>
    </div>

    <div>
      <textarea class="textarea codelike" name="history_sql" id=""
        :style="{'height': $store.style.schema_object_height}"
        style="width: 100%; font-size: 0.7em" v-model="history_selected_sql"></textarea>
    </div>
  </div>
</template>

<script>
import _ from "lodash";
export default {
  methods: {
    conv_date_from_UTC(utc_dt) {
      utc_dt.setMinutes(utc_dt.getMinutes() - utc_dt.getTimezoneOffset());
      return utc_dt;
    },
    dbc_get_query: _.debounce(params => {
      // https://alligator.io/vuejs/lodash-throttle-debounce/
      params.get_queries(params.history_filter, null);
    }, 500),
    filtered_history() {
      try {
        return this.$store.queue.rcv_queries
          .filter(rec => {
            return this.history_filter
              ? rec.sql_text
                  .toString()
                  .toLowerCase()
                  .indexOf(this.history_filter.toLowerCase()) >= 0
              : rec;
          })
          .map(
            rec =>
              `${this.conv_date_from_UTC(new Date(rec.exec_date * 1000))
                .toISOString()
                .slice(0, 16)} | ${rec.task_id}`
          );
      } catch (error) {
        this.log(error);
        return [];
      }
    }
  },
  data() {
    return {
      loading: false,
      history_selected: [],
      history_selected_sql: null,
      history_filter: ""
    };
  },
  mounted() {
    this.get_queries(this.history_filter, null);
  }
};
</script>

<style lang="scss" scoped>
</style>
