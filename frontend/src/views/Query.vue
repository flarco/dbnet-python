<template>
<div class="tile is-ancestor" style="margin: -5px">
  <div class="tile is-parent is-4" style="padding-right: 6px">
    <article class="tile is-child box">
      <textarea name="" id="" cols="60" rows="52">
        Select *
        from hello
      </textarea>
    </article>
  </div>
  <div class="tile is-parent" style="padding-left: 6px">
    <article class="tile is-child box">
      555dd
    </article>
  </div>
</div>
</template>

<script>
import { codemirror, CodeMirror } from "vue-codemirror";
import "codemirror/lib/codemirror.css";
require("codemirror/addon/scroll/annotatescrollbar");
require("codemirror/addon/search/matchesonscrollbar");
require("codemirror/addon/search/searchcursor");
require("codemirror/addon/search/match-highlighter");

export default {
  name: "Home",
  components: {
    codemirror: codemirror
  },
  data() {
    return {
      msg: "Vue.js starter with full-featured Webpack and Buefy"
    };
  }
};
</script>

<style lang="scss" scoped>
.additional-bar {
  padding: 15px;
}

.gh-btn {
  background-color: #eee;
  background-repeat: no-repeat;
  border: 1px solid #d5d5d5;
  border-radius: 4px;
  color: #333;
  text-decoration: none;
  text-shadow: 0 1px 0 #fff;
  white-space: nowrap;
  cursor: pointer;
}
</style>

