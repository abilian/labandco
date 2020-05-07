<template>
  <footer class="main-footer">
    <div class="float-right hidden-xs"><b>Version</b> {{ version }}</div>

    <strong>
      Copyright &copy; 2014-2020
      <a href="http://www.sorbonne-universite.fr/">Sorbonne Université</a>
      and contributors.
    </strong>
    <br />
    Licensed under the Apache License. Powered by
    <a href="https://www.abilian.com/">Abilian</a> and co-designed by
    <a href="https://willstrategy.com/">Will Strategy</a>.
    <a href="https://github.com/abilian/labandco/">Source code</a>.
  </footer>
</template>

<script>
export default {
  data() {
    return {
      version: window.CTX.version,
    };
  },
};
</script>
