<template>
<div class="tile is-ancestor" style="margin: -5px">
  <div class="tile is-parent is-2 animated fadeInLeftBig" style="padding-right: 6px;">
    <article class="tile is-child box">
      <aside class="menu" style=" height: 690px">
        <p class="menu-label">
          General
        </p>
        <ul class="menu-list">
          <li><a>Dashboard</a></li>
          <li><a>Customers</a></li>
        </ul>
        <p class="menu-label">
          Administration
        </p>
        <ul class="menu-list">
          <li><a>Team Settings</a></li>
          <li>
            <a class="is-active">Manage Your Team</a>
            <ul>
              <li><a>Members</a></li>
              <li><a>Plugins</a></li>
              <li><a>Add a member</a></li>
            </ul>
          </li>
          <li><a>Invitations</a></li>
          <li><a>Cloud Storage Environment Settings</a></li>
          <li><a>Authentication</a></li>
        </ul>
        <p class="menu-label">
          Transactions
        </p>
        <ul class="menu-list">
          <li><a>Payments</a></li>
          <li><a>Transfers</a></li>
          <li><a>Balance</a></li>
        </ul>
      </aside>
    </article>
  </div>
  <div class="tile is-parent" style="padding-left: 6px">
    <article class="tile is-child box">
      555
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

